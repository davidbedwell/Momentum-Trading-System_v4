"""Read-only v2 evaluation audit: fixed horizons compared on paired test events."""
import json,pathlib
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008');p=R/'exit_ga_conditional_v2_20261009/report.json';d=json.loads(p.read_text());rows=[]
for x in d['results']:
 if x['status']!='UNCERTIFIED_CHRONOLOGICAL_V2':continue
 b=x['paired_horizon_benchmarks'];h=max(b,key=lambda z:b[z]['benchmark_mean']);selected=str(x['train_baseline_horizon']);rows.append({'index':x['index'],'side':x['side'],'test_events':x['test'],'ga_mean':x['test_ga_mean'],'train_selected_horizon':selected,'gain_vs_train_selected':b[selected]['gain_mean'],'test_oracle_best_horizon':h,'gain_vs_test_oracle':b[h]['gain_mean'],'beats_train_selected':b[selected]['gain_mean']>0,'beats_test_oracle':b[h]['gain_mean']>0,'warning':'test oracle is retrospective and is NOT an admissible model-selection benchmark'})
report={'status':'DIAGNOSTIC_ONLY_NOT_CERTIFIED','n_evaluable':len(rows),'n_beating_train_selected':sum(x['beats_train_selected'] for x in rows),'n_beating_test_oracle':sum(x['beats_test_oracle'] for x in rows),'n_insufficient_support':sum(x['status']=='INSUFFICIENT_ENTRY_SUPPORT' for x in d['results']),'rows':rows,'method':'same test event sample within each chromosome; fixed horizons truncated at last valid executable open; cannot interpret censored forced liquidation as real exit'}
out=R/'exit_ga_conditional_v2_20261009/benchmark_audit.json';out.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
