#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
CONT=("close_vs_ref","sma10_distance","sma10_slope5","sma20_distance","sma20_slope5","sma50_distance","sma50_slope5","ema20_distance","ema20_slope5","atr14","ref_distance_atr","rsi14","volume_vs_mean20","prior_low_5_distance","prior_low_10_distance","prior_low_20_distance","lower_wick_fraction","body_fraction","realized_vol20")
BOOL=("prior_low_5_swept","prior_low_5_reclaimed","prior_low_10_swept","prior_low_10_reclaimed","prior_low_20_swept","prior_low_20_reclaimed","swing10_swept","swing10_reclaimed")
DEPTHS=(.01,.02,.03,.05,.075,.10)
def pct(a,p):
 if not a:return None
 s=sorted(a);x=(len(s)-1)*p;lo=int(x);hi=min(lo+1,len(s)-1);return s[lo]+(s[hi]-s[lo])*(x-lo)
def stats(a):
 a=[float(x) for x in a if x is not None and math.isfinite(float(x))]
 return {"n":len(a),"mean":statistics.fmean(a) if a else None,"median":statistics.median(a) if a else None,"p25":pct(a,.25),"p75":pct(a,.75)}
def auc(a,b):
 a=sorted(float(x) for x in a if x is not None and math.isfinite(float(x)));b=sorted(float(x) for x in b if x is not None and math.isfinite(float(x)))
 if not a or not b:return None
 import bisect
 score=0
 for x in a:
  l=bisect.bisect_left(b,x);r=bisect.bisect_right(b,x);score+=l+.5*(r-l)
 z=score/(len(a)*len(b));return z
def compare(rows,feature_key="reclaim_features"):
 groups=defaultdict(list)
 for r in rows:
  if r.get("mae",0)>=0:continue
  if r.get("reclaim_entry") is None:g="NO_CONFIRMED_RECLAIM"
  elif r.get("reclaim_win"):g="CONFIRMED_RECLAIM_WIN"
  else:g="CONFIRMED_RECLAIM_LOSS"
  f=r.get(feature_key) or {}
  groups[g].append((r,f))
 out={"group_sizes":{g:len(v) for g,v in groups.items()},"continuous":{},"boolean":{}}
 pairs=(("CONFIRMED_RECLAIM_WIN","CONFIRMED_RECLAIM_LOSS"),("CONFIRMED_RECLAIM_WIN","NO_CONFIRMED_RECLAIM"),("CONFIRMED_RECLAIM_LOSS","NO_CONFIRMED_RECLAIM"))
 for k in CONT:
  gs={g:stats([f.get(k) for _,f in v]) for g,v in groups.items()};cs={}
  for a,b in pairs:
   av=[f.get(k) for _,f in groups.get(a,[]) if f.get(k) is not None];bv=[f.get(k) for _,f in groups.get(b,[]) if f.get(k) is not None]
   sa,sb=gs.get(a,{}),gs.get(b,{})
   iqs=[x for x in ((sa.get("p75")-sa.get("p25")) if sa.get("p75") is not None else None,(sb.get("p75")-sb.get("p25")) if sb.get("p75") is not None else None) if x and x>0]
   den=statistics.fmean(iqs) if iqs else None;md=(sa.get("median")-sb.get("median")) if sa.get("median") is not None and sb.get("median") is not None else None
   z=auc(av,bv);cs[a+"__VS__"+b]={"median_diff":md,"median_diff_over_pooled_iqr":(md/den if (md is not None and den) else None),"auc":z,"auc_separation":abs(z-.5)*2 if z is not None else None}
  out["continuous"][k]={"groups":gs,"comparisons":cs}
 for k in BOOL:
  gs={}
  for g,v in groups.items():
   x=[bool(f[k]) for _,f in v if k in f];gs[g]={"n":len(x),"prevalence":sum(x)/len(x) if x else None}
  cs={}
  for a,b in pairs:
   x=gs.get(a,{}).get("prevalence");y=gs.get(b,{}).get("prevalence");cs[a+"__VS__"+b]={"percentage_point_diff":x-y if x is not None and y is not None else None}
  out["boolean"][k]={"groups":gs,"comparisons":cs}
 return out
def depth_compare(rows,d):
 rr=[]
 for r in rows:
  ev=next((e for e in r.get("depth_events",[]) if abs(float(e["depth"])-d)<1e-12),None)
  if not ev:continue
  q=dict(r);q["reclaim_features"]=ev.get("observation_features") or {}
  if ev.get("confirmation_entry") is None:q["reclaim_entry"]=None;q["reclaim_win"]=False
  else:q["reclaim_entry"]=ev["confirmation_entry"];q["reclaim_win"]=bool(ev.get("confirmation_win"))
  rr.append(q)
 return compare(rr)
def main():
 p=argparse.ArgumentParser();p.add_argument("--checkpoint-dir",required=True);p.add_argument("--output",required=True);a=p.parse_args()
 files=sorted(Path(a.checkpoint_dir).glob("*.json.gz"))
 if len(files)!=67:raise RuntimeError(f"expected 67 checkpoints, got {len(files)}")
 rows=[]
 for f in files:
  with gzip.open(f,"rt") as h:z=json.load(h)
  if z.get("verification_a_accessed") or z.get("verification_b_accessed"):raise RuntimeError("verification contamination")
  rows.extend(z["rows"])
 overall=compare(rows);depth={str(d):depth_compare(rows,d) for d in DEPTHS}
 # breadth: per ticker/family group counts, not inferential tests
 breadth={}
 for dim in ("ticker","family"):
  x={}
  for val in sorted(set(r[dim] for r in rows)):
   q=compare([r for r in rows if r[dim]==val]);x[val]=q["group_sizes"]
  breadth[dim]=x
 out={"format":"MTS_V4_DISCOVERY_RECOVERY_DISCRIMINATOR_V1","trade_rows":len(rows),"overall":overall,"by_ae_depth":depth,"breadth_group_counts":breadth,
      "search_run":False,"refit":False,"rule_selection":False,"verification_a_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("REPORT="+a.output);print("TRADES="+str(len(rows))+" GROUPS="+json.dumps(overall["group_sizes"],sort_keys=True))
 key="CONFIRMED_RECLAIM_WIN__VS__CONFIRMED_RECLAIM_LOSS"
 cr=[]
 for k,v in overall["continuous"].items():
  c=v["comparisons"].get(key,{})
  if c.get("auc_separation") is not None:cr.append((c["auc_separation"],k,c.get("auc"),c.get("median_diff_over_pooled_iqr")))
 print("TOP_CONTINUOUS_WIN_VS_LOSS")
 for sep,k,au,iq in sorted(cr,reverse=True)[:8]:print(f"{k}: auc={au:.3f} sep={sep:.3f} med/IQR={(iq or 0):.3f}")
 br=[]
 for k,v in overall["boolean"].items():
  d=v["comparisons"].get(key,{}).get("percentage_point_diff")
  if d is not None:br.append((abs(d),k,d))
 print("TOP_BOOLEAN_WIN_VS_LOSS")
 for _,k,d in sorted(br,reverse=True)[:8]:print(f"{k}: prevalence_diff={d:+.3f}")
 print("DEPTH_GROUP_SIZES")
 for d,z in depth.items():print(f"AE={float(d):.1%} "+json.dumps(z["group_sizes"],sort_keys=True))
 print("SEARCH_RUN=False REFIT=False RULE_SELECTION=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False SOL_CALLS=0")
if __name__=="__main__":main()
