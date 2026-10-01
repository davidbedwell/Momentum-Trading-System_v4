#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,math,statistics
from collections import Counter,defaultdict
from datetime import date,timedelta
from pathlib import Path
import numpy as np
from sklearn.metrics import mutual_info_score
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
MAS=(10,20,30,40,50,75,100,150,200); EMAS=(20,50); PRIOR=(5,10,20,50)
HPTS=(2,4,5,10); FAV=(.01,.02,.03,.05,.08,.10); ATR_EVT=(.5,1,1.5,2,3)
def loadgz(p):
 with gzip.open(p,"rt") as f:return json.load(f)
def mean(v):
 a=[float(x) for x in v if x is not None and math.isfinite(float(x))]
 return statistics.fmean(a) if a else None
def q(v,p):
 a=[float(x) for x in v if x is not None and math.isfinite(float(x))]
 return float(np.percentile(a,p)) if a else None
def atr20(b,i):
 if i<20:return None
 tr=[]
 for j in range(i-19,i+1):
  pc=float(b[j-1]["close"]);h=float(b[j]["high"]);l=float(b[j]["low"])
  tr.append(max(h-l,abs(h-pc),abs(l-pc)))
 return statistics.fmean(tr)
def ema(vals,n):
 a=2/(n+1);out=[];x=None
 for v in vals:x=v if x is None else a*v+(1-a)*x;out.append(x)
 return out
def slope_class(cur,old,at):
 if not at:return None
 s=(cur-old)/at
 return "POS" if s>.10 else ("NEG" if s<-.10 else "FLAT")
def swings(b):
 lows={};highs={}
 for i in range(2,len(b)-2):
  lo=float(b[i]["low"]);hi=float(b[i]["high"])
  if lo<float(b[i-1]["low"]) and lo<float(b[i-2]["low"]) and float(b[i+1]["low"])>lo and float(b[i+2]["low"])>lo:lows[i+2]=(i,lo)
  if hi>float(b[i-1]["high"]) and hi>float(b[i-2]["high"]) and float(b[i+1]["high"])<hi and float(b[i+2]["high"])<hi:highs[i+2]=(i,hi)
 return lows,highs
def page_hinkley(xs,delta=.005,lamb=5.0,alpha=.999):
 m=c=mn=0.
 for i,x in enumerate(xs,1):
  m=alpha*m+(1-alpha)*x;c+=x-m-delta;mn=min(mn,c)
  if c-mn>lamb:return i
 return None
def entropy(y):
 if not y:return 0.
 p=sum(y)/len(y)
 if p in (0,1):return 0.
 return -p*math.log2(p)-(1-p)*math.log2(1-p)
def econ(v):
 if not v:return {"n":0}
 pos=sum(x for x in v if x>0);neg=-sum(x for x in v if x<0)
 return {"n":len(v),"mean":mean(v),"median":q(v,50),"win_rate":sum(x>0 for x in v)/len(v),"profit_factor":pos/neg if neg else None}
def load_rows(td):
 files=sorted(Path(td).glob("*.json.gz"))
 if len(files)!=67:raise RuntimeError(f"expected 67 checkpoints got {len(files)}")
 rows=[]
 for n,p in enumerate(files,1):
  z=loadgz(p);t=z["ticker"];ds=[r["signal_date"] for r in z["rows"]]
  start=(date.fromisoformat(min(ds))-timedelta(days=700)).isoformat()
  b=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=start,end_date="2026-09-16"));b.sort(key=lambda x:str(x["date"]))
  bd={str(x["date"])[:10]:i for i,x in enumerate(b)};cl=[float(x["close"]) for x in b]
  ma={m:np.convolve(cl,np.ones(m)/m,"valid") for m in MAS};em={m:ema(cl,m) for m in EMAS};sl,sh=swings(b)
  for r in z["rows"]:
   si=bd.get(r["signal_date"]);h=int(r["horizon"])
   if si is None or si+1>=len(b) or si+h>=len(b):continue
   path=b[si+1:si+h+1];ep=float(path[0]["open"]);exitp=float(path[-1]["close"]);at=atr20(b,si)
   lows=np.array([float(x["low"]) for x in path]);mi=int(np.argmin(lows));mae=float(lows[mi]/ep-1)
   rows.append({"ticker":t,"family":r["family"],"genome":r["candidate_id"],"signal_date":r["signal_date"],"year":int(r["signal_date"][:4]),"si":si,"h":h,"path":path,"ep":ep,"exitp":exitp,"ret":exitp/ep-1,"winner":exitp>ep,"atr":at,"mae":mae,"mi":mi,"_bars":b,"_ma":ma,"_ema":em,"_sl":sl,"_sh":sh})
  print(f"[{n}/67] LOADED={t}",flush=True)
 if len(rows)!=125002:raise RuntimeError(f"expected 125002 rows got {len(rows)}")
 return rows
