"""GA6 2020 position-aware native decision replay, research only.

Uses three frozen GA6 structural chromosomes and authentic daily decisions.
Position ownership is locked to the chromosome that entered. No GA7,
competitive selector, independent PIT audit, or GA6 accounting parity.
"""
import json,sqlite3,sys
from pathlib import Path
import numpy as np,pandas as pd
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
from ga6.native_position_decision_adapter import native_action,HeldState
from engines.portfolio_replay.kernel import Replay,Bar,Signal
from engines.portfolio_replay.historical_defense import HistoricalDefense
from discovery.competitive_ga.ga6_entry_execution_diagnostic import SIGNALS,PRICES

OUT=Path('/opt/mts/synthetic-market-lab/reports/ga6_2020_native_position_replay.json')
def run(*,max_hold=None,output=None,return_trace=False,manager=None,manager_entry_cap=None,start_date="2020-01-01",end_date="2020-12-31"):
    if manager_entry_cap is not None and not 0.01 <= manager_entry_cap <= 0.10:
        raise ValueError('manager entry cap outside research bounds')
    sample=pd.read_csv(SIGNALS)
    ids=list(dict.fromkeys(sample.chromosome_id))
    db=sqlite3.connect('/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite')
    candidates={sid:StructuralCandidate.restore(json.loads(db.execute('select definition from chromosomes where id=?',(sid,)).fetchone()[0])) for sid in ids}
    frame=pd.read_parquet(PRICES)
    frame=frame[(frame.date>=start_date)&(frame.date<=end_date)].copy()
    frame['date']=pd.to_datetime(frame.date).dt.strftime('%Y-%m-%d')
    dates=sorted(frame.date.unique())
    byday={d:g.set_index('ticker',drop=False) for d,g in frame.groupby('date')}
    replay=Replay()
    defense=HistoricalDefense()
    held={}
    pending_owners={}
    actions={}
    active_days=0
    trace=[]
    decision_log=[]
    manager_log=[]
    attributed_fills=[]
    for i,day in enumerate(dates):
        dayrows=byday[day]
        bars={t:Bar(float(r.open),float(r.close),float(getattr(r,'dividends',0))) for t,r in dayrows.iterrows() if r.open>0 and r.close>0}
        active=defense.state(day)
        active_days+=int(active)
        trace.append((day,active,dict(replay.shares)))
        # Orders submitted at previous close execute at today's open.
        before=len(replay.ledger)
        replay.day(day,bars,(),defense=active)
        fills=replay.ledger[before:]
        for fill in fills:
            _,ticker,side,qty,price,fee=fill
            owner=(pending_owners.get(ticker) if side=='BUY' and ticker not in held
                   else held[ticker][0] if ticker in held else None)
            if owner is None:raise ValueError('fill without immutable chromosome owner')
            attributed_fills.append({'fill':fill,'chromosome_id':owner,'session':i})
        for _,ticker,side,qty,price,fee in fills:
            if side=='BUY':
                if ticker not in held:
                    owner=pending_owners.get(ticker)
                    if owner is None:raise ValueError('buy without chromosome ownership')
                    held[ticker]=(owner,HeldState(replay.shares[ticker],price,price,i))
                else:
                    owner,state=held[ticker]
                    old=state.shares
                    state.entry_price=(state.entry_price*old+price*qty)/(old+qty)
                    state.shares=replay.shares[ticker]
            elif ticker in held:
                held[ticker][1].shares=replay.shares.get(ticker,0)
                if not replay.shares.get(ticker):del held[ticker]
        if active:
            replay.pending=[]
            pending_owners={}
            continue
        proposals=[]
        for ticker,(sid,state) in list(held.items()):
            if ticker not in dayrows.index:continue
            state.peak_price=max(state.peak_price,float(dayrows.loc[ticker,'close']))
            action,weight=native_action(candidates[sid],dayrows.loc[ticker].to_dict(),state,i)
            actions[action]=actions.get(action,0)+1
            if action=='NO_DATA':continue
            age=i-state.entry_session
            if manager is not None and action in ('HOLD','ADD'):
                override=bool(manager(age,dayrows.loc[ticker].to_dict(),state))
                manager_log.append({'date':day,'ticker':ticker,'chromosome':sid,'age':age,'native_action':action,'manager_exit':override,'entry_price':state.entry_price,'close':float(dayrows.loc[ticker,'close'])})
                if override:
                    action,weight='EXIT',0.
                    actions['MANAGER_EXIT']=actions.get('MANAGER_EXIT',0)+1
            if max_hold is not None and age>=max_hold:action,weight='EXIT',0.
            decision_log.append((day,ticker,sid,age,action))
            current=replay.shares[ticker]*float(dayrows.loc[ticker,'close'])/replay.nav[-1][1]
            # HOLD is a no-order decision: do not rebalance unchanged shares.
            # Without scaling evidence ADD must not create churn either.
            if action=='HOLD' or (action=='ADD' and weight<=current):
                continue
            if action=='REDUCE':target=current*weight
            elif action=='ADD':
                # No historical scaling evidence is supplied in this pilot.
                continue
            else:target=0.
            proposals.append(Signal(ticker,'GA6',sid,min(target,.30)))
        selected={s.ticker for s in proposals}
        # Candidate entry competition uses a deterministic chromosome order,
        # not an asserted cross-chromosome calibrated score.
        for ticker,row in dayrows.iterrows():
            if ticker in held or ticker in selected or ticker not in bars:continue
            for sid in ids:
                action,weight=native_action(candidates[sid],row.to_dict(),None,i)
                if action=='ENTER' and weight>0:
                    proposals.append(Signal(ticker,'GA6',sid,min(.10 if manager_entry_cap is None else manager_entry_cap,weight)))
                    pending_owners[ticker]=sid
                    actions['ENTER']=actions.get('ENTER',0)+1
                    break
        replay.pending=proposals
    nav=np.array([x[1] for x in replay.nav])
    actions['defensive_sessions']=active_days
    actions['remaining_positions']=len(held)
    actions['buy_fills']=sum(1 for x in replay.ledger if x[2]=='BUY')
    actions['sell_fills']=sum(1 for x in replay.ledger if x[2]=='SELL')
    result={'label':'GA6 native position-aware 2020 research replay','sessions':len(dates),
            'chromosomes':len(ids),'fills':len(replay.ledger),
            'ending_nav':round(float(nav[-1]),2),'net_return':round(float(nav[-1]/nav[0]-1),6),
            'max_drawdown':round(float(np.max(1-nav/np.maximum.accumulate(nav))),6),
            'native_action_counts':actions,
            'limitations':'3 preselected chromosomes, native GA6 close decisions with shared research kernel, deterministic owner selection, no GA7, no PIT certification, no native GA6 settled-ledger parity, no earnings embargo, no full scaling evidence.'}
    if output not in (False,'ATTRIBUTED'):
        (Path(output) if output else OUT).write_text(json.dumps(result,indent=2))
    if return_trace:return result,replay,trace
    if output=='ATTRIBUTED':return result,attributed_fills
    if manager is not None:result['manager_decisions']=len(manager_log)
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
