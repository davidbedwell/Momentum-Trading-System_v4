import sys,json,collections
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from ga5_chromosome_contract import Genome
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.guarded_evaluator_baseline_loss_audit_20261021 import evaluate
r=Path('/opt/mts')
f=pd.read_parquet(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')
f=f[(f.date>='2005-09-14')&(f.date<'2026-09-15')]
p=PreparedSessions(f)
policy=json.loads((r/'ga5_redesign/exploratory79_policy.json').read_text())
target='33a3baa313664e4108d1f4506b640ee78ee86672c0537302adb03598068bbc0c'
g=next(Genome(**x['genome']) for line in (r/'ga6/runs/ga6_production_200_v1/all_evaluations.jsonl').open() if (x:=json.loads(line)) and Genome(**x['genome']).identity()==target)
a=evaluate(p,g,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'])
c=a['closed_position_audit']
losses=[x for x in c if x['realized_pnl']<0]
bands={'under_0_5':0,'0_5_to_1':0,'1_to_2':0,'over_2':0}
for x in losses:
 v=x['realized_loss_fraction']
 if v<.005:bands['under_0_5']+=1
 elif v<.01:bands['0_5_to_1']+=1
 elif v<.02:bands['1_to_2']+=1
 else:bands['over_2']+=1
out={'chromosome':target,'portfolio_cagr':a['cagr_diagnostic'],'portfolio_mdd':a['mdd_diagnostic'],'closed_positions':len(c),'losing_positions':len(losses),'winning_positions':sum(x['realized_pnl']>0 for x in c),'realized_loss_equity_bands':bands,'positions_exceeding_2pct_observed_loss':sum(x['max_observed_loss_fraction']>=.02 for x in c),'max_realized_loss_fraction':max((x['realized_loss_fraction'] for x in losses),default=0),'largest_realized_losses':sorted(losses,key=lambda x:-x['realized_loss_fraction'])[:10],'all_closed_positions':c}
path=r/'ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021/actual_portfolio_loss_audit_20261021.json'
path.write_text(json.dumps(out,indent=2,default=str))
print(json.dumps({k:v for k,v in out.items() if k not in ('all_closed_positions','largest_realized_losses')},default=str),flush=True)
print('TOP_LOSSES',json.dumps(out['largest_realized_losses'][:5],default=str),flush=True)
