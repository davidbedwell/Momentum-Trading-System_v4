import pandas as pd,pathlib,json
p=pathlib.Path('/opt/mts/ga6/runs/independent_review');d=pd.read_parquet(p/'trade_entries_prior_features.parquet');e=pd.read_parquet(p/'daily_equity.parquet');r=[]
for label,g in d.groupby('exit_reason'):
 r.append({'reason':label,'trades':len(g),'mean_return':float(g.trade_return.mean()),'median_return':float(g.trade_return.median()),'loss_rate':float((g.trade_return<0).mean()),'median_sessions':float(g.sessions.median())})
# Within entry event, compare differing exit mechanisms where they co-occur across chromosomes.
d['event']=d.ticker.astype(str)+'|'+d.entry_date.astype(str);pivot=d.groupby(['event','exit_reason']).trade_return.mean().unstack()
a='max_40_sessions';b='signal_or_scale_exit';paired=pivot[[a,b]].dropna();difference=paired[a]-paired[b]
report={'exit_groups':r,'paired_same_stock_entry_event':{'events':len(paired),'mean_max_hold_minus_signal':float(difference.mean()),'median_difference':float(difference.median()),'fraction_max_hold_higher':float((difference>0).mean())},'warning':'Same-event comparisons across different chromosomes remain confounded by genome, selection, and exit timing; no causal inference.'}
(p/'EXIT_MECHANICS_AUDIT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
