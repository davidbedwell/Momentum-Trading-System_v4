"""Bounded functionality baseline; no fitted utility, fabricated features or I/O.

The caller supplies dated native niche matches (including native center distances),
feature eligibility and native decisions. GA4 is research-only and never traded.
"""
from dataclasses import dataclass
from datetime import date as iso_date
from math import isfinite

from engines.portfolio_replay.kernel import Replay, Signal
from .hierarchical_search import RoutedCandidate, tier
from .native_signal_contract import normalize_proposals
from .position_fill_book import FillBook
from .synthetic_entry_competition import choose
from .capital_competition import Opportunity, compare
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


def run_slice(days, candidates, *, classify, eligible, native, cash=100000.,
              max_sessions=64, max_stocks=32, selector=None, defense_at_close=None,
              manager_override=None, opportunity_at_close=None, conditional_ev=None,
              shadow_horizon=0, native_shadow=False, selection_genes=None,
              native_genomes=None, genome_registry=None, require_genome_identity=False, session_hook=None, retain_audit=True, funded_entry_scale=None, candidate_provider=None):
    """Stream dated bars through native callbacks and a single funded bank.

    classify(ticker, date) -> NicheObservation; eligible(candidate,ticker,date)
    -> explicit bool; native(candidate,ticker,date,held) -> NativeProposal/None.
    Callbacks receive only today's cutoff and filled incumbent state. They must
    query sources at that cutoff; this API cannot certify caller provenance.
    Cold-start competition uses existing deterministic equal-eligibility rotation,
    never invented expected returns. Entries/adds remain inside the 10% cap.
    """
    candidates = tuple(sorted(candidates, key=lambda c: (c.family, c.chromosome_id)))
    keys = [(c.family, c.chromosome_id) for c in candidates]
    if not 1 <= len(candidates) <= 20000 or len(keys) != len(set(keys)):
        raise ValueError('require 1..20000 unique candidates')
    if any(c.family not in ('GA6', 'GA7', 'HORIZONS') or
           not c.chromosome_id or not 0 < c.stop <= .02 for c in candidates):
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
    bank = Replay(cash=cash, settlement_sessions=1)
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
                    trial['net_return_estimate'] = trial['gross_return'] - 2 * bank.fees
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
        signals = []
        shadow_proposals = []
        shadow_contexts = {}
        pending = {}
        remaining = bank.cash / nav
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
                         matches=observation.matches, eligible=[], actions=[], selected=None)
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
                    if tier(RoutedCandidate(c.chromosome_id, c.family, c.niche), controlling) is None:
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
                audit['actions'].append((owner, p.action, p.target_weight))
                pool.append((c, p))
            selected = None
            if position:
                selected = pool[0] if pool else None
            elif pool:
                # Family-qualified identities avoid cross-family alias collisions.
                mapping = {str(keys.index((c.family, c.chromosome_id))): (c, p) for c, p in pool}
                if conditional_ev is None:
                    winner = (selector(tuple(mapping.items()), ticker, date, session, remaining) if selector is not None else choose([(key, p.target_weight) for key, (_, p) in mapping.items()], ticker, session))
                    selected = mapping[winner[0]] if winner else None
                else:
                    ranked = []
                    for c, p in pool:
                        if p.action != 'ENTER':
                            continue
                        estimate = conditional_ev(c, ticker, date, controlling, observation.matches)
                        if estimate is None:
                            continue
                        if type(estimate) not in (float, int) or not isfinite(estimate):
                            raise ValueError('conditional EV must be finite or unavailable')
                        if estimate <= 0:
                            continue
                        # Specialist first; fallback is allowed only when no
                        # positive-EV controlling-niche specialist exists.
                        specialist = int(c.niche == controlling and controlling is not None)
                        distance = next((dist for name, dist in observation.matches if name == c.niche), float('inf'))
                        if selection_genes is not None:
                            value=selection_score(selection_genes,c,controlling,observation.matches,
                                estimate,learning_snapshots[-1] if native_shadow else None,
                                state_from_closes(close_history[ticker],session))
                            if value is None:continue
                            ranked.append((0,value,-distance,c,p))
                        else:
                            ranked.append((specialist, estimate, -distance, c, p))
                    ranked.sort(key=lambda x: (-x[0], -x[1], -x[2], x[3].family, x[3].chromosome_id))
                    selected = (ranked[0][3], ranked[0][4]) if ranked else None
            if shadow_horizon and position is None and not defensive:
                for c, proposal in pool:
                    if proposal.action != 'ENTER':
                        continue
                    ev = conditional_ev(c, ticker, date, controlling, observation.matches) if conditional_ev else None
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
                if position is None and funded_entry_scale is not None:
                    scale = funded_entry_scale()
                    if not isfinite(scale) or not 0 < scale <= 1:
                        raise ValueError('invalid funded entry scale')
                    target *= scale
                if p.action == 'HOLD':
                    target = current
                elif p.action in ('ENTER', 'ADD'):
                    desired = max(0., min(.10, target)-current)
                    funded = min(desired, remaining)
                    target = current + (desired if opportunity_at_close is not None else funded)
                    remaining -= funded
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
                    signals.append(Signal(ticker, c.family, c.chromosome_id, target))
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
                launch_ready=False)
