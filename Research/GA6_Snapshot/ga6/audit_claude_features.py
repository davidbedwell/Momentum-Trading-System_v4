import pathlib,json
import pandas as pd,numpy as np
p=pathlib.Path('/opt/mts/ga6/runs/independent_review');m=pd.read_parquet(p/'market_indicator_panel.parquet');t=pd.read_parquet(p/'trade_entries_prior_features.parquet')
columns=['ga4_sma_20__v1','ga4_sma_50__v1','ga4_rsi_14__v1','ga4_adx_14__v1','ga4_atr_14__v1','ga4_atr_20__v1','ga4_amihud_illiquidity_20__v1','ga4_turnover__v1','ga4_turnover_relative_20__v1','ga4_breadth_above_sma_200__v1','ga4_return_126__v1']
results=[]
for c in columns:
 for label,frame,name in [('panel',m,c),('entry',t,'prior_'+c)]:
  if name not in frame:results.append({'feature':c,'source':label,'missing_column':True});continue
  s=pd.to_numeric(frame[name],errors='coerce');good=s.dropna()
  results.append({'feature':c,'source':label,'rows':len(s),'missing_pct':round(float(s.isna().mean()*100),3),'distinct':int(good.nunique()),'min':float(good.min()) if len(good) else None,'median':float(good.median()) if len(good) else None,'max':float(good.max()) if len(good) else None,'fraction_exact_one':round(float((good==1).mean()),5) if len(good) else None,'fraction_exact_zero':round(float((good==0).mean()),5) if len(good) else None})
# Assess repeated identical equity curves rather than assuming same rounded metrics implies duplicate strategies.
e=pd.read_parquet(p/'daily_equity.parquet');wide=e.pivot(index='date',columns='chromosome',values='nav');fingerprints={c:__import__('hashlib').sha256(wide[c].to_numpy().tobytes()).hexdigest() for c in wide};from collections import defaultdict
groups=defaultdict(list)
for key,digest in fingerprints.items():groups[digest].append(key)
report={'features':results,'identical_equity_groups':[v for v in groups.values() if len(v)>1],'unique_equity_curves':len(groups),'total_equity_curves':len(fingerprints),'entry_rows':len(t)}
(p/'FEATURE_AND_DUPLICATION_AUDIT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
