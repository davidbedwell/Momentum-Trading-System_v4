import sys,json
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_ga6 import evaluate
r=Path('/opt/mts')
f=pd.read_parquet(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')
f=f[(f.date>='2005-09-14')&(f.date<'2026-09-15')]
p=PreparedSessions(f)
policy=json.loads((r/'ga5_redesign/exploratory79_policy.json').read_text())
data=[json.loads(line) for line in (r/'ga6/runs/ga6_production_200_v1/all_evaluations.jsonl').open()]
g=Genome(**max(data,key=lambda x:x['fitness'])['genome'])
a=evaluate(p,g,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
tr=a['shadow']['trades']
win=sum(t['net_return']>0 for t in tr);loss=sum(t['net_return']<0 for t in tr);flat=len(tr)-win-loss
print(json.dumps({'chromosome':g.identity(),'basis':'shadow closed trades, not cash-constrained portfolio fills','closed':len(tr),'wins':win,'losses':loss,'flat':flat,'win_rate':win/len(tr) if tr else None,'portfolio_fill_count':a['reconciliation']['portfolio_trade_count']}))
