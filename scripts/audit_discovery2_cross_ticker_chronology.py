#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,os,statistics
from collections import defaultdict,Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import date,timedelta
from pathlib import Path
from MTS_V4.derived_market_store import DerivedMarketQuery,ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal

FAMS=("MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION","VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL","MARKET_REGIME_STRUCTURE")
G={}

def uniq(r,f):
    seen=set(); out=[]
    for opt in ("random","ga"):
        for c in r["families"][f][opt]["top_candidates"]:
            cid=c["candidate_id"]
            if cid not in seen:
                seen.add(cid); out.append(c)
    return out

def era_bounds(start_s,end_s):
    s=date.fromisoformat(start_s); e=date.fromisoformat(end_s)
    span=(e-s).days+1
    c1=s+timedelta(days=span//3)
    c2=s+timedelta(days=(2*span)//3)
    return [
        ("ERA_1",s,c1-timedelta(days=1)),
        ("ERA_2",c1,c2-timedelta(days=1)),
        ("ERA_3",c2,e),
    ]

def init_worker(cfg,sources,meta,eras):
    G.update(cfg=cfg,sources=sources,meta=meta,eras=eras)

def checkpoint_path(target):
    return Path(G["cfg"]["checkpoint_dir"])/f"{target}.json.gz"

def process_target(target):
    cp=checkpoint_path(target)
    if cp.exists():
        try:
            with gzip.open(cp,"rt") as f:r=json.load(f)
            if r.get("format")=="MTS_V4_DISCOVERY2_CHRONO_TRANSPORT_TARGET_V1" and r.get("target_ticker")==target:
                return target,True,r
        except Exception:
            pass

    cfg=G["cfg"]; m=G["meta"][target]
    report=json.loads(Path(m["report_path"]).read_text())
    store=ParquetDerivedMarketStore(cfg["derived_root"])
    pred=list(store.query(DerivedMarketQuery(
        universe_id=report["universe_id"],
        feature_set_id="mts_market_predictors",
        feature_set_version=report["predictor_feature_set_version"],
        security_ids=(report["security_id"],))))
    pred.sort(key=lambda x:str(x["effective_date"]))
    out=list(store.query(DerivedMarketQuery(
        universe_id=report["universe_id"],
        feature_set_id="mts_historical_outcomes",
        feature_set_version=report["outcome_feature_set_version"],
        security_ids=(report["security_id"],))))
    oi={(str(x["security_id"]),str(x["effective_date"])):x for x in out}

    baselines={}
    for h in sorted({int(c["genome"]["forward_horizon"]) for f in FAMS for _,c in G["sources"][f]}):
        col=f"forward_return_{h}__v1"
        for en,es,ee in G["eras"]:
            vals=[float(o[col]) for o in out if o.get(col) is not None and es <= date.fromisoformat(str(o["effective_date"])[:10]) <= ee]
            baselines[(h,en)] = (statistics.fmean(vals),statistics.median(vals),len(vals)) if vals else (None,None,0)

    rows=[]
    for f in FAMS:
        for src,c in G["sources"][f]:
            if src==target: continue
            h=int(c["genome"]["forward_horizon"]); col=f"forward_return_{h}__v1"
            sig=_compile_signal(pred,c)
            byera=defaultdict(list)
            for pr,on in zip(pred,sig):
                if not on: continue
                ds=str(pr["effective_date"])[:10]; d=date.fromisoformat(ds)
                en=None
                for name,es,ee in G["eras"]:
                    if es<=d<=ee: en=name; break
                if en is None: continue
                o=oi.get((str(pr["security_id"]),str(pr["effective_date"])))
                if o is not None and o.get(col) is not None: byera[en].append(float(o[col]))
            ers=[]
            for name,es,ee in G["eras"]:
                vals=byera.get(name,[]); bm,bmed,bn=baselines[(h,name)]
                usable=len(vals)>=10 and bm is not None
                em=(statistics.fmean(vals)-bm) if usable else None
                ed=(statistics.median(vals)-bmed) if usable else None
                ers.append({"era":name,"n":len(vals),"baseline_n":bn,"usable":usable,
                            "excess_mean":em,"excess_median":ed,
                            "positive_both":bool(usable and em>0 and ed>0)})
            rows.append({"source_ticker":src,"family":f,"candidate_id":c["candidate_id"],"horizon":h,"eras":ers})

    result={"format":"MTS_V4_DISCOVERY2_CHRONO_TRANSPORT_TARGET_V1","target_ticker":target,
            "cohort":m["cohort"],"eras":[{"name":n,"start":str(s),"end":str(e)} for n,s,e in G["eras"]],
            "rows":rows,"verification_accessed":False,"sol_calls":0}
    cp.parent.mkdir(parents=True,exist_ok=True)
    tmp=cp.with_suffix(cp.suffix+".tmp")
    with gzip.open(tmp,"wt",compresslevel=6) as f: json.dump(result,f,separators=(",",":"))
    os.replace(tmp,cp)
    return target,False,result

def main():
    p=argparse.ArgumentParser()
    for x in ("d2-dir","d2b-dir","d2-classification","d2b-manifest","derived-market-root","output","checkpoint-dir"):
        p.add_argument("--"+x,required=True)
    p.add_argument("--workers",type=int,default=8)
    p.add_argument("--start-date",default="2006-09-15")
    p.add_argument("--end-date",default="2026-09-14")
    a=p.parse_args()

    meta={}
    d2c=json.loads(Path(a.d2_classification).read_text())
    for x in d2c["tickers"]:
        t=x["ticker"]; meta[t]={"cohort":"D2_50","report_path":str(Path(a.d2_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}
    d2b=json.loads(Path(a.d2b_manifest).read_text())
    for x in d2b["tickers"]:
        t=x["ticker"]; meta[t]={"cohort":"D2B_SUPPLEMENT","report_path":str(Path(a.d2b_dir)/f"{t}_COMPUTATIONAL_SEARCH_20260930.json")}

    sources=defaultdict(list)
    for t,m in sorted(meta.items()):
        r=json.loads(Path(m["report_path"]).read_text())
        for f in FAMS:
            for c in uniq(r,f): sources[f].append((t,c))

    eras=era_bounds(a.start_date,a.end_date)
    cfg={"derived_root":a.derived_market_root,"checkpoint_dir":a.checkpoint_dir}
    completed=[]
    with ProcessPoolExecutor(max_workers=a.workers,initializer=init_worker,initargs=(cfg,dict(sources),meta,eras)) as ex:
        futs={ex.submit(process_target,t):t for t in sorted(meta)}
        done=0
        for fut in as_completed(futs):
            t,reused,r=fut.result(); done+=1; completed.append(r)
            print(f"[{done}/{len(meta)}] {'RESUMED' if reused else 'COMPLETE'}={t}",flush=True)

    fam=defaultdict(lambda:{"era":defaultdict(lambda:Counter()),"all3":0,"usable_all3":0,
                            "two_plus":0,"usable_two_plus":0,"source":defaultdict(lambda:Counter()),
                            "target":defaultdict(lambda:Counter()),"excess_mean":defaultdict(list),
                            "excess_median":defaultdict(list),"rows":0})
    for tr in completed:
        target=tr["target_ticker"]
        for row in tr["rows"]:
            z=fam[row["family"]]; z["rows"]+=1
            usable=[e for e in row["eras"] if e["usable"]]
            good=[e for e in usable if e["positive_both"]]
            for e in row["eras"]:
                if e["usable"]:
                    z["era"][e["era"]]["usable"]+=1
                    z["excess_mean"][e["era"]].append(e["excess_mean"])
                    z["excess_median"][e["era"]].append(e["excess_median"])
                    z["source"][row["source_ticker"]]["usable"]+=1
                    z["target"][target]["usable"]+=1
                    if e["positive_both"]:
                        z["era"][e["era"]]["positive"]+=1
                        z["source"][row["source_ticker"]]["positive"]+=1
                        z["target"][target]["positive"]+=1
            if len(usable)==3:
                z["usable_all3"]+=1
                if len(good)==3:z["all3"]+=1
            if len(usable)>=2:
                z["usable_two_plus"]+=1
                if len(good)>=2:z["two_plus"]+=1

    summaries=[]
    for f in FAMS:
        z=fam[f]
        er=[]
        for name,_,__ in eras:
            c=z["era"][name]; u=c["usable"]; q=c["positive"]
            er.append({"era":name,"usable":u,"positive_both":q,"fraction":q/u if u else None,
                       "median_excess_mean":statistics.median(z["excess_mean"][name]) if z["excess_mean"][name] else None,
                       "median_excess_median":statistics.median(z["excess_median"][name]) if z["excess_median"][name] else None})
        summaries.append({"family":f,"eras":er,"usable_all3":z["usable_all3"],"positive_all3":z["all3"],
                          "all3_fraction":z["all3"]/z["usable_all3"] if z["usable_all3"] else None,
                          "usable_at_least2":z["usable_two_plus"],"positive_at_least2":z["two_plus"],
                          "at_least2_fraction":z["two_plus"]/z["usable_two_plus"] if z["usable_two_plus"] else None,
                          "positive_target_breadth":sum(1 for c in z["target"].values() if c["positive"]>0),
                          "usable_target_breadth":sum(1 for c in z["target"].values() if c["usable"]>0),
                          "positive_source_breadth":sum(1 for c in z["source"].values() if c["positive"]>0),
                          "usable_source_breadth":sum(1 for c in z["source"].values() if c["usable"]>0)})

    result={"format":"MTS_V4_DISCOVERY2_CROSS_TICKER_CHRONOLOGY_AUDIT_V1",
            "scientific_boundary":"DISCOVERY_INTERNAL_TRANSPORT_CHRONOLOGY_NOT_VERIFICATION",
            "methodology":{"exact_saved_genomes":True,"self_transport_excluded":True,"new_search":False,
                           "new_genomes":False,"refit":False,"winner_selection":False,
                           "calendar_cutpoints_fixed_globally":True,
                           "baseline":"target ticker unconditional same horizon inside same fixed calendar era",
                           "usable_n_min_per_era":10,
                           "positive_both_definition":"era excess mean >0 and era excess median >0",
                           "workers":a.workers,"checkpointed_per_target_gzip":True},
            "eras":[{"name":n,"start":str(s),"end":str(e)} for n,s,e in eras],
            "family_summary":summaries,"checkpoint_dir":a.checkpoint_dir,
            "verification_accessed":False,"sol_calls":0}
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(f"REPORT={a.output}")
    print("ERAS="+" | ".join(f"{n}:{s}..{e}" for n,s,e in eras))
    for s in sorted(summaries,key=lambda q:(-(q["all3_fraction"] if q["all3_fraction"] is not None else -1),q["family"])):
        ae=s["all3_fraction"]
        print(f"{s['family']}: all3={s['positive_all3']}/{s['usable_all3']} fraction={(ae if ae is not None else 0):.3f} "
              f"2plus={s['positive_at_least2']}/{s['usable_at_least2']} fraction={(s['at_least2_fraction'] or 0):.3f} "
              f"targets={s['positive_target_breadth']}/{s['usable_target_breadth']} sources={s['positive_source_breadth']}/{s['usable_source_breadth']}")
        print("  "+ " ".join(f"{e['era']}={e['positive_both']}/{e['usable']}({(e['fraction'] or 0):.3f}) medMean={(e['median_excess_mean'] or 0):.6f} medMedian={(e['median_excess_median'] or 0):.6f}" for e in s["eras"]))
    print("SELF_TRANSPORT=False"); print("WINNER_SELECTION=False"); print("VERIFICATION_ACCESSED=False"); print("SOL_CALLS=0")
if __name__=="__main__": main()