def structure_for(r):
 b=r["_bars"];si=r["si"];at=r["atr"];path=r["path"];refs=[]
 if at:
  for m in MAS:
   if si>=m+4:
    arr=r["_ma"][m];cur=float(arr[si-m+1]);old=float(arr[si-m-4]);refs.append((f"SMA{m}",cur,slope_class(cur,old,at)))
  for m in EMAS:
   if si>=5:
    cur=float(r["_ema"][m][si]);old=float(r["_ema"][m][si-5]);refs.append((f"EMA{m}",cur,slope_class(cur,old,at)))
  for w in PRIOR:
   if si>=w:
    refs.append((f"PRIOR_LOW_{w}",min(float(x["low"]) for x in b[si-w+1:si+1]),None))
    refs.append((f"PRIOR_HIGH_{w}",max(float(x["high"]) for x in b[si-w+1:si+1]),None))
  sl=[v for k,v in r["_sl"].items() if k<=si];sh=[v for k,v in r["_sh"].items() if k<=si]
  if sl:refs.append(("SWING_LOW",sl[-1][1],None))
  if sh:refs.append(("SWING_HIGH",sh[-1][1],None))
 out={}
 for name,ref,sc in refs:
  touch=sweep=fail=reclaim=False;pen=0.;rn=None;br=0
  for j,x in enumerate(path,1):
   lo=float(x["low"]);hi=float(x["high"]);cl=float(x["close"])
   if lo<=ref<=hi:touch=True
   if lo<ref:
    pen=max(pen,(ref-lo)/at)
    if (ref-lo)<=.5*at and (cl>ref or (j<len(path) and float(path[j]["close"])>ref)):sweep=True
   br=br+1 if cl<ref else 0
   if pen>.5 or br>=3:fail=True
   if touch and cl>ref and rn is None:reclaim=True;rn=j
  out[name]={"slope":sc,"touch":touch,"sweep":sweep,"failure":fail,"reclaim":reclaim,"reclaim_session":rn,"max_pen_atr":pen}
 return out
def recovery_stats(r):
 trough=r["ep"];lowi=0;marks={.25:None,.5:None,.75:None,1.:None};recs=[]
 for j,x in enumerate(r["path"],1):
  lo=float(x["low"]);c=float(x["close"])
  if lo<trough:trough=lo;lowi=j
  ae=max(r["ep"]-trough,0);f=(c-trough)/ae if ae>0 else 1.;recs.append(f)
  for k in marks:
   if marks[k] is None and f>=k:marks[k]=j
 return {"recs":recs,"first25":marks[.25],"first50":marks[.5],"first75":marks[.75],"first100":marks[1.],"causal_low_session":lowi}
def states(r,s,rc):
 out=[];mn=r["ep"];af=any(v["failure"] for v in s.values());aw=any(v["sweep"] for v in s.values())
 for j,x in enumerate(r["path"]):
  lo=float(x["low"]);cl=float(x["close"]);prev=r["ep"] if j==0 else float(r["path"][j-1]["close"]);new=lo<mn;mn=min(mn,lo)
  if af:z="STRUCTURAL_FAILURE"
  elif aw:z="STRUCTURAL_SWEEP"
  elif cl>=r["ep"]:z="RECLAIMED"
  elif new:z="NEW_LOW"
  elif rc["recs"][j]>=.5:z="RECOVERING_GE50"
  elif rc["recs"][j]>=.25:z="RECOVERING_25_50"
  elif rc["recs"][j]>0:z="RECOVERING_LT25"
  elif r["atr"] and abs(cl-prev)<=.10*r["atr"]:z="STALLED"
  elif cl<prev:z="DECLINING"
  else:z="STALLED"
  out.append(z)
 return out
