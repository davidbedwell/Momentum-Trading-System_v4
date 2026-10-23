"""Freeze DEV87 survivor evidence, deduplicate behaviors, and enforce holdout governance."""
import json,pathlib,hashlib
import pandas as pd
R=pathlib.Path('/opt/mts/ga6/runs/post_v3_comparison_20261022'); d=pd.read_csv(R/'dev87_structural_holdout_replay.csv'); base=pd.read_csv(R/'matched_window_replay.csv');base=base[base.system.eq('structural_v3')]
assert len(d)==130 and d.definition_hash.nunique()==130 and len(base)==130
m=d.merge(base[['definition_hash','cagr','mdd','ev_lcb','completed_trades']],on='definition_hash',suffixes=('_dev87','_dev79'),validate='one_to_one')
m['pass_holdout']=(m.cagr_dev87>0)&(m.mdd_dev87>=-.25)&(m.ev_lcb_dev87>0)&(m.completed_trades_dev87>=100)
m['cagr_change_pp']=100*(m.cagr_dev87-m.cagr_dev79);m['mdd_change_pp']=100*(m.mdd_dev87-m.mdd_dev79)
s=m[m.pass_holdout].copy();s.sort_values(['cagr_dev87','ev_lcb_dev87'],ascending=False,inplace=True)
assert len(s)==53
s.to_csv(R/'dev87_53_survivors_ranked.csv',index=False)
m.to_csv(R/'dev87_full_transport_audit.csv',index=False)
# Matching aggregate statistics are not independent trade-paths; identical metrics can reflect duplicate behavior.
metrics=['cagr_dev87','mdd_dev87','completed_trades_dev87','win_rate','avg_sessions','net_ev','ev_lcb_dev87']
s['behavior_signature']=s[metrics].round(10).astype(str).agg('|'.join,axis=1).map(lambda x:hashlib.sha256(x.encode()).hexdigest())
s.to_csv(R/'dev87_survivor_behavior_signatures.csv',index=False)
report={'status':'COMPLETE','period':'2025-01-01 to 2026-09-14','unseen_stocks':87,'frozen_chromosomes':130,'holdout_passes':len(s),'median_cagr_survivors':float(s.cagr_dev87.median()),'median_mdd_survivors':float(s.mdd_dev87.median()),'survivors_at_least_35pct_cagr':int((s.cagr_dev87>=.35).sum()),'survivor_niche_counts':s.groupby('niche').size().to_dict(),'unique_metric_signatures':int(s.behavior_signature.nunique()),'duplicate_metric_signatures':int(len(s)-s.behavior_signature.nunique()),'independent_validation':'NOT COMPLETE','governance':'DEV87 includes all historical DEV37 tickers; do not treat DEV37 as another independent test. DEV87 has been used to select these 53 and is now consumed as a selection holdout. BLIND17 and frozen A/B groups must remain untouched. No additional unseen stock group verified available.','limitations':['historical membership approximated by observed bars','earnings embargo retrospectively reconstructed; publication timing unverified','risk veto uniformly permissive','stock-universe transfer is not time-forward validation','repeated metric signatures may indicate equivalent behaviors, not proof of identical trades','individual chromosome CAGR/MDD is not a combined portfolio CAGR/MDD']}
(R/'dev87_survivor_validation_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
