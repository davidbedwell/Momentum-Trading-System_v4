"""Bounded training-only comparison; diagnostic conventions are not certification."""
import json
import sys
from collections import Counter
from pathlib import Path
import pandas as pd
import numpy as np
from .first_year_features import RAW,COLUMNS
from .first_year_manifest import digest
from .archived_genomes import ga7,ga7_bars
from .phase4_native_smoke import CHECKPOINT,GA7_ID,DiagnosticAction
from .ga7_native_daily_producer import decision
from .funded_shadow import FundedShadow
from .action_utility import paired
from engines.portfolio_replay.kernel import Bar


def training_panels():
    sys.path.insert(0,'/opt/mts/ga7-deploy/ga7_unbounded')
    from ga7.runner import COLUMNS as columns,passes
    from ga7.request_replay import replay_requests,score_signal
    genomes,h=ga7(CHECKPOINT,[GA7_ID]);g=genomes[GA7_ID]
    cache=Path('/tmp/mts_phase3_feature_audit/full.parquet')
    if digest(cache)!=cache.with_suffix('.sha256').read_text():raise ValueError('cache hash mismatch')
    # The only market reads are predicate-bounded to the authorized training prefix.
    raw=pd.read_parquet(RAW,columns=COLUMNS,filters=[('Date','<=',pd.Timestamp('2022-12-30'))]).rename(columns=str.lower)
    features=pd.read_parquet(cache,filters=[('date','<=',pd.Timestamp('2022-12-30'))])
    # GA7 needs close alongside predictor columns, as in the existing parity adapter.
    from .first_year_parity import ga6_features
    features=ga6_features(raw,features)
    dates=sorted(raw.date.unique())[-32:]
    panels=[];markets={}
    for d in dates:
        date=pd.Timestamp(d).strftime('%Y-%m-%d')
        frame=features.loc[features.date==d]
        panel=ga7_bars(frame,decision_date=date,eligibility=dict.fromkeys(frame.ticker,True),columns=columns)
        rows=raw.loc[raw.date==d].set_index('ticker')
        for t,b in panel.items():
            b.update({k:float(rows.loc[t,k]) for k in ('open','low','high')})
            b['eligible']=bool(np.isfinite([b['features'][g.feature_a],b['features'][g.feature_b]]).all())
        panels.append((date,panel,False));markets[date]={t:Bar(b['open'],b['close']) for t,b in panel.items()}
    return g, h, cache, panels, markets


def run():
    g,h,cache,panels,markets=training_panels()
    from ga7.runner import passes
    from ga7.request_replay import replay_requests,score_signal
    native,ledger=replay_requests(g,panels,passes,cash_yield=0.,record_pass=True)
    owner=('GA7',GA7_ID);book=FundedShadow([owner],sessions=[p[0] for p in panels],settlement_sessions=1)
    utilities=[];entry_only=[];actions=Counter()
    for i,(date,panel,_) in enumerate(panels):
        book.open_session(i,markets[date]);states=book.native_states(markets[date]).get(owner,{})
        proposals=[]
        for t,b in panel.items():
            state=states.get(t)
            result=decision(g,b,state,signal_evaluator=passes,strength_evaluator=score_signal)
            if result is None:continue
            action,target=result;actions[action]+=1
            proposals.append(DiagnosticAction(date,t,*owner,action,target))
            if state and action in ('ADD','REDUCE','EXIT') and i+1<len(panels):
                next_bar=panels[i+1][1][t]
                # Isolate this held position with its actual exposure fraction.
                cash=state['shares']*b['close']*(1/state['weight']-1)
                entry_only.append((action,next_bar['close']/next_bar['open']-1))
                utilities.append(paired(chromosome=GA7_ID,family='GA7',action=action,decision=i,maturity=i+1,training_end=31,cash=cash,shares=state['shares'],target=target,execution_open=next_bar['open'],terminal_close=next_bar['close']))
        book.close_session(i,proposals)
    summary={a:dict(entry_only_mean=(sum(r for label,r in entry_only if label==a)/sum(label==a for label,r in entry_only)) if any(label==a for label,r in entry_only) else None,n=len(v:=[o.net_r for o in utilities if o.context[-1]==a]),mean=sum(v)/len(v) if v else None) for a in ('ADD','REDUCE','EXIT')}
    return dict(status='DIAGNOSTIC_NOT_CERTIFIED',proof_opened=False,training_only=True,first=panels[0][0],last=panels[-1][0],sessions=32,tickers=len(panels[0][1]),native_final_nav=native['final_nav'],native_cash_residual=native['cash_reconciliation_error'],native_requests=len(ledger.requests),funded_shadow_nav=book.nav_history[-1][-1],funded_fills=len(book.fills),nav_difference=book.nav_history[-1][-1]-native['final_nav'],actions=dict(actions),paired_utility=summary,utility_contract='one-next-session held action versus HOLD; net NAV fraction; not entry return; no fitting or certification',differences=['native integer shares versus shadow fractional shares','native capacity and three-per-sector limit versus shadow no capacity limit','native INCREASE incremental .03 versus shadow target weights','native REDUCE integer half versus shadow close-weight half at next open','native terminal close liquidation versus shadow retained holdings','native risk stop sizing versus shadow target sizing','both use T+1 proceeds and .001 fee; cash yield disabled','all-true diagnostic eligibility, unknown model lineage, no certified event tape'],sources={str(CHECKPOINT):h,str(cache):digest(cache),str(RAW):digest(RAW)})

if __name__=='__main__':
    result=run();Path('PHASE5_DIAGNOSTICS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
