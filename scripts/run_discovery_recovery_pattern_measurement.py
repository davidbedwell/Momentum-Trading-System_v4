#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,os,statistics
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal
FAMS=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
DEPTHS=(.01,.02,.03,.05,.075,.10);G={}
def uniq(r,f):
 s=set();z=[]
 for o in ("random","ga"):
  for c in r["families"][f][o]["top_candidates"]:
   if c["candidate_id"] not in s:s.add(c["candidate_id"]);z.append(c)
 return z
def sma(c,i,n):return statistics.fmean(c[i-n+1:i+1]) if i>=n-1 else None
def ema_series(x,n):
 a=2/(n+1);z=[];v=None
 for q in x:v=q if v is None else a*q+(1-a)*v;z.append(v)
 return z
def rsi_series(c,n=14):
 out=[None]*len(c);g=[];l=[]
 for i in range(1,len(c)):
  d=c[i]-c[i-1];g.append(max(d,0));l.append(max(-d,0))
  if i>=n:
   ag=statistics.fmean(g[i-n:i]);al=statistics.fmean(l[i-n:i]);out[i]=100 if al==0 else 100-100/(1+ag/al)
 return out
def atr_series(b,n=14):
 tr=[]
 for i,x in enumerate(b):
  pc=float(b[i-1]["close"]) if i else float(x["close"]);tr.append(max(float(x["high"])-float(x["low"]),abs(float(x["high"])-pc),abs(float(x["low"])-pc)))
 return [statistics.fmean(tr[max(0,i-n+1):i+1]) if i>=n-1 else None for i in range(len(b))]
def rv(c,i,n=20):
 if i<n:return None
 r=[math.log(c[j]/c[j-1]) for j in range(i-n+1,i+1) if c[j-1]>0 and c[j]>0]
 return statistics.pstdev(r)*math.sqrt(252) if len(r)>1 else None
def feature(b,c,v,ema,atr,rsi,i,ref):
 x=b[i];cl=c[i];hi=float(x["high"]);lo=float(x["low"]);op=float(x["open"]);rng=max(hi-lo,1e-12)
 d={"close_vs_ref":cl/ref-1,"lower_wick_fraction":(min(op,cl)-lo)/rng,"body_fraction":abs(cl-op)/rng,"realized_vol20":rv(c,i)}
 for n in (10,20,50):
  m=sma(c,i,n);prev=sma(c,i-5,n) if i>=5 else None
  d[f"sma{n}_distance"]=cl/m-1 if m else None;d[f"sma{n}_slope5"]=m/prev-1 if m and prev else None
 d["ema20_distance"]=cl/ema[i]-1 if ema[i] else None;d["ema20_slope5"]=ema[i]/ema[i-5]-1 if i>=5 and ema[i-5] else None
 d["atr14"]=atr[i];d["ref_distance_atr"]=(cl-ref)/atr[i] if atr[i] else None;d["rsi14"]=rsi[i]
 vm=statistics.fmean(v[i-19:i+1]) if i>=19 else None;d["volume_vs_mean20"]=v[i]/vm if vm else None
 for n in (5,10,20):
  pl=min(float(q["low"]) for q in b[max(0,i-n):i]) if i>0 else None
  d[f"prior_low_{n}_distance"]=lo/pl-1 if pl else None;d[f"prior_low_{n}_swept"]=bool(pl and lo<pl);d[f"prior_low_{n}_reclaimed"]=bool(pl and lo<pl and cl>=pl)
 pl=min(float(q["low"]) for q in b[max(0,i-10):i]) if i>0 else None
 d["swing10_swept"]=bool(pl and lo<pl);d["swing10_reclaimed"]=bool(pl and lo<pl and cl>=pl)
 return d
def accepted(sig,h):
 z=[];n=0
 for i,on in enumerate(sig):
  if on and i>=n:z.append(i);n=i+h
 return z
