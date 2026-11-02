"""Bounded functionality baseline; no fitted utility, fabricated features or I/O.

The caller supplies dated native niche matches (including native center distances),
feature eligibility and native decisions. GA4 is research-only and never traded.
"""
from dataclasses import dataclass, replace
from datetime import date as iso_date
from math import isfinite

from engines.portfolio_replay.kernel import Replay, Signal
from .hierarchical_search import RoutedCandidate, tier
from .native_signal_contract import normalize_proposals
from .position_fill_book import FillBook
from .capital_competition import Opportunity, compare
from .progressive_scaling import allowed_target
from .native_shadow_trade_book import ShadowBook
from .causal_calibration import Calibrator, TradeOutcome
from .shadow_learning_interface import ShadowLearningView
from .evolved_selection_policy import score as selection_score
from .causal_market_state import state_from_closes
from .genome_identity import GenomeIdentityRegistry


@dataclass(frozen=True)
class NicheObservation:
    as_of: str
    trained_through: str
    source: str
    # Only matches returned by the native classifier; never inferred here.
    matches: tuple  # (niche identity, native center distance)
    native_controller: str | None = None

    def controlling(self, date):
        if self.as_of != date or not self.source:
            raise ValueError('dated native niche observation required')
        if iso_date.fromisoformat(self.trained_through) >= iso_date.fromisoformat(date):
            raise ValueError('niche model must precede decision')
        names = [name for name, _ in self.matches]
        if len(names) != len(set(names)):
            raise ValueError('duplicate niche match')
        if any(not name or not isfinite(distance) or distance < 0
               for name, distance in self.matches):
            raise ValueError('invalid native center distance')
        if self.native_controller is not None:
            if self.native_controller not in names:
                raise ValueError('native controller must be a qualifying niche')
            return self.native_controller
        return min(self.matches, key=lambda x: (x[1], x[0]))[0] if self.matches else None


@dataclass(frozen=True)
class Candidate:
    chromosome_id: str
    family: str
    niche: str | None
    stop: float
    # Caller supplies dated gap loss estimate; missing information assumes total loss.
    gap_risk: float = 1.0


