"""Historical research replay: REAL completed shadow labels, chronological
selection and shared-capital fills. Retrospective niche centers, simplified
shadow fills and missing PIT sector certification prohibit OOS claims.
"""
import argparse,json,tempfile,hashlib,math
from pathlib import Path
import pandas as pd
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from research_niche_recognizer import label_frame
from defense_policy_v3 import permissions
from policy_shadow_runner import run_and_persist
from learning_ledger import LearningLedger
from chronological_selector import select_day
from shared_capital_execution import SharedCapitalExecution
from risk_allocator import RiskPolicy
ROOT=Path('/opt/mts')
def run(symbol_count=3,start='2023-01-01',end='2024-05-01',out=None):
 cp=json.loads((ROOT/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text());cs=[StructuralCandidate.restore(z) for z in cp['members']]
 frame=pd.read_parquet(ROOT/'ga5_redesign/exploratory79_ga4_enriched.parquet');names=sorted(frame.ticker.unique())[:symbol_count]
 frame=frame[(frame.ticker.isin(names))&(frame.date>='2023-01-01')&(frame.date<end)].sort_values(['ticker','date'])
 labs=label_frame(frame);niche={(str(r.date)[:10],r.ticker):r.research_niche for r in labs.itertuples(index=False)}
 policy=json.loads((ROOT/'ga5_redesign/exploratory79_policy.json').read_text());dates=set(frame.date.dt.strftime('%Y-%m-%d'))
 member={(d,t):bool(v) for d,t,v in policy['membership'] if d in dates and t in names}
 veto=permissions(dates)
 blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
 if out is None:out='/opt/mts/ga6_h/selection_engine/real_label_portfolio_smoke.sqlite'
 Path(out).unlink(missing_ok=True)
 shadows=[]
 for t in names:
  g=frame[frame.ticker==t];n={d:label for (d,s),label in niche.items() if s==t}
  result=run_and_persist(g.to_dict('records'),cs,n,membership=member,blocked=blocked,risk_veto=veto,db_path=out,cohort='DEV79')
  shadows.append(dict(symbol=t,decisions=len(result['decisions']),trades=len(result['trades'])))
 ledger=LearningLedger(out)
 # One-time load of real matured labels; daily scores still enforce strict cutoff.
 decisions={}
 for r in ledger.db.execute('SELECT asof,symbol,niche,chromosome,action,proposal_json FROM decisions'):
  if r[4]=='ENTER':decisions.setdefault((r[0],r[1]),[]).append(dict(symbol=r[1],chromosome=r[3],niche=r[2],target_weight=min(.03,float(json.loads(r[5])['raw_weight'])),evidence_cutoff=r[0]))
 x=SharedCapitalExecution(cash=100000,annual_cash_yield=.03)
 frame=frame[(frame.date>=start)&(frame.date<end)]
 ret={t:{} for t in names};prev={};count=0;selected=0
 for date,g in frame.groupby('date',sort=True):
  ds=str(date)[:10];rows={r.ticker:r._asdict() for r in g.itertuples(index=False)}
  if set(rows)!=set(names):continue
  opens={t:float(r['open'])*float(r['adj_close'])/float(r['close']) for t,r in rows.items()}
  closes={t:float(r['adj_close']) for t,r in rows.items()}
  for t,p in closes.items():
   if t in prev:ret[t][ds]=p/prev[t]-1
   prev[t]=p
  x.start(ds,opens,closes,rows,risk_veto=veto,membership=member,blocked=blocked)
  nav=x.nav[-1][1];holdings={t:q*closes[t]/nav for t,q in x.ledger.holdings.items() if q}
  proposals=[p for t in names for p in decisions.get((ds,t),[]) if not x.ledger.holdings.get(t)]
  # Research-only same-sector conservative grouping; genuine PIT sectors pending.
  selected_day=select_day(ledger,asof=ds,candidates=proposals,cash=x.ledger.available_cash(),nav=nav,holdings=holdings,sector_by_symbol={t:'UNVERIFIED_SECTOR' for t in names},trailing_returns=ret,policy=RiskPolicy(min_observations=10),min_samples=2)
  orders=[dict(symbol=o['symbol'],action=o['action'],weight=o['incremental_weight'],max_weight=.10) for o in selected_day['orders'] if o['action'] in ('ENTER','ADD')]
  selected+=len(orders);x.schedule(ds,orders);count+=1
 vals=[v for _,v in x.nav];peak=vals[0];mdd=0
 for v in vals:peak=max(peak,v);mdd=min(mdd,v/peak-1)
 years=(pd.Timestamp(x.nav[-1][0])-pd.Timestamp(x.nav[0][0])).days/365.25
 result=dict(status='RESEARCH_ONLY_NOT_OOS',symbols=names,sessions=count,shadow=shadows,shadow_outcomes=ledger.db.execute('SELECT count(*) FROM outcomes').fetchone()[0],selected_orders=selected,executed_fills=len(x.ledger.fills),final_nav=vals[-1],cagr=(vals[-1]/100000)**(1/years)-1,mdd=mdd,settled_cash=x.ledger.available_cash(),rejections=len(x.rejections),defense_policy='prior-close A-v2/B/B1/C/R1 only; obsolete historical risk veto excluded',limitations=['retrospective niche centers','shadow replay not evaluator-parity certified','unverified sectors','not purged OOS'])
 print(json.dumps(result,indent=2));ledger.close();return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--symbols',type=int,default=3);p.add_argument('--start',default='2023-01-01');p.add_argument('--end',default='2024-05-01');p.add_argument('--out',default='/opt/mts/ga6_h/selection_engine/real_label_portfolio_smoke.sqlite');a=p.parse_args();run(a.symbols,a.start,a.end,a.out)