def event_race(r,s,rc):
 first={"RECOVERY_25":rc["first25"],"RECLAIM":rc["first100"],"STRUCTURAL_SWEEP":1 if any(v["sweep"] for v in s.values()) else None,"STRUCTURAL_FAILURE":1 if any(v["failure"] for v in s.values()) else None,"TERMINAL":len(r["path"])}
 for j,x in enumerate(r["path"],1):
  hi=float(x["high"]);lo=float(x["low"])
  for z in FAV:
   if lo<=r["ep"]*(1-z):first.setdefault(f"ADV_{z}",j)
   if hi>=r["ep"]*(1+z):first.setdefault(f"FAV_{z}",j)
  if r["atr"]:
   for z in ATR_EVT:
    if lo<=r["ep"]-z*r["atr"]:first.setdefault(f"ADV_ATR_{z}",j)
    if hi>=r["ep"]+z*r["atr"]:first.setdefault(f"FAV_ATR_{z}",j)
 ev=[(t,k) for k,t in first.items() if t is not None]
 mt=min(t for t,k in ev);cand=[k for t,k in ev if t==mt];cand.sort(key=lambda k:(0 if k.startswith("ADV") or k=="STRUCTURAL_FAILURE" else 1,k))
 return {"event":cand[0],"session":mt}