def run_slice(days, candidates, *, classify, eligible, native, cash=100000.,
              max_sessions=64, max_stocks=32, selector=None, defense_at_close=None,
              manager_override=None, opportunity_at_close=None, conditional_ev=None,
              shadow_horizon=0, native_shadow=False, selection_genes=None,
              native_genomes=None, genome_registry=None, require_genome_identity=False, session_hook=None, retain_audit=True, funded_entry_scale=None, candidate_provider=None,
              fees=.001, spread=0., slippage=0., impact=0., mdd_limit=.20,
              allocation_priority=None, scaling_evidence=None):
    """Stream dated bars through native callbacks and a single funded bank.

    classify(ticker, date) -> NicheObservation; eligible(candidate,ticker,date)
    -> explicit bool; native(candidate,ticker,date,held) -> NativeProposal/None.
    Callbacks receive only today's cutoff and filled incumbent state. They must
    query sources at that cutoff; this API cannot certify caller provenance.
    conditional_ev must supply comparable marginal net return per dollar, after
    all execution costs and risk/reliability adjustments, using the same horizon.
    Unavailable estimates abstain. Niche tiers apply within each ticker, then
    all funded increases compete globally. No raw family score is used as EV.
    SGOV is unavailable on this seam: explicit zero-yield settled-cash fallback.
    allocation_priority(c,t,date,controlling,matches,net_ev) optionally orders
    funded increases only; finite signed priorities never change EV admission.
    scaling_evidence(c,t,date,held,realized,nav_history) optionally supplies causal
    ScaleEvidence for native ADDs; the kernel validates evidence and risk.
    Defaults retain the 10% cap and EV queue ordering.
    """
    if selector is not None:
        raise ValueError('unpriced selector disabled; provide comparable conditional_ev')
    candidates = tuple(sorted(candidates, key=lambda c: (c.family, c.chromosome_id)))
    keys = [(c.family, c.chromosome_id) for c in candidates]
    if not 1 <= len(candidates) <= 20000 or len(keys) != len(set(keys)):
        raise ValueError('require 1..20000 unique candidates')
    if any(c.family not in ('GA6', 'GA7', 'HORIZONS') or
           not c.chromosome_id or not 0 < c.stop <= .02 or
           not isfinite(c.gap_risk) or not 0 <= c.gap_risk <= 1 for c in candidates):
        raise ValueError('trading candidate invalid; GA4 is research-only')
    if type(max_sessions) is not int or not 2 <= max_sessions <= 10000:
        raise ValueError('require 2..10000 sessions')
    if type(max_stocks) is not int or not 1 <= max_stocks <= 10000:
        raise ValueError('require 1..10000 stocks')
    if not isfinite(cash) or cash <= 0:
        raise ValueError('positive funded cash required')
    if require_genome_identity and (native_genomes is None or genome_registry is None):
        raise ValueError('production requires registered native genomes')
    if native_genomes is not None:
        if set(native_genomes) != set(keys):
            raise ValueError('complete family-qualified native genomes required')
        registry = genome_registry if genome_registry is not None else GenomeIdentityRegistry()
        for family, chromosome_id in keys:
            if require_genome_identity:
                registry.require(family, chromosome_id, native_genomes[(family, chromosome_id)])
            else:
                registry.register(family, chromosome_id, native_genomes[(family, chromosome_id)])
    elif genome_registry is not None:
        raise ValueError('native genomes required for registry verification')
    genome_hashes = {key: registry.by_id[key] for key in keys} if native_genomes is not None else {}
    bank = Replay(cash=cash, settlement_sessions=1, fees=fees, spread=spread,
                  slippage=slippage, impact=impact, mdd_limit=mdd_limit)
    book = FillBook()
    by_owner = dict(zip(keys, candidates))
    decisions = []
    shadow_ledger = []
    shadow_open = []
    shadow_book = ShadowBook(genome_hashes=genome_hashes) if native_shadow else None
    shadow_calibrator = Calibrator(min_samples=5) if native_shadow else None
    shadow_outcomes = []
    shadow_learning = ShadowLearningView() if native_shadow else None
    learning_snapshots = []
    close_history = {}
    if type(shadow_horizon) is not int or not 0 <= shadow_horizon <= 20:
        raise ValueError('shadow horizon must be 0..20 sessions')
    pending = {}
    last = None
    for session, (date, bars) in enumerate(days):
        iso_date.fromisoformat(date)
        if session >= max_sessions or (last is not None and date <= last):
            raise ValueError('bounded chronological sessions required')
        if not bars or len(bars) > max_stocks or set(book.positions) - set(bars):
            raise ValueError('bounded complete market bars required')
        last = date
        for t,bar in bars.items():
            close_history.setdefault(t,[]).append(bar.close)
        if native_shadow:
            matured = shadow_book.open_session(session, bars)
            for outcome in matured:
                shadow_calibrator.record(outcome)
                shadow_learning.ingest(outcome)
                shadow_outcomes.append(outcome)
        if native_shadow:
            snapshot = shadow_learning.snapshot(session) if session_hook is None else {}
            snapshot['genome_hashes'] = genome_hashes
            if retain_audit: learning_snapshots.append(snapshot)
        if session_hook is not None:
            session_hook(session, date, matured if native_shadow else [])
        if candidate_provider is not None:
            updated = tuple(sorted(candidate_provider(), key=lambda c: (c.family,c.chromosome_id)))
            if updated != candidates:
                updated_keys = [(c.family,c.chromosome_id) for c in updated]
                if len(updated_keys) != len(set(updated_keys)) or not set(keys) <= set(updated_keys):
                    raise ValueError('evolution must preserve incumbent and shadow identities')
                for key in updated_keys:
                    registry.require(*key,native_genomes[key])
                    genome_hashes[key] = registry.by_id[key]
                candidates=updated;keys=updated_keys;by_owner=dict(zip(keys,candidates))
        if shadow_horizon:
            for trial in shadow_open:
                if trial['ticker'] not in bars:
                    raise ValueError('shadow ticker missing from bars')
                if session == trial['entry_session']:
                    trial['entry_price'] = bars[trial['ticker']].open
                if session == trial['entry_session'] + shadow_horizon:
                    trial['exit_price'] = bars[trial['ticker']].close
                    trial['exit_date'] = date
                    trial['gross_return'] = trial['exit_price'] / trial['entry_price'] - 1
                    trial['net_return_estimate'] = trial['gross_return'] - bank.round_trip_cost
                    trial['status'] = 'MATURED_FIXED_HORIZON'
                    shadow_ledger.append(trial)
            shadow_open = [t for t in shadow_open if t['status'] == 'OPEN']
        before = len(bank.ledger)
        for ticker, p in book.positions.items():
            p.shares *= bars[ticker].split
            p.entry /= bars[ticker].split
            p.basis /= bars[ticker].split
            p.peak /= bars[ticker].split
        bank.day(date, bars)
        for fill in bank.ledger[before:]:
            _, ticker, side, *_ = fill
            owner = pending[ticker] if side == 'BUY' else book.positions[ticker].owner
            book.apply(fill, owner, stop=by_owner[owner].stop, session=session)
        if set(book.positions) != set(bank.shares) or any(
                abs(p.shares-bank.shares[t]) > 1e-7 for t, p in book.positions.items()):
            raise ValueError(f'fill attribution mismatch at {date}: book_only={set(book.positions)-set(bank.shares)}, bank_only={set(bank.shares)-set(book.positions)}')
        nav = bank.nav[-1][1]
        if nav <= 0 or bank.cash < -1e-7:
            raise ValueError('invalid funded bank')
        defensive = False if defense_at_close is None else defense_at_close(date)
        if type(defensive) is not bool:
            raise ValueError('defense controller must return explicit boolean')
        # Flag the state known at this close. Do not pass it to day(defense=):
        # that would liquidate at an open preceding this close's observation.
        bank.nav[-1] = (*bank.nav[-1][:4], defensive)
        signals = []
        shadow_proposals = []
        shadow_contexts = {}
        pending = {}
        remaining = bank.cash / nav
        estimates = {}
        def estimate_for(candidate, ticker, controlling, matches):
            key = (candidate.family, candidate.chromosome_id, ticker)
            if key not in estimates:
                value = (conditional_ev(candidate, ticker, date, controlling, matches)
                         if conditional_ev is not None else None)
                if value is not None and (type(value) not in (int, float) or not isfinite(value)):
                    raise ValueError('conditional EV must be finite or unavailable')
                estimates[key] = value
            return estimates[key]
        for ticker in sorted(bars):
            observation = classify(ticker, date)
            if not isinstance(observation, NicheObservation):
                raise TypeError('native niche observation required')
            controlling = observation.controlling(date)
            position = book.positions.get(ticker)
            held = None
            if position:
                position.peak = max(position.peak, bars[ticker].close)
                held = {**book.held(ticker, bars[ticker].close, nav),
                        'shares': position.shares, 'peak': position.peak,
                        'entry_session': position.entry_session}
            pool = []
            audit = dict(date=date, ticker=ticker, defensive=defensive, controlling_niche=controlling,
                         matches=observation.matches, eligible=[], actions=[], selected=None,
                         opportunity_evaluations=[])
            if defensive:
                if position:
                    signals.append(Signal(ticker, position.owner[0], position.owner[1], 0.))
                    pending[ticker] = position.owner
                    audit['selected'] = (*position.owner, 'DEFENSE_EXIT', 0.)
                if retain_audit: decisions.append(audit)
                continue
            for c in candidates:
                owner = (c.family, c.chromosome_id)
                # The filled incumbent retains management even after niche drift
                # or loss of entry eligibility. Challengers cannot manage it.
                if position:
                    if owner != position.owner:
                        continue
                else:
                    # Related means explicitly supplied qualifying native matches.
                    # No historical center relationship or provenance is inferred.
                    route = tier(RoutedCandidate(c.chromosome_id, c.family, c.niche), controlling)
                    if route is None and c.niche not in dict(observation.matches):
                        continue
                    gate = eligible(c, ticker, date)
                    if type(gate) is not bool:
                        raise ValueError('explicit native chromosome eligibility required')
                    if not gate:
                        continue
                audit['eligible'].append(owner)
                p = native(c, ticker, date, held)
                if p is None:
                    continue
                normalize_proposals([p], date)
                if (p.family, p.chromosome_id) != owner or p.ticker != ticker:
                    raise ValueError('native identity mismatch')
                if p.model_trained_through >= date:
                    raise ValueError('native model must precede decision')
                if position is None and p.action != 'ENTER':
                    raise ValueError('non-entry without incumbent')
                if position is not None and p.action == 'ENTER':
                    raise ValueError('incumbent cannot enter again')
                if p.action in ('ENTER', 'ADD') and p.target_weight <= 0:
                    continue  # zero is abstention, never a minimum allocation
                audit['actions'].append((owner, p.action, p.target_weight))
                pool.append((c, p))
            selected = None
            if position:
                selected = pool[0] if pool else None
            elif pool:
                # Family-qualified identities avoid cross-family alias collisions.
                ranked = []
                for c, p in pool:
                    estimate = estimate_for(c, ticker, controlling, observation.matches)
                    audit['opportunity_evaluations'].append(dict(owner=(c.family, c.chromosome_id),
                        marginal_net_ev=estimate, positive=estimate is not None and estimate > 0))
                    if estimate is None:
                        continue
                    if type(estimate) not in (float, int) or not isfinite(estimate):
                        raise ValueError('conditional EV must be finite or unavailable')
                    if estimate <= 0 or bank.admission_halted:
                        continue
                    route = tier(RoutedCandidate(c.chromosome_id, c.family, c.niche), controlling)
                    priority = 0 if c.niche == controlling and controlling is not None else (1 if route is None else 2)
                    distance = next((dist for name, dist in observation.matches if name == c.niche), float('inf'))
                    value = estimate
                    if selection_genes is not None:
                        value = selection_score(selection_genes,c,controlling,observation.matches,
                            estimate,learning_snapshots[-1] if native_shadow else None,
                            state_from_closes(close_history[ticker],session))
                        if value is None:
                            continue
                        if not isfinite(value) or value <= 0:
                            continue
                    ranked.append((priority, -value, distance, c.family, c.chromosome_id, c, p))
                ranked.sort(key=lambda item: item[:5])
                selected = (ranked[0][-2], ranked[0][-1]) if ranked else None
            if shadow_horizon and position is None and not defensive:
                for c, proposal in pool:
                    if proposal.action != 'ENTER':
                        continue
                    ev = estimate_for(c, ticker, controlling, observation.matches)
                    chosen = selected is not None and (c.family, c.chromosome_id) == (selected[0].family, selected[0].chromosome_id)
                    distance = next((dist for name, dist in observation.matches if name == c.niche), None)
                    shadow_open.append(dict(date=date, ticker=ticker, owner=(c.family,c.chromosome_id),
                        controlling_niche=controlling, specialized_niche=c.niche, niche_distance=distance,
                        conditional_ev=ev, selected=chosen, entry_session=session+1,
                        status='OPEN', horizon=shadow_horizon))
            if native_shadow:
                for c in candidates:
                    skey=(c.family,c.chromosome_id,ticker)
                    shadow_held=shadow_book.positions.get(skey)
                    if shadow_held is None:
                        continue  # Existing native shadow positions need their own exit decisions.
                    shadow_equity=shadow_held['cash']+shadow_held['units']*bars[ticker].close
                    shadow_held['peak']=max(shadow_held.get('peak',shadow_held['entry_price']),bars[ticker].close)
                    sp=native(c,ticker,date,{'shadow':True,'entry_session':shadow_held['entry_session'],
                        'entry':shadow_held['entry_price'],
                        'shares':shadow_held['units'],'peak':shadow_held['peak'],
                        'weight':shadow_held['units']*bars[ticker].close/shadow_equity})
                    if sp is not None:
                        normalize_proposals([sp],date)
                        if (sp.family,sp.chromosome_id,sp.ticker)!=skey or sp.model_trained_through>=date:
                            raise ValueError('invalid native shadow identity/cutoff')
                        if sp.action in ('EXIT','ADD','REDUCE'):shadow_proposals.append(sp)
                for c in candidates:
                    skey=(c.family,c.chromosome_id,ticker)
                    if skey in shadow_book.positions or skey in shadow_book.pending:
                        continue
                    # Shadow all eligible library members, including noncontrolling niches.
                    # The funded selection loop retains its niche-first restriction.
                    gate=eligible(c,ticker,date)
                    if type(gate) is not bool:raise ValueError('explicit shadow eligibility required')
                    if not gate:continue
                    entry=next((p for owner,p in pool if owner==c),None)
                    if entry is None:
                        entry=native(c,ticker,date,None)
                        if entry is None:continue
                        normalize_proposals([entry],date)
                        if (entry.family,entry.chromosome_id,entry.ticker)!=skey or entry.model_trained_through>=date:
                            raise ValueError('invalid shadow entry identity/cutoff')
                    if entry.action!='ENTER':continue
                    shadow_proposals.append(entry)
                    distance=next((d for n,d in observation.matches if n==c.niche), None)
                    shadow_contexts[skey]=(controlling,c.niche,distance)

            if selected:
                c, p = selected
                current = held['weight'] if held else 0.
                target = p.target_weight
                marginal_ev = 0.
                evidence = None
                other_risk = 0.
                if p.action in ('ENTER', 'ADD'):
                    marginal_ev = estimate_for(c, ticker, controlling, observation.matches)
                    if marginal_ev is not None and (type(marginal_ev) not in (int, float) or not isfinite(marginal_ev)):
                        raise ValueError('conditional EV must be finite or unavailable')
                    if marginal_ev is None or marginal_ev <= 0 or bank.admission_halted:
                        target = current
                        marginal_ev = 0.
                evidence = None
                other_risk = 0.
                if position is None and funded_entry_scale is not None:
                    scale = funded_entry_scale()
                    if not isfinite(scale) or not 0 < scale <= 1:
                        raise ValueError('invalid funded entry scale')
                    target *= scale
                if p.action == 'HOLD':
                    target = current
                elif p.action in ('ENTER', 'ADD'):
                    if p.action == 'ADD' and target > current and marginal_ev > 0 and scaling_evidence is not None:
                        evidence = scaling_evidence(c, ticker, date, held, tuple(dict(x) for x in book.realized), tuple(bank.nav))
                        other_risk = sum(pos.shares * bars[t].close / nav *
                            (max(by_owner[pos.owner].stop, by_owner[pos.owner].gap_risk) + bank.round_trip_cost)
                            for t, pos in book.positions.items() if t != ticker)
                    desired = max(0., min(.20 if evidence is not None else .10, target)-current)
                    target = current + desired
                elif p.action == 'REDUCE':
                    target = min(current, target)
                action = p.action
                if position and manager_override is not None:
                    override = manager_override(ticker, date, held, (c, p), tuple(audit['actions']))
                    if override is not None:
                        if (not isinstance(override, tuple) or len(override) != 2 or
                            type(override[0]) not in (int, float) or
                            not isfinite(override[0]) or not 0 <= override[0] <= current or
                            not isinstance(override[1], str) or not override[1]):
                            raise ValueError('manager override requires funded reduction and reason')
                        raise ValueError('unverified manager override disabled: requires funded competing opportunity evidence')
                audit['selected'] = (c.family, c.chromosome_id, action, target)
                if action != 'HOLD' and (action in ('REDUCE', 'EXIT', 'MANAGER_EXIT', 'MANAGER_REDUCE') or target > current):
                    priority_score = marginal_ev
                    if target > current and allocation_priority is not None:
                        priority_score = allocation_priority(c, ticker, date, controlling, observation.matches, marginal_ev)
                        if type(priority_score) not in (int, float) or not isfinite(priority_score):
                            raise ValueError('allocation priority must be finite')
                    audit['marginal_net_ev'] = marginal_ev
                    audit['allocation_priority'] = priority_score
                    audit['scaling_evidence'] = None if evidence is None else vars(evidence)
                    signals.append(Signal(ticker, c.family, c.chromosome_id, target,
                                          score=priority_score, scaling_evidence=evidence, stop_distance=c.stop,
                                          gap_risk=c.gap_risk, other_equity_risk=other_risk))
                    pending[ticker] = (c.family, c.chromosome_id)
            if retain_audit: decisions.append(audit)
        # Compete across funded tickers only with causal, comparable estimates.
        # Sales settle after execution; their proceeds are never credited to
        # today's buying budget. The challenger must remain eligible tomorrow.
        if opportunity_at_close is not None and not defensive:
            entrants = [s for s in signals if s.ticker not in book.positions and s.target_weight > 0]
            committed = sum(s.target_weight for s in entrants)
            available = max(0., bank.cash / nav)
            for ticker, position in sorted(book.positions.items()):
                if committed <= available + 1e-10:
                    break
                if any(s.ticker == ticker for s in signals):
                    continue  # respect incumbent native exit/reduction/add
                held_weight = position.shares * bars[ticker].close / nav
                incumbent = opportunity_at_close(date, ticker, position.owner, True)
                if not isinstance(incumbent, Opportunity) or incumbent.owner != position.owner or incumbent.ticker != ticker:
                    raise ValueError('comparable funded incumbent estimate required')
                challengers = []
                for entry in entrants:
                    estimate = opportunity_at_close(date, entry.ticker, (entry.family, entry.chromosome), False)
                    if not isinstance(estimate, Opportunity) or estimate.owner != (entry.family, entry.chromosome) or estimate.ticker != entry.ticker:
                        raise ValueError('comparable challenger estimate required')
                    challengers.append(estimate)
                transfer = compare(incumbent, challengers, held_weight=held_weight,
                                   free_weight=available, required_weight=committed)
                if transfer is None:
                    continue
                target = max(0., held_weight - transfer.released_weight)
                signals.append(Signal(ticker, *position.owner, target))
                pending[ticker] = position.owner
                available += transfer.released_weight  # forecast only, not spendable
                decisions.append({'date': date, 'ticker': ticker, 'action': 'COMPETITIVE_RELEASE',
                                  'incumbent': transfer.incumbent, 'challenger': transfer.challenger,
                                  'challenger_ticker': transfer.challenger_ticker,
                                  'released_weight': transfer.released_weight,
                                  'net_advantage': transfer.net_advantage,
                                  'settlement_deferred': True})
        # Reserve only settled cash, fees and execution allowances, in global
        # marginal net-EV order. Sales and receivables cannot fund this close.
        remaining = bank.cash / nav
        ranked_signals = []
        reserved_loss = 0.
        for signal in sorted(signals, key=lambda s: (-s.score, s.ticker, s.family, s.chromosome)):
            current = bank.shares.get(signal.ticker, 0.) * bars[signal.ticker].close / nav
            if signal.target_weight > current:
                per_dollar_loss = max(signal.stop_distance, signal.gap_risk) + bank.round_trip_cost
                risk_cap = bank.max_equity_risk / per_dollar_loss if per_dollar_loss else 0.
                requested = signal.target_weight
                cap_target = requested
                # Evidence approval precedes cash reservation. A denied scale
                # request is not permission to top up a drifting ordinary holding.
                if signal.scaling_evidence is not None:
                    cap_target = allowed_target(current, requested, signal.scaling_evidence,
                        stop_distance=signal.stop_distance, gap_risk=signal.gap_risk,
                        max_equity_risk=bank.max_equity_risk)
                    if cap_target <= .10 + 1e-12:
                        cap_target = current
                    # Mandatory limit is per trade (entire candidate position), not portfolio aggregate.
                approved = max(current, min(cap_target, risk_cap))
                desired = max(0., approved - current)
                for audit in reversed(decisions):
                    if audit.get('ticker') == signal.ticker and audit.get('date') == date and audit.get('selected'):
                        audit['reservation'] = dict(requested=requested, current=current,
                            cap_target=cap_target, approved=approved,
                            cap_rejected=cap_target < requested - 1e-12,
                            risk_rejected=min(cap_target, risk_cap) < cap_target - 1e-12)
                        break
                funded = min(desired, remaining / ((1 + bank.friction) * (1 + bank.fees)))
                reserved_loss += funded * per_dollar_loss
                remaining = max(0., remaining - funded * (1 + bank.friction) * (1 + bank.fees))
                signal = replace(signal, target_weight=current + funded)
                for audit in reversed(decisions):
                    if audit.get('ticker') == signal.ticker and audit.get('date') == date and audit.get('selected'):
                        audit['selected'] = (*audit['selected'][:3], signal.target_weight)
                        audit['funding_reason'] = ('GLOBAL_PRIORITY' if allocation_priority is not None else 'GLOBAL_NET_EV') if funded else 'NO_SETTLED_CASH_OR_RISK_BUDGET'
                        break
                if funded <= 0:
                    continue
            ranked_signals.append(signal)
        signals = ranked_signals
        if native_shadow:
            shadow_book.close_session(session,shadow_proposals,shadow_contexts)
        bank.pending = signals
    if len(bank.nav) < 2:
        raise ValueError('require at least two sessions')
    if shadow_horizon:
        shadow_ledger.extend(shadow_open)
    return dict(scope='FUNCTIONAL_RESEARCH_BASELINE', learning_snapshots=learning_snapshots,
                native_shadow_outcomes=shadow_outcomes,
                native_shadow_open=dict(shadow_book.positions) if native_shadow else {},
                native_shadow_calibrator=shadow_calibrator if native_shadow else None,
                shadow_markouts=shadow_ledger,
                shadow_method=('NATIVE_POSITION_EXIT_REPLAY' if native_shadow else
                               'FIXED_HORIZON_MARKOUT_NOT_NATIVE_EXIT_REPLAY'), decisions=decisions,
                ledger=bank.ledger, nav=bank.nav, realized=book.realized,
                pending=list(bank.pending), unsettled=list(bank.unsettled),
                owners={t: p.owner for t, p in book.positions.items()},
                risk_audit=bank.risk_audit, drawdowns=bank.drawdowns,
                max_drawdown=bank.max_drawdown, admission_halted=bank.admission_halted,
                mdd_policy={'ceiling': bank.mdd_limit, 'breached': bank.admission_halted,
                            'feasible': not bank.admission_halted,
                            'action': 'LATCH_NEW_RISK_ADMISSION_KEEP_NATIVE_EXITS',
                            'guaranteed_loss_ceiling': False},
                liquidity={'mode': 'SAFE_SETTLED_CASH_FALLBACK', 'sgov_enabled': False,
                           'reason': 'No verified SGOV price/yield/pay-date adapter on run_slice',
                           'cash_yield_daily': 0., 'settled_cash': bank.cash,
                           'unsettled_cash': sum(v for _, v in bank.unsettled)},
                costs={'fees': fees, 'spread': spread, 'slippage': slippage,
                       'impact': impact, 'round_trip_allowance': bank.round_trip_cost},
                launch_ready=False)
