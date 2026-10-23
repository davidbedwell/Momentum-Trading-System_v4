import json
from pathlib import Path
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6_h.hold_variant_evaluator import evaluate
root=Path('/opt/mts'); base=root/'thunder-migration/mts-certification-20261011/dev87'
cp=json.loads((root/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text())
cs={c.identity():c for c in [StructuralCandidate.restore(z) for z in cp['members']]}
old=pd.read_csv(root/'ga6_h/audits/ga6v3_400_DEV87_same_period_2019_2024.csv')
new=pd.read_csv(root/'ga6_h/audits/ga6v3_400_DEV87_20261023.csv')
chosen={n:g.sort_values('cagr',ascending=False).iloc[0]['identity'] for n,g in new.groupby('niche')}
raw=json.loads((base/'dev87_ga6_policy.json').read_text())
state=build_revised_daily_state().set_index('date');state.index=state.index.strftime('%Y-%m-%d')
frame=pd.read_parquet(base/'dev87_ga6_enriched.parquet')
rows=[]
for start,end,period in [('2019-01-01','2025-01-01','2019-2024'),('2025-01-01','2026-09-15','2025-2026')]:
 f=frame[(frame.date>=start)&(frame.date<end)]; prep=PreparedSessions(f);dates=prep.dates
 policy={'membership':{(d,t):v for d,t,v in raw['membership'] if d in dates},'risk_veto':{d:bool(raw['risk_veto'].get(d) is True and not state.iloc[state.index.get_loc(d)-1].defensive) for d in dates},'blocked':{t:frozenset(v) for t,v in raw['blocked'].items()},'annual_cash_yield':raw['cash_proxy_annual_yield']}
 for niche,identity in chosen.items():
  c=cs[identity];res=evaluate(prep,c.genome,entry_tree=c.entry_tree,max_swing_sessions=40,allocation_audit=True,**policy)
  a=res['allocation_audit'];m=res['ga6_completed_position_metrics'];fills=pd.DataFrame(a['fills']);trades=pd.DataFrame(a['completed']);marks=pd.DataFrame(a['marks'])
  buys=fills[fills.side=='BUY'] if len(fills) else fills
  sums=marks.groupby('symbol').weight.sum().sort_values(ascending=False) if len(marks) else pd.Series(dtype=float)
  invested=marks.groupby('date').weight.sum() if len(marks) else pd.Series(dtype=float)
  row={'period':period,'niche':niche,'identity':identity,'genome':c.checkpoint()['genome'],'entry_tree':c.entry_tree,'cagr':res['cagr_diagnostic'],'mdd':res['mdd_diagnostic'],'win_rate':m['win_rate'],'trades':m['completed_trades'],'avg_sessions':m['avg_sessions'],'signals':res['signal_trace'],'rejections':res['rejections'],'scale_fills':res['scale_fills'],'unique_symbols':int(buys.security.nunique()) if len(buys) else 0,'avg_invested_weight':float(invested.reindex(sorted(dates),fill_value=0).mean()),'top5_exposure_share':float(sums.head(5).sum()/sums.sum()) if len(sums) else 0,'max_stock_weight':float(marks.weight.max()) if len(marks) else 0,'top10_symbols':sums.head(10).index.tolist(),'mean_scaleins_per_trade':float(trades.scaleins.mean()) if len(trades) else None,'median_entry_weight':float(trades.entry_weight.median()) if len(trades) else None,'trade_entries':a['completed'],'fills':a['fills']}
  rows.append(row);print('DONE',period,niche,round(row['cagr'],4),flush=True)
 out=root/'ga6_h/audits/ga6v3_niche_trade_behavior_20261023.json'
 out.write_text(json.dumps(rows,default=str))
 print('CHECKPOINT',out,flush=True)
print('FINISHED',len(rows))
