"""Read-only native state observation and endogenous shadow first divergences.

Trace hooks observe the selected native function only, never patch its policy or
ledger. The source anchor must be unique; unsupported native versions fail shut.
"""
import inspect
import json
import sys
from types import SimpleNamespace
from pathlib import Path
from .phase5_diagnostics import training_panels
from .phase4_native_smoke import GA7_ID, DiagnosticAction
from .funded_shadow import FundedShadow
from .ga7_native_daily_producer import decision
from .ga7_ledger_bridge import replay
from .ledger_audit import funded_shadow
from .first_year_manifest import digest


def first_difference(left, right):
    """Ordered event tapes: preserve order, missing events and exact payloads."""
    for i in range(max(len(left), len(right))):
        a = left[i] if i < len(left) else None
        b = right[i] if i < len(right) else None
        if a != b:
            return dict(index=i, native=a, shadow=b)
    return None


def observe_native(fn, genome, panels, passes):
    source, start = inspect.getsourcelines(fn)
    anchors = [start+i for i, line in enumerate(source) if line.lstrip().startswith('nav.append(cash +')]
    if len(anchors) != 1 or sys.gettrace() is not None:
        raise ValueError('unsupported native observation contract')
    states = []
    def trace(frame, event, arg):
        if frame.f_code is fn.__code__ and event == 'line' and frame.f_lineno == anchors[0]:
            v = frame.f_locals
            states.append(dict(session=v['i'], cash=v['cash'],
                               receivable=sum(x[1] for x in v['unsettled']),
                               positions={t: dict(shares=p.shares, entry=p.entry,
                                   entry_session=p.entered, peak=p.high, initial_stop=p.initial_stop)
                                   for t, p in v['positions'].items()}))
        return trace if frame.f_code is fn.__code__ else None
    sys.settrace(trace)
    try:
        result, ledger = fn(genome, panels, passes, cash_yield=0., record_pass=True)
    finally:
        sys.settrace(None)
    if len(states) != len(panels):
        raise ValueError('incomplete native observations')
    return result, ledger, states


def common_request(action, *, target=None):
    """Smallest safe semantic interface; never translate native sizing silently.

    EXIT and non-rebalancing HOLD have common meaning GIVEN identical holdings.
    Funding/initial-state support must be established separately by a caller.
    """
    if action == 'EXIT' and target == 0:
        return ('EXIT', 0.)
    if action == 'HOLD' and target is None:
        return ('HOLD', None)
    raise ValueError('unsupported common request: native integer/stop/incremental sizing '
                     'and shadow fractional NAV targets require an explicit share-order interface')


