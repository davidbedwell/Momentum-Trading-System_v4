"""Bounded four-family feed -> native decisions -> shared bank + funded shadows.

This runner accepts governed dependencies; it creates none. Native contract
failure happens before market I/O. Accounting conventions remain research-only.
"""
from .first_year_manifest import FAMILIES, audit_contracts
from .chronological_manager_replay import run
from .native_four_family_orchestrator import produce
from .archived_genomes import ga7_bars
from .funded_shadow import FundedShadow


def bounded_replay(*, feed, dates, controls, requirements, market_loader,
                   settings_loader, owners, stops_by_owner, ga7_columns,
                   settlement_sessions=1, min_samples=5, risk_provider=None):
    dates = tuple(dates)
    if not 2 <= len(dates) <= 64:
        raise ValueError('bounded smoke requires 2..64 sessions')
    indices = [feed.calendar.sessions.index(d) for d in dates]
    if indices != list(range(indices[0], indices[0]+len(dates))):
        raise ValueError('smoke sessions must be contiguous')
    for date in dates:
        feed.calendar.permit(date)
        blockers = audit_contracts(feed.contracts, decision_date=date, scenario_hash=feed.scenario_hash)
        if blockers:
            raise ValueError('blocked native input contracts: '+'; '.join(blockers))
    if set(requirements) != set(FAMILIES):
        raise ValueError('all four family requirements required')
    shadow = FundedShadow(owners, sessions=dates, settlement_sessions=settlement_sessions)
    current = {}
    calls = {f: 0 for f in FAMILIES}

    def evaluate(date, session, bars, defense, states):
        settings = current['settings']
        # Provider owns compiler/lineage restoration. All requested specs must
        # be explicit; an empty family may not masquerade as a four-family run.
        proposals = []
        for family, spec_key in (('GA4','ga4_specs'), ('HORIZONS','horizons_specs'),
                                 ('GA6','ga6_specs'), ('GA7','ga7_specs')):
            if not settings.get(spec_key):
                raise ValueError('missing native family specs: '+family)
            contract = feed.contracts[family]
            kw = {spec_key: settings[spec_key]}
            if family == 'GA4':
                kw['ga4_compiler'] = settings['ga4_compiler']
            elif family == 'HORIZONS':
                kw['horizons_panel'] = settings['horizons_panel']
            elif family == 'GA6':
                kw['ga6_rows'] = {r['ticker']: r for r in current['panels'][family].to_dict('records')}
            else:
                panel = current['panels'][family]
                kw['ga7_bars'] = ga7_bars(panel, decision_date=date,
                    eligibility=dict(zip(panel.ticker, map(bool, panel.eligible))), columns=ga7_columns)
            native = produce(date, trained_through=contract['trained_through'],
                source_hash=contract['source_hash'], snapshot_hash=settings['snapshot_hash'],
                session=session, held_by_owner=states, defensive=defense, **kw)
            allowed = current['panels'][family].set_index('ticker').eligible.to_dict()
            if any(p.ticker not in allowed for p in native):
                raise ValueError('native proposal outside declared universe')
            proposals.extend(p for p in native if p.action not in ('ENTER','ADD') or
                             (not defense and allowed[p.ticker]))
            calls[family] += 1
        return proposals

    def actual(date, session, bars, holdings, actual_owners, defense, fills):
        control = current['control']
        current['panels'] = feed.at_close(date, decision_at=control['decision_at'],
            gates=control['gates'], requirements=requirements)
        current['settings'] = settings_loader(date, current['panels'])
        if any(getattr(s.get('exit_producer'), 'experimental_exit_version', None)
               for s in current['settings'].get('ga4_specs', ())):
            raise ValueError('experimental GA4 exit cannot pass authentic four-family runner')
        states = {}
        for ticker, owner in actual_owners.items():
            p = fills.positions[ticker]
            states.setdefault(owner, {})[ticker] = dict(entry=p.entry, peak=p.peak,
                shares=p.shares, entry_session=p.entry_session, initial_stop=p.stop,
                weight=holdings[ticker], owner=owner)
        return evaluate(date, session, bars, defense, states)

    def shadow_native(date, session, bars, defense, book):
        result = evaluate(date, session, bars, defense, book.native_states(bars))
        # GA4 remains outside funded books until its native exit is approved.
        return [p for p in result if (p.family, p.chromosome_id) in book.cash]

    def days():
        for date in dates:
            control = controls(date)
            current['control'] = control
            if type(control['defense']) is not bool:
                raise ValueError('explicit dated defense observation required')
            yield date, market_loader(as_of=date), actual, [], control['defense']

    result = run(days(), min_samples=min_samples, stops_by_owner=stops_by_owner,
        shadow_book=shadow, shadow_native=shadow_native,
        settlement_sessions=settlement_sessions, max_sessions=len(dates), risk_provider=risk_provider)
    result.update(native_calls=calls, shadow_fills=list(shadow.fills),
        shadow_rejections=list(shadow.rejections), shadow_nav=list(shadow.nav_history),
        launch_ready=False, scope='BOUNDED_RESEARCH_ONLY',
        limitations='caller input provenance is not certification; GA4 funded shadows disabled; native ledger and aggregate risk parity remain required')
    return result