def entry_policy(r,session):
 if session is None or session<1 or session>=len(r["path"]):return None
 px=float(r["path"][session-1]["close"]);tail=r["path"][session:]
 return {"ret":float(tail[-1]["close"])/px-1,"mae":min(float(x["low"]) for x in tail)/px-1,"mfe":max(float(x["high"]) for x in tail)/px-1,"px_delta":px/r["ep"]-1}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--trajectory-dir",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
 rows=load_rows(a.trajectory_dir)
 out={"format":"MTS_V4_DISCOVERY_ADVERSE_PATH_PHASE2_V1","trade_count":len(rows),"ticker_count":67,"verification_a_accessed":False,"verification_b_accessed":False,"search_run":False,"refit":False,"rule_selection":False}
 structs=[structure_for(r) for r in rows];recs=[recovery_stats(r) for r in rows];sts=[states(r,s,rc) for r,s,rc in zip(rows,structs,recs)]
 dims=defaultdict(list)
 for i,r in enumerate(rows):
  d=-r["mae"];t=r["mi"]+1;atn=d*r["ep"]/r["atr"] if r["atr"] else None;rf=max(recs[i]["recs"][:min(4,len(recs[i]["recs"]))]) if recs[i]["recs"] else 0
  bins=[("AE","LT3" if d<.03 else "3_5" if d<.05 else "5_8" if d<.08 else "GE8"),("TIME","LE2" if t<=2 else "3_4" if t<=4 else "5_10" if t<=10 else "GT10"),("REC","LT25" if rf<.25 else "25_50" if rf<.5 else "50_100" if rf<1 else "GE100"),("ATR","MISSING" if atn is None else "LT1" if atn<1 else "1_2" if atn<2 else "2_3" if atn<3 else "GE3"),("FAMILY",r["family"]),("GENOME",r["genome"]),("YEAR",str(r["year"]))]
  for k,v in bins:dims[(k,v)].append(i)
 out["conditional_regimes"]={}
 for (k,v),ix in dims.items():
  out["conditional_regimes"].setdefault(k,{})[v]={"n":len(ix),"tickers":len({rows[j]["ticker"] for j in ix}),"win_rate":mean([rows[j]["winner"] for j in ix]),"expectancy":mean([rows[j]["ret"] for j in ix]),"mae_median":q([-rows[j]["mae"] for j in ix],50),"time_to_mae_median":q([rows[j]["mi"]+1 for j in ix],50)}
 agg=defaultdict(lambda:defaultdict(list))
 for i,r in enumerate(rows):
  lab="WINNER" if r["winner"] else "LOSER"
  for name,v in structs[i].items():
   for f in ("touch","sweep","failure","reclaim"):agg[name][lab+"_"+f].append(v[f])
   agg[name][lab+"_pen"].append(v["max_pen_atr"])
 out["structural_references"]={n:{k:(mean(v) if not k.endswith("_pen") else {"median":q(v,50),"p90":q(v,90)}) for k,v in d.items()} for n,d in agg.items()}
 pats=defaultdict(list)
 for i,r in enumerate(rows):
  s=structs[i];rc=recs[i];af=any(v["failure"] for v in s.values());aw=any(v["sweep"] for v in s.values())
  ps={"P1":rc["causal_low_session"]<=4 and rc["first25"] is not None and not af,
      "P2":rc["first25"] is not None and aw and any(v["reclaim"] and (v["reclaim_session"] or 99)<=3 for v in s.values()),
      "P3":(rc["first25"] is None or rc["first25"]>rc["causal_low_session"]+4) and r["mi"]+1>rc["causal_low_session"],
      "P4":af and not any(v["reclaim"] and (v["reclaim_session"] or 99)<=5 for v in s.values()) and r["mi"]+1>1}
  for nm,ok in ps.items():
   if ok:pats[nm].append(i)
 out["path_patterns"]={k:{"n":len(ix),"tickers":len({rows[j]["ticker"] for j in ix}),"win_rate":mean([rows[j]["winner"] for j in ix]),"expectancy":mean([rows[j]["ret"] for j in ix])} for k,ix in pats.items()}
 tr={"WINNER":Counter(),"LOSER":Counter()};tr2={"WINNER":Counter(),"LOSER":Counter()}
 for r,ss in zip(rows,sts):
  lab="WINNER" if r["winner"] else "LOSER"
  for x,y in zip(ss,ss[1:]):tr[lab][x+"->"+y]+=1
  for x,y in zip(ss,ss[2:]):tr2[lab][x+"->"+y]+=1
 out["state_transitions"]={"one_step":{k:dict(v) for k,v in tr.items()},"two_step":{k:dict(v) for k,v in tr2.items()}}
 cp={"WINNER":[],"LOSER":[]}
 for r in rows:
  prev=r["ep"];xs=[]
  for x in r["path"]:
   c=float(x["close"]);xs.append((c-prev)/r["atr"] if r["atr"] else c/prev-1);prev=c
  cp["WINNER" if r["winner"] else "LOSER"].append(page_hinkley(xs))
 out["change_point"]={k:{"detected_rate":mean([x is not None for x in v]),"median_session":q([x for x in v if x],50),"parameters":{"delta":.005,"lambda":5.0,"alpha":.999}} for k,v in cp.items()}
 races=defaultdict(list)
 for i,r in enumerate(rows):
  e=event_race(r,structs[i],recs[i]);races[e["event"]].append((i,e["session"]))
 out["event_race"]={k:{"n":len(v),"share":len(v)/len(rows),"median_session":q([x[1] for x in v],50),"win_rate":mean([rows[x[0]]["winner"] for x in v])} for k,v in races.items()}
 pols={"REC25":lambda i:recs[i]["first25"],"REC50":lambda i:recs[i]["first50"],"REC75":lambda i:recs[i]["first75"],"REC100":lambda i:recs[i]["first100"],"LOW+1":lambda i:recs[i]["causal_low_session"]+1,"LOW+2":lambda i:recs[i]["causal_low_session"]+2,"LOW+3":lambda i:recs[i]["causal_low_session"]+3,"LOW+4":lambda i:recs[i]["causal_low_session"]+4,"LOW+5":lambda i:recs[i]["causal_low_session"]+5}
 ef={}
 for name,fn in pols.items():
  vals=[];ma=[];mf=[];pd=[]
  for i,r in enumerate(rows):
   x=entry_policy(r,fn(i))
   if x:vals.append(x["ret"]);ma.append(x["mae"]);mf.append(x["mfe"]);pd.append(x["px_delta"])
  ef[name]={"participation":len(vals)/len(rows),"n":len(vals),"economics":econ(vals),"median_entry_delta":q(pd,50),"median_subsequent_mae":q(ma,50),"median_subsequent_mfe":q(mf,50)}
 out["entry_frontier"]=ef
 feats=defaultdict(list);ys=[]
 for i,r in enumerate(rows):
  ys.append(int(r["winner"]))
  for nm,pos in (("state_s2",1),("state_s4",3),("state_s5",4)):feats[nm].append(sts[i][pos] if len(sts[i])>pos else "MISSING")
  feats["recovery25_by5"].append(int(recs[i]["first25"] is not None and recs[i]["first25"]<=5))
  feats["structural_failure"].append(int(any(v["failure"] for v in structs[i].values())))
  feats["structural_sweep"].append(int(any(v["sweep"] for v in structs[i].values())))
 hy=entropy(ys);iv={}
 for k,v in feats.items():
  lab={x:j for j,x in enumerate(sorted(set(v),key=str))};x=[lab[z] for z in v];groups=defaultdict(list)
  for a1,y in zip(x,ys):groups[a1].append(y)
  cond=sum(len(g)/len(ys)*entropy(g) for g in groups.values())
  iv[k]={"mutual_information":float(mutual_info_score(x,ys)),"entropy_reduction_bits":hy-cond,"n":len(ys)}
 out["information_value"]=iv
 matches={}
 for h in HPTS:
  X=[];meta=[]
  for i,r in enumerate(rows):
   if len(r["path"])<h or not r["atr"]:continue
   p=r["path"][:h];scale=r["atr"]/r["ep"];cl=np.array([float(x["close"])/r["ep"]-1 for x in p]);lo=np.array([float(x["low"])/r["ep"]-1 for x in p])
   X.append([cl[-1]/scale,lo.min()/scale,np.sum(np.diff(np.r_[0,cl])>0),recs[i]["recs"][h-1]]);meta.append((i,r["family"],r["ticker"],r["winner"]))
  X=np.asarray(X,float);mu=X.mean(0);sd=X.std(0);sd[sd==0]=1;Z=(X-mu)/sd;pairs=[];used=set()
  by=defaultdict(list)
  for j,m in enumerate(meta):by[(m[1],m[3])].append(j)
  for a1,(i1,f1,t1,w1) in enumerate(meta):
   cand=[j for j in by[(f1,not w1)] if meta[j][2]!=t1]
   if not cand:continue
   j=min(cand,key=lambda z:float(np.linalg.norm(Z[a1]-Z[z])));key=tuple(sorted((a1,j)))
   if key in used:continue
   used.add(key);pairs.append(float(np.linalg.norm(Z[a1]-Z[j])))
  matches[str(h)]={"pairs":len(pairs),"median_distance":q(pairs,50),"p90_distance":q(pairs,90)}
 out["matched_trajectory"]=matches
 out["three_action_framing"]={"ENTER_MAINTAIN":"shallow/early-recovering path without causal structural failure","WAIT_REDUCE":"unresolved path with repeated lower lows or weak recovery absent frozen failure","ABANDON_EXIT":"persistent causal structural failure; no rule nominated"}
 out["unavailable_or_deferred"]={"broad_market_regime":"no pre-existing causal market-regime artifact supplied; omitted rather than invented","compression_geometry":"deferred to dedicated structural runner; not silently approximated","prompt_structural_reclaim_entry":"deferred pending reference-specific causal lineage","controlled_retest_entry":"deferred pending reference-specific causal lineage","change_point_mean_shift":"deferred; Page-Hinkley executed","change_point_vol_ratio":"deferred; Page-Hinkley executed"}
 out["limitations"]=["Discovery only; no optimized result is validation.","Current-S&P calibration universe is survivorship-biased.","Repeated/overlapping trades are dependent; raw N is not effective independent sample size.","No costs were invented; economics are gross where governed costs were unavailable.","Structural states aggregate across prespecified references and are descriptive, not executable."]
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("REPORT="+a.output);print("TRADES=125002 TICKERS=67");print("PATTERNS",json.dumps(out["path_patterns"],sort_keys=True));print("VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False SEARCH_RUN=False REFIT=False RULE_SELECTION=False")
if __name__=="__main__":main()
