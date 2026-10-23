import json,pandas as pd,numpy as np
from pathlib import Path
root=Path('/opt/mts/ga5_redesign')
out=root/'dev79_niche_origin_500x1000_20261019'
dest=out/'all13_niche_screen';dest.mkdir(exist_ok=True)
unique={}
for line in (out/'all_evaluations.jsonl').open():
 x=json.loads(line);unique[x['chromosome_id']]=x
rows=[]
for x in unique.values():
 r=x['result'];sh=r.get('shadow',{})
 if sh.get('closed_trades',0)<50 or r.get('fills',0)<20:continue
 g=x['genome']
 rows.append({'niche':x['origin_niche'],'id':x['chromosome_id'],'generation':x['generation'],'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'fitness':x['fitness'],'fills':r['fills'],'closed_trades':sh['closed_trades'],'win_rate':sh.get('win_rate'),'mean_net_return':sh.get('mean_net_return'),'entry_feature':g['entry_feature'],'hold_feature':g['hold_feature'],'exit_feature':g['exit_feature'],'regime_feature':g['regime_feature']})
df=pd.DataFrame(rows);df.to_parquet(dest/'eligible_chromosomes.parquet',index=False)
summary=[]
for niche,g in df.groupby('niche'):
 g=g.sort_values('cagr');n=len(g)
 for label,z in [('bottom',g.iloc[:max(1,n//3)]),('middle',g.iloc[n//3:2*n//3]),('top',g.iloc[2*n//3:])]:
  summary.append({'niche':niche,'cohort':label,'count':len(z),'median_cagr':z.cagr.median(),'median_mdd':z.mdd.median(),'median_win_rate':z.win_rate.median(),'median_shadow_return':z.mean_net_return.median(),'median_fills':z.fills.median()})
pd.DataFrame(summary).to_csv(dest/'cohort_summary_all13.csv',index=False)
print('ELIGIBLE',len(df),'NICHES',df.niche.nunique(),'COUNTS',df.groupby('niche').size().to_dict(),flush=True)
print('OUTPUT',dest,flush=True)
