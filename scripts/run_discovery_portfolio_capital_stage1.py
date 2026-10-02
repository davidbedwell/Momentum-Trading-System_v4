#!/usr/bin/env python3
import argparse,gzip,pickle,json,hashlib,math,heapq
from pathlib import Path
from collections import defaultdict
import numpy as np
SPLIT='2021-09-13'; EXPECT_TRADES=125002; EXPECT_TICKERS=67; CACHE_FMT='MTS_V4_DISCOVERY_RESEARCH_CACHE_V1'
FLOORS=(.25,.50); CAPS=(1.25,1.50,2.00)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(cache,manifest):
 m=json.load(open(manifest)); b=Path(cache).read_bytes()
 if hashlib.sha256(b).hexdigest()!=m['cache_file_sha256']: raise RuntimeError('cache file hash mismatch')
 z=pickle.loads(gzip.decompress(b))
 if z['format']!=CACHE_FMT or z['trade_count']!=EXPECT_TRADES or z['ticker_count']!=EXPECT_TICKERS or z['split_date']!=SPLIT: raise RuntimeError('cache identity mismatch')
 return z,m
def metric(x):
 x=np.asarray(x,float); neg=x[x<0]; eq=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0,eq])[1:];dd=eq-peak
 return {'n':len(x),'mean':float(x.mean()),'total_return_units':float(x.sum()),'p05':float(np.quantile(x,.05)),'cvar05':float(x[x<=np.quantile(x,.05)].mean()),'max_drawdown_return_units':float(dd.min()),'volatility':float(x.std(ddof=1))}
def atr_ratio(r): return float(r['atr']/r['ep']) if r.get('atr') is not None and r.get('ep') else math.nan
def prevol(r,n=20):
 b=r['_bars'];i=r['si']; a=b[max(0,i-n):i]
 if len(a)<10:return math.nan
 c=np.array([x['close'] for x in a],float); rr=np.diff(np.log(c));return float(rr.std(ddof=1)) if len(rr)>1 else math.nan
def normclip(raw,floor,cap):
 a=np.asarray(raw,float);mask=np.isfinite(a)&(a>0);inv=np.zeros(len(a),float);inv[mask]=1/a[mask];lo,hi=0.0,1000.0/max(float(np.nanmedian(inv[mask])),1e-12)
 for _ in range(80):
  mid=(lo+hi)/2;w=np.ones(len(a),float);w[mask]=np.clip(inv[mask]*mid,floor,cap)
  if float(w.mean())>1:hi=mid
  else:lo=mid
 w=np.ones(len(a),float);w[mask]=np.clip(inv[mask]*((lo+hi)/2),floor,cap);return w
def chronological_downside(rows,kind,minn=100):
 # Strictly causal: a trade outcome becomes usable only after that trade has exited.
 order=sorted(range(len(rows)),key=lambda i:(rows[i]['signal_date'],rows[i]['ticker'],i)); vals=defaultdict(list);glob=[];risk=np.full(len(rows),np.nan);pending=[]
 pos=0
 while pos<len(order):
  d=rows[order[pos]]['signal_date']
  while pending and pending[0][0] < d:
   _,_,key,ret=heapq.heappop(pending); vals[key].append(ret);glob.append(ret)
  end=pos
  while end<len(order) and rows[order[end]]['signal_date']==d:end+=1
  for j in range(pos,end):
   i=order[j];r=rows[i];key=r['genome'] if kind=='genome' else r['family'];hist=vals[key] if len(vals[key])>=minn else glob
   if len(hist)>=minn:
    aa=np.array(hist,float);losses=aa[aa<0];risk[i]=abs(float(np.quantile(losses,.10))) if len(losses)>=20 else float(np.std(aa,ddof=1))
  for j in range(pos,end):
   i=order[j];r=rows[i];key=r['genome'] if kind=='genome' else r['family'];heapq.heappush(pending,(r['path'][-1]['date'],i,key,r['ret']))
  pos=end
 return risk

def evaluate(rows,name,w):
 ret=np.array([r['ret'] for r in rows]); wr=ret*w
 return {'name':name,'trade_metrics':metric(wr),'avg_exposure':float(w.mean()),'p05_exposure':float(np.quantile(w,.05)),'p95_exposure':float(np.quantile(w,.95)),'min_exposure':float(w.min()),'max_exposure':float(w.max())}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 z,m=load(a.cache,a.manifest);rows=z['rows'];dev=[r for r in rows if r['signal_date']<SPLIT];hold=[r for r in rows if r['signal_date']>=SPLIT]
 # Stage 1 selection is Development only. Holdout remains uninspected/uncomputed here.
 out={'protocol_sha256':sha(a.protocol),'cache_manifest':m,'population':{'all':len(rows),'development':len(dev),'holdout_reserved':len(hold),'tickers':len(set(r['ticker'] for r in rows)),'split':SPLIT},'verification_a_accessed':False,'verification_b_accessed':False,'holdout_accessed_for_results':False,'stage':'STAGE1_DEVELOPMENT_ONLY','missingness':{},'baseline':evaluate(dev,'equal_weight',np.ones(len(dev))),'candidates':[]}
 measures={'inverse_atr_price':np.array([atr_ratio(r) for r in dev]),'inverse_realized_vol20':np.array([prevol(r) for r in dev]),'inverse_genome_downside':chronological_downside(dev,'genome'),'inverse_family_downside':chronological_downside(dev,'family')}
 for mn,raw in measures.items():
  out['missingness'][mn]=int(np.sum(~np.isfinite(raw)))
  for fl in FLOORS:
   for cp in CAPS:
    w=normclip(raw,fl,cp);out['candidates'].append(evaluate(dev,f'{mn}_floor{fl}_cap{cp}',w))
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('STAGE1_CANDIDATES='+str(len(out['candidates'])));print('BASE_MEAN='+str(out['baseline']['trade_metrics']['mean']));print('OUTPUT='+a.output);print('HOLDOUT_ACCESSED_FOR_RESULTS=False');print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()
