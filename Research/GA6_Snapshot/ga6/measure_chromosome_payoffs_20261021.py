import sys,json,statistics
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
target='33a3baa313664e4108d1f4506b640ee78ee86672c0537302adb03598068bbc0c'
row=next((x for x in reversed(data) if Genome(**x['genome']).identity()==target),None)
assert row,'Chromosome not found'
g=Genome(**row['genome'])
a=evaluate(p,g,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
tr=a['shadow']['trades']
wins=[float(t['net_return']) for t in tr if t['net_return']>0]
losses=[float(t['net_return']) for t in tr if t['net_return']<0]
print(json.dumps({'chromosome':target,'basis':'shadow net return per trade, NOT portfolio-equity loss or dollar P&L','wins':len(wins),'losses':len(losses),'avg_win_pct':statistics.mean(wins)*100,'avg_loss_pct':statistics.mean(losses)*100,'median_win_pct':statistics.median(wins)*100,'median_loss_pct':statistics.median(losses)*100,'largest_win_pct':max(wins)*100,'largest_loss_pct':min(losses)*100,'payoff_ratio':statistics.mean(wins)/(-statistics.mean(losses)),'net_ev_pct':statistics.mean([float(t['net_return']) for t in tr])*100}))