def init(cfg,meta):G.update(cfg=cfg,meta=meta)
def cp(t):return Path(G["cfg"]["checkpoint"])/f"{t}.json.gz"
def process(t):
 p=cp(t)
 if p.exists():
  try:
   with gzip.open(p,"rt") as f:r=json.load(f)
   if r.get("format")=="MTS_V4_RECOVERY_PATTERN_TARGET_V1":return t,True,r
  except:pass
 m=G["meta"][t];sr=json.loads(Path(m["report"]).read_text());store=ParquetDerivedMarketStore(G["cfg"]["root"])
 pred=list(store.query(DerivedMarketQuery(universe_id=sr["universe_id"],feature_set_id="mts_market_predictors",feature_set_version=sr["predictor_feature_set_version"],security_ids=(sr["security_id"],))));pred.sort(key=lambda x:str(x["effective_date"]))
 pd=[str(x["effective_date"])[:10] for x in pred];bars=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=pd[0],end_date=pd[-1]));bars.sort(key=lambda x:str(x["date"]));bd={str(x["date"])[:10]:i for i,x in enumerate(bars)}
 c=[float(x["close"]) for x in bars];v=[float(x["volume"]) for x in bars];em=ema_series(c,20);at=atr_series(bars);rs=rsi_series(c);rows=[]
 for fam in FAMS:
  for cand in uniq(sr,fam):
   h=int(cand["genome"]["forward_horizon"])
   for pi in accepted(_compile_signal(pred,cand),h):
    ri=bd.get(pd[pi])
    if ri is None or ri+1>=len(bars) or ri+h>=len(bars):continue
    ei=ri+1;xi=ri+h
    if xi<=ei:continue
    ref=float(bars[ei]["open"]);exitp=float(bars[xi]["close"]);path=bars[ei:xi+1]
    lows=[float(x["low"])/ref-1 for x in path];mi=min(range(len(lows)),key=lambda j:lows[j]);mae=lows[mi]
    base={"ticker":t,"cohort":m["cohort"],"family":fam,"candidate_id":cand["candidate_id"],"horizon":h,"signal_date":pd[pi],"reference":ref,"mae":mae,"mae_offset":mi,"terminal_return":exitp/ref-1}
    events=[]
    for dep in DEPTHS:
     di=next((j for j,q in enumerate(lows) if q<=-dep),None)
     if di is None:continue
     reclaim=next((j for j in range(di+1,len(path)) if float(path[j]["close"])>=ref),None)
     entryj=reclaim+1 if reclaim is not None and reclaim+1<len(path) else None
     ev={"depth":dep,"depth_offset":di,"reclaim_offset":reclaim,"confirmed_entry_offset":entryj}
     obs=(ei+reclaim) if reclaim is not None else (ei+di)
     ev["observation_features"]=feature(bars,c,v,em,at,rs,obs,ref)
     if entryj is not None:
      ep=float(path[entryj]["open"]);post=path[entryj:];ev.update({"confirmation_entry":ep,"confirmation_terminal_return":exitp/ep-1,
       "confirmation_win":exitp>ep,"post_entry_mae":min(float(q["low"])/ep-1 for q in post),"post_entry_mfe":max(float(q["high"])/ep-1 for q in post)})
     events.append(ev)
    any_di=next((j for j,q in enumerate(lows) if q<0),None);reclaim=None
    if any_di is not None:reclaim=next((j for j in range(any_di+1,len(path)) if float(path[j]["close"])>=ref),None)
    base["any_ae_reclaim_offset"]=reclaim;base["any_ae_confirmed_entry_offset"]=(reclaim+1 if reclaim is not None and reclaim+1<len(path) else None)
    if reclaim is not None:
     base["reclaim_features"]=feature(bars,c,v,em,at,rs,ei+reclaim,ref)
     if reclaim+1<len(path):
      ep=float(path[reclaim+1]["open"]);post=path[reclaim+1:];base.update({"reclaim_entry":ep,"reclaim_terminal_return":exitp/ep-1,"reclaim_win":exitp>ep,
       "reclaim_post_mae":min(float(q["low"])/ep-1 for q in post),"reclaim_post_mfe":max(float(q["high"])/ep-1 for q in post)})
    base["depth_events"]=events;rows.append(base)
 out={"format":"MTS_V4_RECOVERY_PATTERN_TARGET_V1","ticker":t,"rows":rows,"verification_a_accessed":False,"verification_b_accessed":False,"search_run":False,"refit":False}
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(".tmp.gz")
 with gzip.open(tmp,"wt") as f:json.dump(out,f,separators=(",",":"))
 os.replace(tmp,p);return t,False,out