def run():
    g, _, _, panels, markets = training_panels()
    from ga7.runner import passes
    from ga7.request_replay import replay_requests, score_signal
    from ga7.portfolio_priority import prioritize_pending
    prior = json.loads(Path('PHASE5_DIAGNOSTICS.json').read_text())
    for path, expected in prior['sources'].items():
        if digest(Path(path)) != expected:
            raise ValueError('source identity changed: '+path)
    if len(panels)!=32 or any(len(bars)!=500 for _,bars,_ in panels) or panels[-1][0]!='2022-12-30':
        raise ValueError('exact authorized 32-session/500-name panel required')
    native, ledger, observed = observe_native(replay_requests, g, panels, passes)
    bridge = replay(g, panels, ledger.requests)
    owner = ('GA7', GA7_ID)
    book = FundedShadow([owner], sessions=[p[0] for p in panels], settlement_sessions=1)
    events = []; first = {}; max_native = 0.
    tape = [SimpleNamespace(**p) if isinstance(p, dict) else p for p in ledger.requests]
    requests = {i: [p for p in tape if p.session == i] for i in range(31)}
    for i, (date, bars, defense) in enumerate(panels):
        begin = len(book.fills)
        opening = dict(cash=book.cash[owner], receivable=sum(v for _,v in book.unsettled[owner]),
                       positions={k[2]: p['shares'] for k,p in book.positions.items()})
        book.open_session(i, markets[date])
        states = book.native_states(markets[date]).get(owner, {})
        n = observed[i]; b = bridge['daily'][i]
        nnav = n['cash']+n['receivable']+sum(p['shares']*bars[t]['close'] for t,p in n['positions'].items())
        residual = max(abs(n['cash']-b['cash']), abs(n['receivable']-b['receivable']), abs(nnav-b['nav']))
        if {t:p['shares'] for t,p in n['positions'].items()} != b['holdings'] or residual > 1e-7:
            raise ArithmeticError('native observed daily bridge mismatch')
        max_native = max(max_native, residual)
        proposals = []; decisions = []; native_decisions = []
        for t, bar in bars.items():
            result = decision(g, bar, states.get(t), defensive=defense,
                              signal_evaluator=passes, strength_evaluator=score_signal)
            action, target = result if result else ('PASS', 0.)
            decisions.append((t, action))
            if result:
                proposals.append(DiagnosticAction(date,t,*owner,action,target))
        if i < 31:
            native_decisions = [(p.ticker, 'ADD' if p.action=='INCREASE' else p.action) for p in requests[i]]
            # Normalize only action spelling, never sizing or portfolio state.
            native_decisions.sort(); decisions.sort()
            nd = first_difference(native_decisions, decisions)
            if nd and 'decision' not in first:
                t = (nd['native'] or nd['shadow'])[0]
                first['decision'] = dict(date=date, difference=nd, ticker=t,
                    dated_features={f:bars[t]['features'][f] for f in (g.feature_a,g.feature_b)}, eligible=bars[t]['eligible'],
                    native_position=n['positions'].get(t), shadow_position=states.get(t),
                    signal=bool(passes(g,bars[t])))
            nr = [p.ticker for p in prioritize_pending(requests[i]) if p.action in ('ENTER','INCREASE','REDUCE','EXIT')]
            sr = [p.ticker for p in sorted(proposals,key=lambda p:(p.action not in ('EXIT','REDUCE'),p.ticker)) if p.action!='HOLD']
            for label, value in [('candidate_set', first_difference(sorted(p.ticker for p in requests[i] if p.action=='ENTER'), sorted(p.ticker for p in proposals if p.action=='ENTER'))),
                                 ('priority', first_difference(nr,sr))]:
                if value and label not in first: first[label] = dict(date=date,difference=value)
        nf = [list(f[1:]) for f in bridge['fills'] if f[0]==i]
        # Exclude research terminal liquidation from the next-open comparison.
        if i==31: nf = nf[:len(nf)-len(b['holdings'])] if b['holdings'] else nf
        sf = [[k[2],side,q,price,fee] for _,k,side,q,price,fee in book.fills[begin:]]
        fd = first_difference(nf,sf)
        if fd and 'fill' not in first: first['fill'] = dict(date=date,difference=fd)
        if i < 31: book.close_session(i, proposals)
        else: book.close_session(i, [])
        events.append(dict(date=date,native=n,shadow_before_open=opening,
            shadow_after_open=dict(cash=book.cash[owner],receivable=sum(v for _,v in book.unsettled[owner]),positions=states),
            native_fills=nf,shadow_fills=sf,native_nav=nnav,shadow_nav=book.nav_history[-1][-1],
            native_capacity=g.capacity,native_sector_cap=3,shadow_capacity=None,
            native_sizing='integer; utility priority; stop budget; settled equity',
            shadow_sizing='fractional; alphabetical priority; prior-close target; opening NAV including receivables',
            decisions_native=native_decisions, decisions_shadow=decisions if i<31 else [],
            requests_native=[vars(p) for p in requests.get(i,[])],
            requests_shadow=[dict(ticker=p.ticker,action=p.action,target=p.target_weight) for p in proposals] if i<31 else [],
            dated_policy_inputs={t:dict(features={f:bar['features'][f] for f in (g.feature_a,g.feature_b)},
                eligible=bar['eligible'],sector=bar.get('sector'),signal=bool(passes(g,bar))) for t,bar in bars.items()}))
    audit = funded_shadow(owners=[owner],sessions=[p[0] for p in panels],bars=markets,
                          fills=book.fills,nav_history=book.nav_history,settlement_sessions=1)
    if len(book.fills)!=prior['funded_fills'] or abs(book.nav_history[-1][-1]-prior['funded_shadow_nav'])>1e-7:
        raise ArithmeticError('original shadow not reproduced')
    return dict(status='BLOCKED_POLICY_AND_EXECUTION_CONVENTIONS_DIFFER',proof_opened=False,
        sessions=32,tickers=500,first_divergences=first,events=events,
        source_hashes={p:digest(Path(p)) for p in prior['sources']},
        native_source_hash=digest(Path(inspect.getfile(replay_requests))),
        native_daily_max_residual=max_native,shadow_audit=audit,
        marked_gap=book.nav_history[-1][-1]-bridge['daily'][-1]['nav'],
        common_request_blocker='No common ENTER/ADD/REDUCE sizing contract. Native API generates endogenous requests internally; bridge accepts fixed requests but only empty opening holdings. FundedShadow accepts target weights, not integer share orders. EXIT/HOLD semantic subset alone cannot reproduce this funded portfolio. Add explicit dated share requests and opening-state import to both independent ledgers before claiming common-request parity.',
        corporate_actions='Adjusted-price/ex-date diagnostic defaults only; no certified event tape; raw splits/pay dates unsupported for parity.',
        attribution='No endogenous gap waterfall asserted. Phase6 fixed-request sensitivities remain path dependent with interactions.')


if __name__ == '__main__':
    result = run()
    Path('PHASE7_DIAGNOSTICS.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False,default=lambda x:x.item())+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='events'},indent=2,default=lambda x:x.item()))
