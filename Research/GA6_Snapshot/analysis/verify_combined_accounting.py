import sys,json,pandas as pd,numpy as np
from pathlib import Path
sys.path.insert(0,'/opt/mts')
from ga6_h.run_four_way_trade_audit import ROOT,sources,START,END
from ga6_h.hold_variant_evaluator import evaluate
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
p=ROOT/'ga6_h/audits'; checkpoint=json.loads((ROOT/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text()); cs=[StructuralCandidate.restore(z) for z in checkpoint['members']]
state=build_revised_daily_state().set_index('date');state.index=state.index.strftime('%Y-%m-%d')
frames={};policies={}
for n,(f,pol) in sources.items():
 frame=pd.read_parquet(ROOT/f);frames[n]=frame[(frame.date>=START)&(frame.date<END)].copy();policies[n]=json.loads((ROOT/pol).read_text())
rows=[]
for cohort in ['DEV79','DEV87','DEV79_DEV87','DEV50b']:
 frame=pd.concat([frames['DEV79'],frames['DEV87']],ignore_index=True) if cohort=='DEV79_DEV87' else frames[cohort]
 rawlist=[policies['DEV79'],policies['DEV87']] if cohort=='DEV79_DEV87' else [policies[cohort]]
 dates=set(frame.date.dt.strftime('%Y-%m-%d'));tickers=set(frame.ticker)
 membership={(d,t):v for raw in rawlist for d,t,v in raw['membership'] if d in dates and t in tickers}
 blocked={t:frozenset(v) for raw in rawlist for t,v in raw['blocked'].items()}
 veto={d:bool(all(raw['risk_veto'].get(d) is True for raw in rawlist) and not state.iloc[state.index.get_loc(d)-1].defensive) for d in dates}
 prepared=PreparedSessions(frame)
 original=pd.read_csv(p/f'GA6v3_400_{cohort}_trade_ledger_2019_2024.csv').set_index('index')
 for i in [382,54,74]:
  c=cs[i];r=evaluate(prepared,c.genome,entry_tree=c.entry_tree,max_swing_sessions=40,allocation_audit=True,membership=membership,blocked=blocked,risk_veto=veto,annual_cash_yield=.03)
  o=original.loc[i];nav=pd.DataFrame(r['calendar_nav'],columns=['date','nav']); nav['date']=pd.to_datetime(nav.date)
  years=(nav.date.iloc[-1]-nav.date.iloc[0]).days/365.25
  independently_calculated_cagr=(nav.nav.iloc[-1]/100000)**(1/years)-1
  independently_calculated_mdd=(nav.nav/nav.nav.cummax().clip(lower=100000)-1).min()
  err=r['reconciliation']['cash_flow_nav_error'];assert abs(err)<.01
  assert abs(independently_calculated_cagr-o.cagr)<1e-9,(cohort,i,independently_calculated_cagr,o.cagr)
  assert abs(independently_calculated_mdd-o.mdd)<1e-9,(cohort,i,independently_calculated_mdd,o.mdd)
  assert len(r['allocation_audit']['completed'])==int(o.trades)
  rows.append({'cohort':cohort,'chromosome':i,'saved_cagr':o.cagr,'recomputed_cagr':independently_calculated_cagr,'saved_mdd':o.mdd,'recomputed_mdd':independently_calculated_mdd,'cashflow_nav_error':err,'start_nav':nav.nav.iloc[0],'end_nav':nav.nav.iloc[-1],'sessions':len(nav),'trade_count':int(o.trades),'fees':r['reconciliation']['fees'],'cash_yield':r['reconciliation']['cash_yield'],'nav_reconciled':True})
  print('PASS',cohort,i,'CAGR',round(o.cagr,6),'MDD',round(o.mdd,6),'ending NAV',round(nav.nav.iloc[-1],2),'recon err',round(err,9),flush=True)
pd.DataFrame(rows).to_csv(p/'GA6v3_top3_independent_nav_accounting_audit.csv',index=False)
