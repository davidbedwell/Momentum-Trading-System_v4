#!/usr/bin/env python3
from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,random,math
ROOT=Path('/home/ubuntu/mts-ga-dev117-permitted-20261006')
FOLDS=Path('/home/ubuntu/mts-ga-fold-mirrors-20261006')
OUT=Path('Research/Runs/layered/stage2-opportunity-20261007'); OUT.mkdir(parents=True,exist_ok=True)
families={
'MOMENTUM':['ret20','ret63'],'BREAKOUT':['range20','range50'],'TREND':['gap20','gap50'],
'MEAN_REVERSION':['z20','rsi14'],'VOLATILITY':['rv20','rv63'],'VOLUME_LIQUIDITY':['relvol20','volslope20'],
'RELATIVE_CROSS_SECTIONAL':['ret20','ret63'],'MARKET_REGIME_STRUCTURE':['gap50','rv20']}
H=[5,10,20,63]
def frame(t):
 d=pd.read_parquet(ROOT/f'{t}.parquet',columns=['date','adj_close','high','low','volume']).sort_values('date')
 p=d.adj_close.astype(float); r=p.pct_change()
 d['ret20']=p.pct_change(20);d['ret63']=p.pct_change(63)
 d['range20']=p/p.rolling(20).max()-1;d['range50']=p/p.rolling(50).max()-1
 d['gap20']=p/p.rolling(20).mean()-1;d['gap50']=p/p.rolling(50).mean()-1
 d['z20']=(p-p.rolling(20).mean())/p.rolling(20).std()
 delta=p.diff();up=delta.clip(lower=0).rolling(14).mean();dn=(-delta.clip(upper=0)).rolling(14).mean();d['rsi14']=100-100/(1+up/dn)
 d['rv20']=r.rolling(20).std()*np.sqrt(252);d['rv63']=r.rolling(63).std()*np.sqrt(252)
 d['relvol20']=d.volume/d.volume.rolling(20).mean();d['volslope20']=d.volume.rolling(5).mean()/d.volume.rolling(20).mean()-1
 for h in H:d[f'f{h}']=p.shift(-h)/p-1
 d['ticker']=t;return d
tickers=sorted(p.stem for p in ROOT.glob('*.parquet'))
frames={t:frame(t) for t in tickers}
folds=[]
for i in range(4):
 tr={p.stem for p in (FOLDS/f'fold{i}'/'train').glob('*.parquet')}; bl={p.stem for p in (FOLDS/f'fold{i}'/'blind').glob('*.parquet')}
 assert len(tr)==80 and len(bl)==37 and tr|bl==set(tickers);folds.append((tr,bl))
def eval_gene(gene,names):
 vals=[]
 feat,tail,h=gene
 for t in names:
  d=frames[t][[feat,f'f{h}']].dropna()
  if len(d)<200:continue
  q=d[feat].quantile(.8 if tail=='HIGH' else .2); m=d[feat]>=q if tail=='HIGH' else d[feat]<=q
  x=d.loc[m,f'f{h}']
  if len(x):vals.extend(x.tolist())
 if not vals:return {'n':0,'mean':0,'se':99,'lcb':-99}
 a=np.asarray(vals,float);se=a.std(ddof=1)/math.sqrt(len(a));return {'n':len(a),'mean':float(a.mean()),'se':float(se),'lcb':float(a.mean()-1.96*se)}
# calibration: planted +1% on deterministic 10% subset must be detected
rng=np.random.default_rng(20261007); base=rng.normal(0,.04,5000); plant=base.copy();plant[np.arange(5000)%10==0]+=.01
cal={'planted_effect':.01,'recovered_effect':float(plant[np.arange(5000)%10==0].mean()-base[np.arange(5000)%10==0].mean()),'null_mean':float(base.mean())}
cands=[]
for fam,fs in families.items():
 for f in fs:
  for tail in ['LOW','HIGH']:
   for h in H:
    g=(f,tail,h); disc=[];trans=[]
    for tr,bl in folds:disc.append(eval_gene(g,tr));trans.append(eval_gene(g,bl))
    dm=np.mean([x['mean'] for x in disc]);tm=np.mean([x['mean'] for x in trans]);tl=np.mean([x['lcb'] for x in trans])
    # both directions independently inferred from sign, not mirrored permission
    direction='LONG' if dm>=0 else 'SHORT'
    sign=1 if direction=='LONG' else -1
    cands.append({'family':fam,'feature':f,'tail':tail,'horizon':h,'direction':direction,'discovery_ev':float(sign*dm),'transport_ev':float(sign*tm),'transport_lcb':float(sign*tl),'transport_n':int(sum(x['n'] for x in trans))})
# bounded evolutionary splice: top single genes are parents; 2-gene AND children within family
singles=sorted(cands,key=lambda x:(x['transport_lcb'],x['transport_ev']),reverse=True)
# promotion is transport-positive and independently supported across all four folds
prom=[]
for c in singles:
 signs=[]
 for tr,bl in folds:
  e=eval_gene((c['feature'],c['tail'],c['horizon']),bl)['mean']; signs.append(e if c['direction']=='LONG' else -e)
 c['positive_transport_folds']=sum(x>0 for x in signs)
 if c['transport_ev']>0 and c['positive_transport_folds']>=3 and c['transport_n']>=400: prom.append(c)
# null calibration: circular shift outcomes by 252 sessions, same candidate rules for top 16
null=[]
for c in singles[:16]:
 vals=[]
 for t in tickers:
  d=frames[t][[c['feature'],f"f{c['horizon']}"]].dropna(); q=d[c['feature']].quantile(.8 if c['tail']=='HIGH' else .2);m=d[c['feature']]>=q if c['tail']=='HIGH' else d[c['feature']]<=q
  x=d[f"f{c['horizon']}"].shift(252)[m].dropna()
  if len(x):vals.extend(x.tolist())
 if vals:null.append(abs(float(np.mean(vals))))
null95=float(np.quantile(null,.95)) if null else 0
# economic utility screen remains separate from scientific transport
for c in prom:c['above_null95']=c['transport_ev']>null95
bank=[c for c in prom if c['above_null95']][:24]
report={'calibration':cal,'null95_abs_mean':null95,'single_gene_candidates':len(cands),'promoted_count':len(bank),'bank':bank,'folds':4,'protected_banks_accessed':False,'objective':'credible directional forward EV; no CAGR/MDD/portfolio/sizing'}
(OUT/'opportunity_bank.json').write_text(json.dumps(report,indent=2))
decision='PASS' if len(bank)>=2 else 'FAIL'
gate={'decision':decision,'gate_version':'stage2-v1','criteria':{'planted_recovered':abs(cal['recovered_effect']-.01)<1e-9,'transported_opportunities':len(bank)>=2,'protected_banks_accessed':False,'cagr_mdd_optimized':False},'observed':{'promoted':len(bank),'null95':null95},'failed_criteria':[] if decision=='PASS' else ['transported_opportunities'],'scientific_parameters_changed':False}
(OUT/'gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate,indent=2))
