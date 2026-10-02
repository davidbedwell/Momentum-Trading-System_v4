#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,pickle,json,hashlib,heapq,os,math,multiprocessing as mp
from pathlib import Path
from collections import defaultdict,Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
from MTS_V4.search_candidate_analysis import _compile_signal
from run_discovery_portfolio_capital_stage1_portfolio import metrics,simulate

EXPECTED_PROTOCOL='b1076bd5084e953c1e91fc35b87a7b4612a0fcd925029b9fd488c4399db26270'
EXPECTED_INPUT='507c5a018605b518596036c3c4231d2ab9f8b761ba60c50fb5a1711407501fa6'
SCALE=3.2434248679805613; FLOOR=.5; CAP=2.; MINN=100; BASE=.001321003963011889
G={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def accepted(sig,h):
 out=[];nxt=0
 for i,on in enumerate(sig):
  if on and i>=nxt:out.append(i);nxt=i+h
 return out
def init(cfg,cands):G.update(cfg=cfg,cands=cands)
def cp(t):return Path(G['cfg']['checkpoint'])/f'{t}.pkl.gz'
def process_target(target):
 t=target['ticker'];p=cp(t)
 if p.exists():
  with gzip.open(p,'rb') as f:z=pickle.load(f)
  if z.get('format')=='MTS_V4_CAPITAL_VERIFICATION_A_TARGET_V1':return t,True,len(z['trades'])
 store=ParquetDerivedMarketStore(G['cfg']['root']);sid=target['security_id']
 pred=list(store.query(DerivedMarketQuery(universe_id='sp500-current-calibration-20260915',feature_set_id='mts_market_predictors',feature_set_version='v2',security_ids=(sid,))))
 pred.sort(key=lambda x:str(x['effective_date']));pd=[str(x['effective_date'])[:10] for x in pred]
 if not pred:raise RuntimeError(t+': no predictors')
 bars=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=pd[0],end_date=pd[-1]));bars.sort(key=lambda x:str(x['date']))
 bd={str(x['date'])[:10]:i for i,x in enumerate(bars)};tr=[]
 for c in G['cands']:
  h=int(c['genome']['forward_horizon']); sig=_compile_signal(pred,c)
  for pi in accepted(sig,h):
   si=bd.get(pd[pi]);
   if si is None or si+1>=len(bars) or si+h>=len(bars):continue
   ei=si+1;xi=si+h
   if xi<ei:continue
   ep=float(bars[ei]['open']);xp=float(bars[xi]['close']);mae=min(float(bars[j]['low'])/ep-1 for j in range(ei,xi+1))
   tr.append((t,c['family'],c['candidate_id'],pd[pi],ei,xi,ep,xp/ep-1,mae))
 z={'format':'MTS_V4_CAPITAL_VERIFICATION_A_TARGET_V1','ticker':t,'security_id':sid,'bars':[(str(x['date'])[:10],float(x['close'])) for x in bars],'trades':tr}
 p.parent.mkdir(parents=True,exist_ok=True);tmp=str(p)+'.tmp'
 with gzip.open(tmp,'wb',compresslevel=3) as f:pickle.dump(z,f,protocol=5)
 os.replace(tmp,p);return t,False,len(tr)
def seed_rows(cache):
 with gzip.open(cache,'rb') as f:z=pickle.load(f)
 return [(r['ticker'],r['family'],r['genome'],r['signal_date'],r['path'][-1]['date'],float(r['ret']),float(r['mae']),False,None) for r in z['rows']]
