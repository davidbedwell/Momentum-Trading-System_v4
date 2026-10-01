#!/usr/bin/env python3
"""Frozen Discovery adverse-path analysis.

Consumes only the corrected 67-ticker trajectory checkpoints.  It never reads
Verification manifests.  The script is deliberately calculation-only: it
reports the complete prespecified grids and does not promote a rule.
"""
from __future__ import annotations
import argparse,gzip,json,math,statistics
from collections import Counter,defaultdict
from datetime import date,timedelta
from pathlib import Path
import numpy as np
from scipy.cluster.vq import kmeans2
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource

PCT_STOPS=np.arange(.01,.1501,.005)
ATR_STOPS=np.arange(.5,5.0001,.25)
SIG_LEVELS=(.5,1,1.5,2,2.5,3,3.5,4,5)
TIME_STOPS=range(1,21)
PCTS=(50,70,80,90,95)
HORIZONS=(2,4,5,10,20)

def loadgz(p):
 with gzip.open(p,"rt") as f:return json.load(f)
def q(v,p):
 a=[x for x in v if x is not None and math.isfinite(x)]
 return float(np.percentile(a,p)) if a else None
def mean(v):
 a=[x for x in v if x is not None and math.isfinite(x)]
 return statistics.fmean(a) if a else None
def pf(v):
 pos=sum(x for x in v if x>0); neg=-sum(x for x in v if x<0)
 return pos/neg if neg else None
def maxdd(v):
 e=peak=0.;dd=0.
 for x in v:
  e+=x;peak=max(peak,e);dd=min(dd,e-peak)
 return dd
def metrics(v):
 if not v:return {"n":0}
 return {"n":len(v),"win_rate":sum(x>0 for x in v)/len(v),"mean":mean(v),"median":q(v,50),"p05":q(v,5),"worst":min(v),"profit_factor":pf(v),"max_drawdown_return_units":maxdd(v),"total_return_units":sum(v)}
def atr20(bars,i):
 if i<20:return None
 tr=[]
 for j in range(i-19,i+1):
  pc=float(bars[j-1]["close"]) if j else float(bars[j]["open"])
  tr.append(max(float(bars[j]["high"])-float(bars[j]["low"]),abs(float(bars[j]["high"])-pc),abs(float(bars[j]["low"])-pc)))
 return statistics.fmean(tr)
def sigma(bars,i,w):
 if i<w:return None
 rr=[math.log(float(bars[j]["close"])/float(bars[j-1]["close"])) for j in range(i-w+1,i+1)]
 return statistics.stdev(rr) if len(rr)>1 else None
def stopret(path,ep,level):
 for x in path:
  op=float(x["open"]);lo=float(x["low"])
  if op<=level:return op/ep-1,True
  if lo<=level:return level/ep-1,True
 return float(path[-1]["close"])/ep-1,False
