#!/usr/bin/env python3
import sys,json,gzip,pickle,hashlib
from pathlib import Path
import pyarrow.parquet as pq
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
sys.path.insert(0,str(ROOT/'Reconstruction/Recovered-GitHub/october-original-code'))
from MTS_V4.search_candidate_analysis import _compile_signal
SEARCH=Path('/home/ubuntu/mts-v4-preserved50-search-reconstructed-20261005')
RAW=Path('/home/ubuntu/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance')
PRED='/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet'
OUT='/home/ubuntu/mts-v4-cache/preserved50_reconstructed_replay_population_20261005.pkl.gz'
FAMS=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
def uniq(sr,f):
 s=set();z=[]
 for o in ('random','ga'):
  for c in sr['families'][f][o]['top_candidates']:
   if c['candidate_id'] not in s:s.add(c['candidate_id']);z.append(c)
 return z
def accepted(sig,h):
 z=[];n=0
 for i,on in enumerate(sig):
  if on and i>=n:z.append(i);n=i+h
 return z
rows=[]; files=sorted(SEARCH.glob('*_COMPUTATIONAL_SEARCH_RECONSTRUCTED_20261005.json'))
for ni,fp in enumerate(files,1):
 sr=json.load(open(fp)); t=sr['ticker']; sid=sr['security_id']
 pred=pq.read_table(PRED,filters=[('security_id','=',sid)]).to_pylist(); pred.sort(key=lambda x:str(x['effective_date']))
 pd=[str(x['effective_date'])[:10] for x in pred]
 bars=pq.read_table(RAW/f'{t}.parquet').to_pylist(); bars.sort(key=lambda x:str(x['date']))
 for b in bars:b['date']=str(b['date'])[:10]
 bd={b['date']:i for i,b in enumerate(bars)}
 for fam in FAMS:
  for cand in uniq(sr,fam):
   h=int(cand['genome']['forward_horizon'])
   for pi in accepted(_compile_signal(pred,cand),h):
    ri=bd.get(pd[pi])
    if ri is None or ri+1>=len(bars) or ri+h>=len(bars):continue
    path=bars[ri+1:ri+h+1]
    ep=float(path[0]['open']); exitp=float(path[-1]['close'])
    lows=[float(x['low'])/ep-1 for x in path]; mi=min(range(len(lows)),key=lambda j:lows[j])
    clean=[{k:(float(x[k]) if k in ['open','high','low','close','volume'] else x[k]) for k in ['date','open','high','low','close','volume']} for x in path]
    rows.append({'ticker':t,'family':fam,'genome':'candidate:'+cand['candidate_id'],'signal_date':pd[pi],'year':int(pd[pi][:4]),'si':pi,'h':h,'path':clean,'ep':ep,'exitp':exitp,'ret':exitp/ep-1,'winner':exitp>ep,'atr':None,'mae':lows[mi],'mi':mi,'_bars':bars})
 print(f'[{ni}/{len(files)}] {t} rows={len(rows)}',flush=True)
payload={'format':'MTS_V4_PRESERVED50_REPLAY_CACHE_RECONSTRUCTED_V1','trade_count':len(rows),'ticker_count':len(files),'source':{'search_reports':len(files),'contract':'8 families x random+GA x 500, seed 20260930','provenance':'RECONSTRUCTED_FROM_SURVIVING_SPEC'},'rows':rows}
with gzip.open(OUT,'wb') as f:pickle.dump(payload,f,pickle.HIGHEST_PROTOCOL)
print('OUT',OUT,'ROWS',len(rows),'TICKERS',len(set(r['ticker'] for r in rows)))
