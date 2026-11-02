"""Vectorized descriptive slopes within each chromosome-year and family-year."""
import json
import numpy as np
import pandas as pd
from study import R
m=json.loads((R/'run_metadata.json').read_text());feats=m['features'];t=pd.read_csv(R/'trades_with_features.csv.gz',low_memory=False);parts=[]
for aset in ['identity_sample','retrospective_top']:
 for system,u in t[t.eligible&t[aset]].groupby('system'):
  for outcome in ['r','win','close_mae_proxy']:
   g=u[u[outcome].notna()];rx=g[feats]-g.groupby(['chromosome_id','year'])[feats].transform('mean');ry=g[outcome]-g.groupby(['chromosome_id','year'])[outcome].transform('mean')
   for dim in ['chromosome_id','family']:
    dx=rx;dy=ry
    if dim=='family':
     dx=g[feats]-g.groupby(['chromosome_id','year','family'])[feats].transform('mean');dy=g[outcome]-g.groupby(['chromosome_id','year','family'])[outcome].transform('mean')
    keys=pd.MultiIndex.from_frame(g[[dim,'year']]);codes,unique=pd.factorize(keys);n=np.bincount(codes);base=unique.to_frame(index=False);base.columns=[dim,'year'];base['n']=n
    for feat in feats:
     x=dx[feat].to_numpy();den=np.bincount(codes,weights=x*x);num=np.bincount(codes,weights=x*dy.to_numpy());valid=(n>=30)&(den>1e-18);z=base.loc[valid].copy();z['feature']=feat;z['within_sd']=np.sqrt(den[valid]/n[valid]);z['effect']=num[valid]/den[valid]*z.within_sd;z['outcome']=outcome;z['system']=system;z['analysis_set']=aset;z['level']=dim+'_year';parts.append(z)
d=pd.concat(parts,ignore_index=True);d.to_csv(R/'within_year_detail.csv',index=False);print('Descriptive chromosome-year/family-year slopes',len(d))
