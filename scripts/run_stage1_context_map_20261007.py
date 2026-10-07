from pathlib import Path
import pandas as pd, numpy as np, json, hashlib
OUT=Path('Research/Runs/layered/stage1-context-map-20261007'); OUT.mkdir(parents=True,exist_ok=True)
SPY=Path('/home/ubuntu/Momentum-Trading-System_v4/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')
SEC=Path('/home/ubuntu/Momentum-Trading-System_v4/Research/Data/ExternalMarket/G2/legacy_sector_etf_panel_2005_2026.parquet')
assert 'preserved50' not in str(SPY).lower()+str(SEC).lower() and 'blind17' not in str(SPY).lower()+str(SEC).lower()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def enrich(d,key):
 d=d.sort_values('date').copy(); px=d['adj_close'].astype(float)
 d['ret20']=px.pct_change(20); d['ret60']=px.pct_change(60)
 d['ma_gap50']=px/px.rolling(50,min_periods=50).mean()-1
 d['ma_slope50']=px.rolling(50,min_periods=50).mean().pct_change(20)
 d['rv20']=px.pct_change().rolling(20,min_periods=20).std()*np.sqrt(252)
 raw=.35*d.ret20+.35*d.ret60+.20*d.ma_gap50+.10*d.ma_slope50
 # strictly causal expanding normalization: today's scale uses only prior observations
 mu=raw.shift(1).expanding(252).mean(); sd=raw.shift(1).expanding(252).std().replace(0,np.nan)
 d['strength']=(raw-mu)/sd
 d['trajectory']=d.strength-d.strength.shift(20)
 bins=[-np.inf,-1,-.25,.25,1,np.inf]; labels=['Strong Down','Down','Flat','Up','Strong Up']
 d['state']=pd.cut(d.strength,bins=bins,labels=labels).astype('string')
 d['context_key']=key
 return d
spy=pd.read_parquet(SPY); spy['date']=pd.to_datetime(spy.date)
gal=enrich(spy,'SPY')
sec=pd.read_parquet(SEC); sec['date']=pd.to_datetime(sec.date)
ext=OUT/'sector_etf_extension_xlre_xlc_yfinance_20261007.parquet'
if ext.exists():
 extd=pd.read_parquet(ext); extd['date']=pd.to_datetime(extd.date); sec=pd.concat([sec,extd],ignore_index=True)
parts=[]
for t,g in sec.groupby('ticker',sort=True): parts.append(enrich(g,t))
sectors=pd.concat(parts,ignore_index=True)
# sector-v-galaxy relative behavior
g=gal[['date','ret20','ret60','strength']].rename(columns={c:'gal_'+c for c in ['ret20','ret60','strength']})
sectors=sectors.merge(g,on='date',how='left')
sectors['rel20']=sectors.ret20-sectors.gal_ret20; sectors['rel60']=sectors.ret60-sectors.gal_ret60
gal.to_parquet(OUT/'galaxy_context.parquet',index=False); sectors.to_parquet(OUT/'sector_context.parquet',index=False)
def audit(d,name):
 valid=d.state.notna()
 trans=pd.crosstab(d.loc[valid,'state'].shift(),d.loc[valid,'state'],normalize='index').round(4).to_dict()
 return {'name':name,'rows':len(d),'date_min':str(d.date.min().date()),'date_max':str(d.date.max().date()),'state_coverage':float(valid.mean()),'state_counts':{str(k):int(v) for k,v in d.state.value_counts(dropna=False).items()},'transitions':trans}
aud={'stage':'STAGE1','objective':'causal context map only; no trading/P&L/CAGR/MDD optimization','inputs':{str(SPY):sha(SPY),str(SEC):sha(SEC)},'galaxy':audit(gal,'SPY'),'sectors':{t:audit(g,t) for t,g in sectors.groupby('ticker')},'causality':'rolling features use current/past prices; expanding normalization parameters are shifted one row and therefore prior-only','protected_banks_accessed':False}
(OUT/'audit.json').write_text(json.dumps(aud,indent=2,default=str))
# deterministic replay hashes
for p in [OUT/'galaxy_context.parquet',OUT/'sector_context.parquet']:
 print(p,sha(p))
print(json.dumps({'out':str(OUT),'galaxy_rows':len(gal),'sector_rows':len(sectors),'sector_count':sectors.ticker.nunique()},indent=2))
