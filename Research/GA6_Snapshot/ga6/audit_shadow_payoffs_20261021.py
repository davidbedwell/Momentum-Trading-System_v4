import sys,json,statistics,collections
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_ga6 import evaluate
root=Path('/opt/mts')
f=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
f=f[(f.date>='2005-09-14')&(f.date<'2026-09-15')]
p=PreparedSessions(f)
policy=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
target='33a3baa313664e4108d1f4506b640ee78ee86672c0537302adb03598068bbc0c'
rows=(json.loads(line) for line in (root/'ga6/runs/ga6_production_200_v1/all_evaluations.jsonl').open())
g=next(Genome(**row['genome']) for row in rows if Genome(**row['genome']).identity()==target)
a=evaluate(p,g,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
tr=a['shadow']['trades']
def view(t):
 return {k:t.get(k) for k in ('ticker','entry_date','exit_date','entry','exit','sessions','shares','invested','realized_pnl','dividends','net_return','mae','mfe')}
w=sorted((t for t in tr if t['net_return']>0),key=lambda t:-t['net_return'])
l=sorted((t for t in tr if t['net_return']<0),key=lambda t:t['net_return'])
out={'chromosome':target,'basis':'shadow unit-notional, NOT actual portfolio equity','counts':{'wins':len(w),'losses':len(l),'closed':len(tr)},'top_winners':[view(t) for t in w[:10]],'all_losses':[view(t) for t in l],'max_return_price_ratio':max(t['exit']/t['entry'] for t in w),'longest_holding_sessions':max(t['sessions'] for t in tr),'median_holding_sessions':statistics.median(t['sessions'] for t in tr),'dividend_positive_trades':sum(t['dividends']>0 for t in tr),'split_events':None}
path=root/'ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021/shadow_payoff_audit_20261021.json'
path.write_text(json.dumps(out,indent=2,default=str))
print(json.dumps({'path':str(path),'counts':out['counts'],'top_winners':out['top_winners'][:3],'worst_losses':out['all_losses'][:3],'longest_holding_sessions':out['longest_holding_sessions'],'median_holding_sessions':out['median_holding_sessions'],'dividend_positive_trades':out['dividend_positive_trades']},default=str))