def path_features(path,ep,atr):
 closes=np.array([float(x["close"])/ep-1 for x in path],float)
 if not len(closes):return {}
 d=np.diff(np.r_[0.,closes]);vel2=np.convolve(d,np.ones(2)/2,"valid") if len(d)>=2 else np.array([])
 vel4=np.convolve(d,np.ones(4)/4,"valid") if len(d)>=4 else np.array([])
 acc=np.diff(d)
 lows=np.array([float(x["low"])/ep-1 for x in path])
 newlow=[];m=0.
 for j,x in enumerate(lows):
  if x<m:newlow.append(j);m=x
 rec=0
 for j in range(1,len(d)):
  if d[j]*d[j-1]<0:rec+=1
 den=float(np.abs(d).sum())
 return {"max_decline_velocity":float(d.min()),"max_recovery_velocity":float(d.max()),"min_acceleration":float(acc.min()) if len(acc) else None,
 "max_acceleration":float(acc.max()) if len(acc) else None,"velocity2_min":float(vel2.min()) if len(vel2) else None,"velocity4_min":float(vel4.min()) if len(vel4) else None,
 "new_lower_lows":len(newlow),"sign_changes":rec,"path_efficiency":abs(float(closes[-1]))/den if den else None,
 "mae_pct":float(lows.min()),"mae_atr":float(lows.min()*ep/atr) if atr else None}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--trajectory-dir",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
 files=sorted(Path(a.trajectory_dir).glob("*.json.gz"))
 if len(files)!=67:raise RuntimeError(f"expected 67 corrected Discovery checkpoints, got {len(files)}")
 rows=[];ticker_bars={}
 for n,p in enumerate(files,1):
  z=loadgz(p)
  if not z.get("rows"):raise RuntimeError(f"{p.name}: empty checkpoint")
  t=z["ticker"]; dates=[r["signal_date"] for r in z["rows"]]
  start=(date.fromisoformat(min(dates))-timedelta(days=500)).isoformat();end="2026-09-16"
  bars=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=start,end_date=end));bars.sort(key=lambda x:str(x["date"]))
  if not bars:raise RuntimeError(f"{t}: zero market bars")
  ticker_bars[t]=bars;bd={str(x["date"])[:10]:i for i,x in enumerate(bars)}
  for r in z["rows"]:
   si=bd.get(r["signal_date"]);h=int(r["horizon"])
   if si is None or si+1>=len(bars) or si+h>=len(bars):continue
   path=bars[si+1:si+h+1];ep=float(path[0]["open"]);exitp=float(path[-1]["close"]);at=atr20(bars,si)
   sig={w:sigma(bars,si,w) for w in (10,20,50,100)}
   lows=[float(x["low"]) for x in path];mae=min(lows)/ep-1;mi=min(range(len(lows)),key=lambda j:lows[j])
   pftr=path_features(path,ep,at)
   rows.append({"ticker":t,"family":r["family"],"genome":r["candidate_id"],"signal_date":r["signal_date"],"year":int(r["signal_date"][:4]),"horizon":h,
    "winner":exitp>ep,"base_return":exitp/ep-1,"ep":ep,"path":path,"mae":mae,"mae_offset":mi,"atr":at,"sigma":sig,"path_features":pftr})
  print(f"[{n}/67] LOADED={t}",flush=True)
 if len(rows)!=125002:raise RuntimeError(f"expected corrected 125002 trades, got {len(rows)}")
 out={"format":"MTS_V4_DISCOVERY_ADVERSE_PATH_PHASE1_V1","trade_count":len(rows),"ticker_count":67,"verification_a_accessed":False,"verification_b_accessed":False,"search_run":False,"refit":False,"rule_selection":False}
 # A/J: MAE distributions and survival.
 dist={}
 for lab,rr in (("WINNER",[r for r in rows if r["winner"]]),("LOSER",[r for r in rows if not r["winner"]])):
  d={"n":len(rr),"mae_pct_percentiles":{str(p):q([-r["mae"] for r in rr],p) for p in PCTS},"sessions_to_mae_percentiles":{str(p):q([r["mae_offset"]+1 for r in rr],p) for p in PCTS}}
  d["mae_atr_percentiles"]={str(p):q([-r["mae"]*r["ep"]/r["atr"] for r in rr if r["atr"]],p) for p in PCTS}
  d["mae_sigma20_percentiles"]={str(p):q([-r["mae"]/r["sigma"][20] for r in rr if r["sigma"][20]],p) for p in PCTS}
  dist[lab]=d
 out["mae_distributions"]=dist
 out["survival_pct"]=[{"threshold":float(s),"winner_share":mean([(-r["mae"]<=s) for r in rows if r["winner"]]),"loser_share":mean([(-r["mae"]<=s) for r in rows if not r["winner"]])} for s in np.arange(.005,.1501,.005)]
 out["survival_atr"]=[{"threshold":float(s),"winner_share":mean([(-r["mae"]*r["ep"]/r["atr"]<=s) for r in rows if r["winner"] and r["atr"]]),"loser_share":mean([(-r["mae"]*r["ep"]/r["atr"]<=s) for r in rows if (not r["winner"]) and r["atr"]])} for s in ATR_STOPS]
 out["survival_sigma"]={str(w):[{"threshold":s,"winner_share":mean([(-r["mae"]/r["sigma"][w]<=s) for r in rows if r["winner"] and r["sigma"][w]]),"loser_share":mean([(-r["mae"]/r["sigma"][w]<=s) for r in rows if (not r["winner"]) and r["sigma"][w]])} for s in SIG_LEVELS] for w in (10,20,50,100)}
 # B: stop tradeoff.
 base=[r["base_return"] for r in rows];stopcurves={"percent":[],"atr":[]}
 for s in PCT_STOPS:
  vals=[];killed=cut=st=0
  for r in rows:
   v,hit=stopret(r["path"],r["ep"],r["ep"]*(1-float(s)));vals.append(v);st+=hit;killed+=bool(hit and r["winner"]);cut+=bool(hit and not r["winner"])
  stopcurves["percent"].append({"stop":float(s),"stopped":st,"winner_killed":killed,"loser_cut":cut,"economics":metrics(vals),"delta_expectancy":mean(vals)-mean(base)})
 for s in ATR_STOPS:
  vals=[];killed=cut=st=n=0
  for r in rows:
   if not r["atr"]:continue
   n+=1;v,hit=stopret(r["path"],r["ep"],r["ep"]-float(s)*r["atr"]);vals.append(v);st+=hit;killed+=bool(hit and r["winner"]);cut+=bool(hit and not r["winner"])
  stopcurves["atr"].append({"stop_atr":float(s),"eligible":n,"stopped":st,"winner_killed":killed,"loser_cut":cut,"economics":metrics(vals),"delta_expectancy":mean(vals)-mean([r["base_return"] for r in rows if r["atr"]])})
 out["stop_tradeoff"]=stopcurves
 # C: time-conditioned path and time stops.
 wins=(("WINNER",True),("LOSER",False));windows=((1,2),(3,4),(5,10),(11,999))
 tc={}
 for lab,w in wins:
  rr=[r for r in rows if r["winner"]==w];tc[lab]={}
  for lo,hi in windows:
   vals=[]
   for r in rr:
    p=r["path"][lo-1:min(hi,len(r["path"]))]
    if p:vals.append(min(float(x["low"])/r["ep"]-1 for x in p))
   tc[lab][f"{lo}-{hi if hi<999 else 'plus'}"]={"n":len(vals),"median_increment_window_low":q(vals,50),"p10":q(vals,10)}
 out["time_conditioned"]=tc
 ts=[]
 for n in TIME_STOPS:
  vals=[]
  for r in rows:
   j=min(n,len(r["path"]))-1
   vals.append(float(r["path"][j]["close"])/r["ep"]-1)
  ts.append({"sessions":n,"economics":metrics(vals)})
 out["time_stops"]=ts
 # K: path-shape outcome summaries.
 out["path_shape"]={}
 for lab,w in wins:
  rr=[r["path_features"] for r in rows if r["winner"]==w]
  keys=("max_decline_velocity","max_recovery_velocity","min_acceleration","max_acceleration","new_lower_lows","sign_changes","path_efficiency")
  out["path_shape"][lab]={"n":len(rr),**{k:{"median":q([x.get(k) for x in rr],50),"p25":q([x.get(k) for x in rr],25),"p75":q([x.get(k) for x in rr],75)} for k in keys}}
 # H: chronological 70/30 boundary, frozen before any optimization.
 ordered=sorted(range(len(rows)),key=lambda i:(rows[i]["signal_date"],rows[i]["ticker"],rows[i]["family"],rows[i]["genome"]))
 cut=int(.7*len(ordered));splitdate=rows[ordered[cut]]["signal_date"]
 dev=[r for r in rows if r["signal_date"]<splitdate];hold=[r for r in rows if r["signal_date"]>=splitdate]
 out["discovery_split"]={"split_date":splitdate,"development_n":len(dev),"holdout_n":len(hold)}
 # G/H: percent-stop x genome development ceiling, then unchanged holdout replay.
 bygen=defaultdict(list)
 for r in dev:bygen[r["genome"]].append(r)
 opts=[]
 for g,rr in bygen.items():
  if len(rr)<100:continue
  for s in PCT_STOPS:
   vals=[stopret(r["path"],r["ep"],r["ep"]*(1-float(s)))[0] for r in rr]
   m=metrics(vals);opts.append((m["mean"],m["win_rate"],m["profit_factor"] or -1,g,float(s),m))
 def replay(item):
  _,_,_,g,s,dm=item;rr=[r for r in hold if r["genome"]==g];vals=[stopret(r["path"],r["ep"],r["ep"]*(1-s))[0] for r in rr]
  return {"genome":g,"stop":s,"development":dm,"holdout":metrics(vals),"holdout_n":len(rr)}
 if opts:
  out["optimization_ceiling"]={"highest_expectancy":replay(max(opts,key=lambda x:x[0])),"highest_success_rate":replay(max(opts,key=lambda x:x[1])),"highest_profit_factor":replay(max(opts,key=lambda x:x[2])),"label":"IN-SAMPLE OPTIMIZATION CEILING — NOT VALIDATED"}
 # O: simple label-blind clustering on development using fixed horizon-5 summaries; scipy only.
 def vec(r):
  p=r["path"][:5]
  if len(p)<5:return None
  cl=np.array([float(x["close"])/r["ep"]-1 for x in p]);lo=np.array([float(x["low"])/r["ep"]-1 for x in p])
  scale=(r["atr"]/r["ep"]) if r["atr"] else None
  if not scale or scale<=0:return None
  return np.array([cl[-1]/scale,lo.min()/scale,cl.min()/scale,cl.max()/scale,r["path_features"]["path_efficiency"] or 0.])
 dv=[(r,vec(r)) for r in dev];dv=[x for x in dv if x[1] is not None]
 X=np.vstack([x[1] for x in dv]);mu=X.mean(0);sd=X.std(0);sd[sd==0]=1;Z=(X-mu)/sd
 best=None
 for k in (2,3,4,5,6,8,10):
  cen,lab=kmeans2(Z,k,minit="points",seed=20261001,iter=30)
  # deterministic compactness proxy; selection uses only geometry, never outcome labels.
  within=float(np.mean([np.linalg.norm(Z[i]-cen[lab[i]]) for i in range(len(Z))]))
  if best is None or within<best[0]:best=(within,k,cen,lab)
 if best:
  _,k,cen,lab=best;devc=[]
  for c in range(k):
   ix=np.where(lab==c)[0];devc.append({"cluster":c,"n":len(ix),"winner_rate_revealed_after_fit":mean([dv[i][0]["winner"] for i in ix])})
  hv=[(r,vec(r)) for r in hold];hv=[x for x in hv if x[1] is not None];hc=Counter();hw=Counter()
  for r,v in hv:
   z=(v-mu)/sd;c=int(np.argmin(np.linalg.norm(cen-z,axis=1)));hc[c]+=1;hw[c]+=int(r["winner"])
  out["label_blind_clustering"]={"horizon":5,"k":k,"selection_metric":"minimum mean within-cluster distance; outcome labels hidden","development":devc,"holdout":[{"cluster":c,"n":hc[c],"winner_rate":hw[c]/hc[c] if hc[c] else None} for c in range(k)]}
 out["limitations"]=["Phase-1 executable covers distribution, percent/ATR stop economics, sigma normalization, time conditioning, path derivatives, chronological split, development-only genome/stop ceiling, and label-blind clustering.","Structural geometry, state transitions, change-point, matching, information-value, competing-risk, and entry-frontier modules are protocol-frozen but intentionally require the phase-2 runner; they are not silently approximated here.","Current-S&P calibration universe remains survivorship-biased; overlapping/repeated trades are not independent.","No optimized Discovery result is validation."]
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("REPORT="+a.output);print(f"TRADES={len(rows)} TICKERS=67 SPLIT={splitdate}")
 print("WIN_MAE_PCT",out["mae_distributions"]["WINNER"]["mae_pct_percentiles"])
 print("LOSS_MAE_PCT",out["mae_distributions"]["LOSER"]["mae_pct_percentiles"])
 if out.get("optimization_ceiling"):print("OPTIMIZATION_CEILING",json.dumps(out["optimization_ceiling"],sort_keys=True))
 print("VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False SEARCH_RUN=False REFIT=False RULE_SELECTION=False")
if __name__=="__main__":main()