def causal_weights(seed,vr):
 class Hist:
  __slots__=('lo','hi','sum','n')
  def __init__(self):self.lo=[];self.hi=[];self.sum=0.;self.n=0
  def add(self,x):
   self.n+=1;self.sum+=x
   if not self.lo or x<=-self.lo[0]:heapq.heappush(self.lo,-x)
   else:heapq.heappush(self.hi,x)
   target=math.floor((self.n-1)*.10)+1
   while len(self.lo)>target:heapq.heappush(self.hi,-heapq.heappop(self.lo))
   while len(self.lo)<target and self.hi:heapq.heappush(self.lo,-heapq.heappop(self.hi))
  def score(self):
   ev=self.sum/self.n;k=(self.n-1)*.10;frac=k-math.floor(k);x0=-self.lo[0];x1=self.hi[0] if self.hi else x0
   q10=x0+frac*(x1-x0);return ev,max(1e-12,-q10)
 allr=seed+vr;bydate=defaultdict(list)
 for i,r in enumerate(allr):bydate[r[3]].append(i)
 gh=defaultdict(Hist);fh=defaultdict(Hist);glob=Hist();pending=[];w=np.ones(len(vr));src=Counter()
 for d in sorted(bydate):
  while pending and pending[0][0] < d:
   _,i=heapq.heappop(pending);r=allr[i];gh[r[2]].add(r[5]);fh[r[1]].add(r[5]);glob.add(r[5])
  cache={}
  for i in bydate[d]:
   r=allr[i]
   if gh[r[2]].n>=MINN:key=('genome',r[2]);h=gh[r[2]]
   elif fh[r[1]].n>=MINN:key=('family',r[1]);h=fh[r[1]]
   elif glob.n>=MINN:key=('global','global');h=glob
   else:key=('unavailable','unavailable');h=None
   if key not in cache:cache[key]=None if h is None else h.score()
   if r[7]:
    vi=r[8];src[key[0]]+=1;q=cache[key];w[vi]=1.0 if q is None else float(np.clip(max(q[0],0)/q[1]*SCALE,FLOOR,CAP))
  for i in bydate[d]:heapq.heappush(pending,(allr[i][4],i))
 return w,src

def compact_events(trades,bars_by):
 dates=sorted({d for b in bars_by.values() for d,_ in b});dm={d:i for i,d in enumerate(dates)};n=len(trades);ec=np.zeros(len(dates),np.int32);xc=np.zeros(len(dates),np.int32);uc=np.zeros(len(dates),np.int64);lens=np.empty(n,np.int32)
 for i,r in enumerate(trades):
  t,f,g,sd,ei,xi,ep,ret,mae=r;b=bars_by[t];ec[dm[b[ei][0]]]+=1;xc[dm[b[xi][0]]]+=1;l=xi-ei+1;lens[i]=l
  for j in range(ei,xi+1):uc[dm[b[j][0]]]+=1
 eo=np.r_[0,np.cumsum(ec,dtype=np.int64)];xo=np.r_[0,np.cumsum(xc,dtype=np.int64)];uo=np.r_[0,np.cumsum(uc,dtype=np.int64)]
 eiarr=np.empty(n,np.int32);xiarr=np.empty(n,np.int32);ui=np.empty(int(uo[-1]),np.int32);uf=np.empty(int(uo[-1]),np.float32);epos=eo[:-1].copy();xpos=xo[:-1].copy();upos=uo[:-1].copy()
 for i,r in enumerate(trades):
  t,f,g,sd,bi,bx,entry,ret,mae=r;b=bars_by[t];de=dm[b[bi][0]];dx=dm[b[bx][0]];eiarr[epos[de]]=i;epos[de]+=1;xiarr[xpos[dx]]=i;xpos[dx]+=1;prev=entry
  for j in range(bi,bx+1):
   d=dm[b[j][0]];q=upos[d];ui[q]=i;uf[q]=b[j][1]/prev;upos[d]+=1;prev=b[j][1]
 return dates,(eo,eiarr),(xo,xiarr),(uo,ui,uf),lens
def match_exposure(dates,E,X,U,n,target):
 W=np.ones((n,1));lo=1e-8;hi=.01
 for _ in range(16):
  mid=(lo+hi)/2;w,g,c=simulate(dates,E,X,U,W,mid,False);x=metrics(dates,w[:,0],g[:,0],c[:,0])['avg_gross_exposure']
  if x<target:lo=mid
  else:hi=mid
 base=(lo+hi)/2;w,g,c=simulate(dates,E,X,U,W,base,False);return base,metrics(dates,w[:,0],g[:,0],c[:,0])
