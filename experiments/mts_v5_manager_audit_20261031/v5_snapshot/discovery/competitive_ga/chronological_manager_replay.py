"""Causal research replay of dated native signals and matured outcomes.
Outcomes must be independently produced from native shadow/actual ledgers.
No fabricated calibration or future outcome visibility is permitted.
"""
from inspect import signature
from dataclasses import replace
from math import isfinite
from engines.portfolio_replay.kernel import Replay,Signal
from .causal_calibration import Calibrator
from .causal_manager_proposals import calibrated_proposals
from .manager_order_adapter import orders
from .native_owner_risk_orders import mandatory_orders
from .manager_policy_v2 import Genes
from .position_fill_book import FillBook
from .causal_scaling_evidence import EvidenceBook


def run(days,genes=Genes(),min_samples=5,stops_by_owner=None,scaling_by_owner=None,folds_by_session=None,shadow_book=None,shadow_native=None,settlement_sessions=0,max_sessions=None,risk_provider=None,
        cash_reserve_policy=None):
    """Days: chronological (date,bars,native_proposals,newly_matured_outcomes,defense).
    Defense is observed at close and takes effect at the following open.
    Outcomes enter after today's close decisions, visible only on later dates.
    """
    replay=Replay(settlement_sessions=settlement_sessions)
    if max_sessions is not None and (type(max_sessions) is not int or not 1 <= max_sessions <= 252):
        raise ValueError('bounded replay requires 1..252 sessions')
    owner_flows={}
    reconciliation=[]
    calibrator=Calibrator(min_samples=min_samples)
    decisions=[]
    owners={}
    fills=FillBook()
    evidence_book=EvidenceBook()
    last_date=None
    prior_defense=False
    if shadow_native is not None and shadow_book is None:
        raise ValueError("shadow producer requires independent shadow book")
    for session,(date,bars,native,outcomes,defense) in enumerate(days):
        if max_sessions is not None and session >= max_sessions:
            raise ValueError('bounded replay session limit exceeded')
        if last_date is not None and date<=last_date:
            raise ValueError('dates must be strictly increasing')
        if not bars:
            raise ValueError('empty session bars')
        if any(o.maturity_session!=session for o in outcomes):
            raise ValueError('outcome maturity must match session')
        last_date=date
        missing=set(replay.shares)-set(bars)
        if missing:
            raise ValueError('missing held-position bars: '+','.join(sorted(missing)))
        shadow_matured=shadow_book.open_session(session,bars) if shadow_book is not None else []
        prior_pending=list(replay.pending)
        before=len(replay.ledger)
        opening_cash=replay.cash
        opening_receivable=sum(v for _,v in replay.unsettled)
        opening_shares=dict(replay.shares)
        replay.day(date,bars,(),defense=prior_defense)
        # Independent cashflow identity: corporate actions precede open fills.
        expected_cash=opening_cash+sum(q*bars[t].split*bars[t].dividend
                                      for t,q in opening_shares.items())
        expected_shares={t:q*bars[t].split for t,q in opening_shares.items()}
        for _,ticker,side,qty,price,fee in replay.ledger[before:]:
            direction=1 if side=='BUY' else -1
            expected_cash-=direction*qty*price+fee
            expected_shares[ticker]=expected_shares.get(ticker,0.)+direction*qty
        receivable=sum(v for _,v in replay.unsettled)
        if abs(expected_cash+opening_receivable-replay.cash-receivable)>1e-7:
            raise ValueError('manager cashflow reconciliation failed')
        expected_nav=expected_cash+opening_receivable+sum(q*bars[t].close for t,q in expected_shares.items())
        if abs(expected_nav-replay.nav[-1][1])>1e-7:
            raise ValueError('manager NAV reconciliation failed')
        for ticker,position in fills.positions.items():
            owner_flows[position.owner]=owner_flows.get(position.owner,0.)+position.shares*bars[ticker].split*bars[ticker].dividend
            position.shares*=bars[ticker].split
            position.basis/=bars[ticker].split
            position.entry/=bars[ticker].split
            position.peak/=bars[ticker].split
        for fill in replay.ledger[before:]:
            _,ticker,side,qty,price,fee=fill
            if side=='BUY':
                matches=[s for s in prior_pending if s.ticker==ticker and s.target_weight>0]
                if len(matches)!=1:raise ValueError('unattributed manager buy fill')
                candidate=(matches[0].family,matches[0].chromosome)
                if ticker in owners and owners[ticker]!=candidate:
                    raise ValueError('cross-owner fill without transfer')
                if ticker not in fills.positions and candidate[0]=='GA7' and candidate not in (stops_by_owner or {}):
                    raise ValueError('GA7 chromosome stop configuration required')
                configured=(stops_by_owner or {}).get(candidate,.02)
                fills.apply(fill,candidate,stop=configured if ticker not in fills.positions else None,session=session)
                owners[ticker]=candidate
                owner_flows[candidate]=owner_flows.get(candidate,0.)-qty*price-fee
            else:
                owner=owners.get(ticker)
                owner_flows[owner]=owner_flows.get(owner,0.)+qty*price-fee
                fills.apply(fill,owners.get(ticker))
                if ticker not in fills.positions:owners.pop(ticker,None)
        if set(fills.positions)!=set(replay.shares):
            raise ValueError('fill book and replay holdings disagree')
        for ticker,position in fills.positions.items():
            if abs(position.shares-replay.shares[ticker])>1e-7:
                raise ValueError('fill book share reconciliation failed')
        for ticker,position in fills.positions.items():
            position.peak=max(position.peak,bars[ticker].close)
        nav=replay.nav[-1][1]
        contributions={owner:flow+sum(p.shares*bars[t].close for t,p in fills.positions.items() if p.owner==owner)
                       for owner,flow in owner_flows.items()}
        residual=nav-(100000.+sum(contributions.values()))
        if replay.cash < -1e-7 or abs(residual)>1e-7:
            raise ValueError('shared-bank owner contribution reconciliation failed')
        reconciliation.append(dict(date=date,settled_cash=replay.cash,receivable=receivable,
            nav=nav,owner_pnl=contributions,owner_residual=residual))
        if nav<=0:raise ValueError('invalid portfolio equity')
        holdings={t:qty*bars[t].close/nav for t,qty in replay.shares.items()}
        cash=replay.cash/nav
        if callable(native):
            args=(date,session,bars,dict(holdings),dict(owners),bool(defense))
            native=native(*args,fills) if len(signature(native).parameters)>=7 else native(*args)
        eligible=calibrated_proposals(native,date,session,calibrator)
        # Only the filled owner may manage an incumbent. Another chromosome's
        # attractive score cannot add to, reduce, or take ownership of it.
        eligible=[p for p in eligible if p.ticker not in owners or
                  owners[p.ticker]==(p.family,p.chromosome_id)]
        if shadow_book is not None:
            shadow_signals = (shadow_native(date, session, bars, bool(defense), shadow_book)
                              if shadow_native is not None else native)
            shadow_book.close_session(session, shadow_signals)
        scaling={}
        if folds_by_session is not None:
            for (ticker,family,chromosome),details in (scaling_by_owner or {}).items():
                if owners.get(ticker)!=(family,chromosome):continue
                if ticker not in fills.positions:continue
                position=fills.positions[ticker]
                ev=evidence_book.estimate(family,chromosome,session,
                    signal_confirmed=any(p.ticker==ticker and p.chromosome_id==chromosome and p.action=='ADD' for p in native),
                    position_profitable=bars[ticker].close>position.basis)
                if ev is not None:
                    scaling[(ticker,chromosome)]={**details,'evidence':ev}
        eligible=[p for p in eligible if not (p.action=='INCREASE' and p.target>.10
                  and (p.ticker,p.chromosome_id) not in scaling)]
        effective_genes=genes
        if cash_reserve_policy is not None:
            reserve=cash_reserve_policy(date,session,dict(holdings),cash,tuple(eligible))
            if (not isinstance(reserve,(float,int)) or not isfinite(reserve)
                    or not 0<=reserve<=1):
                raise ValueError('causal cash reserve must be a finite portfolio fraction')
            effective_genes=replace(genes,min_cash=reserve)
        signals=orders(eligible,holdings,cash,effective_genes,defense=defense,scaling=scaling)
        source={(p.ticker,p.chromosome_id):p.family for p in eligible}
        signals=[Signal(s.ticker,source.get((s.ticker,s.chromosome),s.family),
                        s.chromosome,s.target_weight,s.score,s.scaling_evidence,
                        s.stop_distance,s.gap_risk,s.other_equity_risk)
                 for s in signals]
        risk=mandatory_orders(native,date,holdings,owners)
        # Incumbent native risk exits override competing buys or calibration.
        signals=[s for s in signals if s.ticker not in risk]+list(risk.values())
        if defense:
            signals=[Signal(t,owners[t][0],owners[t][1],0.) for t in holdings]
        if risk_provider is not None:
            snapshot=risk_provider(date,session,bars,dict(holdings))
            if snapshot is None or snapshot.as_of != date:
                raise ValueError('current close risk snapshot required')
            replay.risk_snapshot=snapshot
        replay.pending=signals
        prior_defense=bool(defense)
        decisions.append({'date':date,'native':len(native),'eligible':len(eligible),
                          'orders':len(signals),'nav':nav,'defense':bool(defense)})
        for outcome in list(outcomes)+shadow_matured:
            if outcome.maturity_session!=session:
                raise ValueError('outcome maturity must match session')
            calibrator.record(outcome)
        for record in (folds_by_session or {}).get(session,()):
            if record.maturity_session!=session:
                raise ValueError('fold maturity must match session')
            evidence_book.add(record)
    return {'risk_audit':replay.risk_audit,'decisions':decisions,'ledger':list(replay.ledger),
            'reconciliation':reconciliation,'unsettled':list(replay.unsettled),
            'realized':list(fills.realized),
            'position_basis':{t:p.basis for t,p in fills.positions.items()},
            'nav':list(replay.nav),'matured_outcomes':len(calibrator.outcomes),
            'shadow_completed':len(shadow_book.completed) if shadow_book is not None else 0,
            'status':'RESEARCH_CAUSAL_NATIVE_MANAGER_REPLAY',
            'limitations':'requires external native signal and independently verified matured outcome stream; no native producer or PIT certification'}