def main():
 a=argparse.ArgumentParser()
 for x in ("protocol","d2-dir","d2b-dir","d2-classification","d2b-manifest","derived-market-root","checkpoint-dir","output"):a.add_argument("--"+x,required=True)
 a.add_argument("--workers",type=int,default=8);q=a.parse_args();meta={}
 for x in json.loads(Path(q.d2_classification).read_text())["tickers"]:
  t=x["ticker"];meta[t]={"cohort":"D2_50","report":str(Path(q.d2_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}
 for x in json.loads(Path(q.d2b_manifest).read_text())["tickers"]:
  t=x["ticker"];meta[t]={"cohort":"D2B_SUPPLEMENT","report":str(Path(q.d2b_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}
 if len(meta)!=67:raise RuntimeError(len(meta))
 cfg={"root":q.derived_market_root,"checkpoint":q.checkpoint_dir};allr=[]
 with ProcessPoolExecutor(max_workers=q.workers,initializer=init,initargs=(cfg,meta)) as ex:
  fs={ex.submit(process,t):t for t in sorted(meta)}
  for n,f in enumerate(as_completed(fs),1):
   t,reused,r=f.result();allr.extend(r["rows"]);print(f"[{n}/67] {'RESUMED' if reused else 'COMPLETE'}={t}",flush=True)
 def bench(rows):
  eligible=[r for r in rows if r["mae"]<0];conf=[r for r in eligible if r.get("reclaim_entry") is not None]
  ow=sum(r["terminal_return"]>0 for r in eligible);cw=sum(r["reclaim_win"] for r in conf)
  return {"eligible":len(eligible),"confirmed":len(conf),"confirmation_rate":len(conf)/len(eligible) if eligible else None,
   "original_win_rate":ow/len(eligible) if eligible else None,"confirmed_win_rate":cw/len(conf) if conf else None,
   "original_winners_filtered":sum(r["terminal_return"]>0 and r.get("reclaim_entry") is None for r in eligible),
   "original_losers_filtered":sum(r["terminal_return"]<=0 and r.get("reclaim_entry") is None for r in eligible),
   "confirmed_mean_return":statistics.fmean(r["reclaim_terminal_return"] for r in conf) if conf else None,
   "confirmed_median_return":statistics.median(r["reclaim_terminal_return"] for r in conf) if conf else None}
 byfam={f:bench([r for r in allr if r["family"]==f]) for f in FAMS};depth={}
 for d in DEPTHS:
  ev=[]
  for r in allr:
   z=next((e for e in r["depth_events"] if e["depth"]==d),None)
   if z:ev.append((r,z))
  conf=[(r,z) for r,z in ev if z.get("confirmation_entry") is not None]
  depth[str(d)]={"reached":len(ev),"confirmed":len(conf),"confirmation_rate":len(conf)/len(ev) if ev else None,
   "confirmed_win_rate":sum(z.get("confirmation_win",False) for r,z in conf)/len(conf) if conf else None,
   "confirmed_mean_return":statistics.fmean(z["confirmation_terminal_return"] for r,z in conf) if conf else None}
 result={"format":"MTS_V4_DISCOVERY_RECOVERY_PATTERN_SUMMARY_V1","protocol_sha256":hashlib.sha256(Path(q.protocol).read_bytes()).hexdigest(),
  "ticker_count":67,"trade_count":len(allr),"benchmark":bench(allr),"depth_reclaim":depth,"family_benchmark":byfam,
  "detail_location":q.checkpoint_dir,"search_run":False,"refit":False,"winner_selection":False,"verification_a_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 Path(q.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");b=result["benchmark"]
 print("REPORT="+q.output);print(f"TRADES={len(allr)} ANY_AE={b['eligible']} CONFIRMED_RECLAIM={b['confirmed']} RATE={b['confirmation_rate']:.3f}")
 print(f"ORIGINAL_WIN_RATE={b['original_win_rate']:.3f} RECLAIM_WIN_RATE={b['confirmed_win_rate']:.3f} FILTERED_WINNERS={b['original_winners_filtered']} FILTERED_LOSERS={b['original_losers_filtered']} CONF_MEAN_RET={b['confirmed_mean_return']:.6f} CONF_MED_RET={b['confirmed_median_return']:.6f}")
 for d,z in depth.items():print(f"AE={float(d):.1%} reached={z['reached']} confirmed={z['confirmed']} rate={(z['confirmation_rate'] or 0):.3f} win={(z['confirmed_win_rate'] or 0):.3f} meanRet={(z['confirmed_mean_return'] or 0):.6f}")
 print("DETAILS=PER_TICKER_GZIP_CHECKPOINTS");print("SEARCH_RUN=False REFIT=False WINNER_SELECTION=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False SOL_CALLS=0")
if __name__=="__main__":main()