def main():
 a=argparse.ArgumentParser();
 for x in ('protocol','input','discovery-cache','derived-root','checkpoint-dir','output'):a.add_argument('--'+x,required=True)
 a.add_argument('--workers',type=int,default=6);q=a.parse_args()
 if sha(q.protocol)!=EXPECTED_PROTOCOL or sha(q.input)!=EXPECTED_INPUT:raise RuntimeError('frozen input/protocol hash mismatch')
 inp=json.load(open(q.input));
 if inp.get('verification_a_target_count') != 20 or len(inp.get('verification_a_targets',[])) != 20: raise RuntimeError('A2 evidence budget violation: exactly 20 targets required')
 cands=[dict(c,family_id=c['family']) for c in inp['candidates']];targets=inp['verification_a_targets'];cfg={'root':q.derived_root,'checkpoint':q.checkpoint_dir}
 global G;G={'cfg':cfg,'cands':cands}; Path(q.checkpoint_dir).mkdir(parents=True,exist_ok=True)
 with ProcessPoolExecutor(max_workers=min(q.workers,6),mp_context=mp.get_context("spawn"),initializer=init,initargs=(cfg,cands)) as ex:
  fs={ex.submit(process_target,t):t['ticker'] for t in targets};done=0
  for f in as_completed(fs):
   t,reused,n=f.result();done+=1;print(f'[{done}/{len(targets)}] {"RESUMED" if reused else "BUILT"}={t} trades={n}',flush=True)
 trades=[];bars={};vr=[]
 for target in targets:
  with gzip.open(cp(target['ticker']),'rb') as f:z=pickle.load(f)
  bars[z['ticker']]=z['bars'];off=len(trades);trades.extend(z['trades'])
 for i,r in enumerate(trades):
  t,f,g,sd,bi,bx,ep,ret,mae=r;vr.append((t,f,g,sd,bars[t][bx][0],ret,mae,True,i))
 print('VERIFICATION_TRADES='+str(len(trades)),flush=True);weights,src=causal_weights(seed_rows(q.discovery_cache),vr);print('SCORE_SOURCES='+str(dict(src)),flush=True)
 dates,E,X,U,lens=compact_events(trades,bars);W=np.column_stack([np.ones(len(trades)),weights]);wealth,gross,cash=simulate(dates,E,X,U,W,BASE,False);pol=[]
 for j,name in enumerate(('equal_weight','ev_over_risk_p10_loss_floor0.5_cap2.0')):pol.append({'name':name,'metrics':metrics(dates,wealth[:,j],gross[:,j],cash[:,j])})
 embase,em=match_exposure(dates,E,X,U,len(trades),pol[1]['metrics']['avg_gross_exposure'])
 # ticker breadth: capital-normalized return contribution delta, independent of portfolio ordering
 by=defaultdict(float)
 for r,w in zip(trades,weights):by[r[0]]+=r[7]*(w-1.0)
 usable=len(by);pos=sum(v>0 for v in by.values());b=pol[0]['metrics'];s=pol[1]['metrics']
 crit={'wealth_gt_equal':bool(s['terminal_wealth']>b['terminal_wealth']),'wealth_gt_exposure_matched':bool(s['terminal_wealth']>em['terminal_wealth']),'max_drawdown_no_worse':bool(s['max_drawdown']>=b['max_drawdown']),'cvar05_no_worse':bool(s['daily_cvar05']>=b['daily_cvar05']),'ticker_majority_positive':bool(pos>usable/2)}
 conclusion='VERIFICATION_A2_VALIDATED' if all(crit.values()) else 'VERIFICATION_A2_FAILED'
 out={'format':'MTS_V4_CAPITAL_SIZING_VERIFICATION_A2_V1','protocol_sha256':sha(q.protocol),'input_sha256':sha(q.input),'candidate':'ev_over_risk_p10_loss_floor0.5_cap2.0','frozen_calibration':{'scale':SCALE,'floor':FLOOR,'cap':CAP,'min_history':MINN,'base_trade_fraction':BASE},'verification_a_target_count':len(targets),'verification_a_trades':len(trades),'score_sources':dict(src),'policies':pol,'exposure_matched_baseline':{'base_trade_fraction':embase,'metrics':em},'ticker_breadth':{'usable':usable,'positive':pos,'fraction':pos/usable if usable else None},'criteria':crit,'conclusion':conclusion,'verification_b_accessed':False,'search_run':False,'retune':False}
 Path(q.output).write_text(json.dumps(out,indent=2,sort_keys=True,default=lambda o:o.item() if isinstance(o,np.generic) else (_ for _ in ()).throw(TypeError(type(o).__name__)))+'\n');print('BASE',b,flush=True);print('SIZED',s,flush=True);print('EXPOSURE_MATCHED',em,flush=True);print('BREADTH',out['ticker_breadth'],flush=True);print('CRITERIA',crit,flush=True);print('CONCLUSION='+conclusion,flush=True);print('VERIFICATION_B_ACCESSED=False',flush=True)
if __name__=='__main__':main()
