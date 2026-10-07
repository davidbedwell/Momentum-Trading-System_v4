#!/usr/bin/env python3
from layered_stage_common_20261007 import *
bank=load_bank()[:12];gal=pd.read_parquet(RUN/'stage1-context-map-20261007/galaxy_context.parquet')[['date','state','strength','trajectory']];gal.date=pd.to_datetime(gal.date)
meta=json.load(open(RUN/'sector_metadata_dev117_20261007.json'));sm={x['ticker']:x['sector'] for x in meta['rows']};emap={'Basic Materials':'XLB','Communication Services':'XLC','Consumer Cyclical':'XLY','Consumer Defensive':'XLP','Energy':'XLE','Financial Services':'XLF','Healthcare':'XLV','Industrials':'XLI','Real Estate':'XLRE','Technology':'XLK','Utilities':'XLU'}
sec=pd.read_parquet(RUN/'stage1-context-map-20261007/sector_context.parquet')[['date','ticker','strength','trajectory']].rename(columns={'ticker':'etf','strength':'sec_strength','trajectory':'sec_trajectory'});sec.date=pd.to_datetime(sec.date)
def task(z):
 ci,t=z;c=bank[ci];d=frame(t);d.date=pd.to_datetime(d.date);d=d.merge(gal,on='date',how='left');etf=emap.get(sm.get(t));s=sec[sec.etf==etf];d=d.merge(s[['date','sec_strength']],on='date',how='left');m=mask(d,c);x=signed(d[f"f{c['horizon']}"],c);agree=(d.strength>=0) if c['direction']=='LONG' else (d.strength<=0);sa=(d.sec_strength>=0) if c['direction']=='LONG' else (d.sec_strength<=0)
 return ci,{k:v.dropna().tolist() for k,v in {'planet':x[m],'gal_agree':x[m&agree],'sec_agree':x[m&sa],'both_agree':x[m&agree&sa]}.items()}
res=pmap(task,[(i,p.stem) for i in range(len(bank)) for p in sorted(ROOT.glob('*.parquet'))]);agg=[{k:[] for k in ['planet','gal_agree','sec_agree','both_agree']} for _ in bank]
for i,d in res:
 for k,v in d.items():agg[i][k]+=v
rows=[]
for i,c in enumerate(bank):rows.append({'candidate':c,**{k:{'n':len(v),'ev':float(np.mean(v)) if v else None} for k,v in agg[i].items()}})
write(3,'context-ablation',{'workers':WORKERS,'comparisons':rows,'conclusion':'Context retained only as evidence; no hard permission gate. Sector association is static 2026 metadata and explicitly not historical membership.'})
