"""Observed OHLC emergency-cap replay, including executable gap-through fills.

Per-security adjusted OHLC, decision-T ATR20, next-open entry, 63-session
maximum holding period. All frozen sensitivity thresholds are evaluated.
"""
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from .ga4_gap_fill import emergency_exit
from .stage2_path_v3 import _adjusted_ohlc
from .stage2_data_v3 import sha256_file

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"Research/Runs/layered/stage2-opportunity-v3-20261007"
POLICY=ROOT/"Research/Design/MTS_STAGE2_V3_CATASTROPHIC_POLICY_FREEZE_20261007.json"

def replay(raw,policy,max_horizon=63):
    cuts=[("fraction",float(x)) for x in policy["thresholds"]["loss_fraction_sensitivity"]]
    cuts += [("atr20",float(x)) for x in policy["thresholds"]["atr20_sensitivity"]]
    results={}
    for side in ("LONG","SHORT"):
        for kind,threshold in cuts:
            results[f"{side}:{kind}:{threshold:g}"]={"eligible":0,"breached":0,"gap_fills":0,"intraday_fills":0,
                "sum_realized_gross_return":0.,"sum_uncapped_gross_return":0.,"gap_loss_worse_than_stop":0}
    for _,g0 in raw.groupby("security_id",sort=False):
        g=g0.sort_values("date")
        o,h,l,_=_adjusted_ohlc(g)
        adjclose=g["adj_close"].to_numpy(float)
        prev=np.r_[np.nan,adjclose[:-1]]
        tr=np.maximum.reduce([h-l,np.abs(h-prev),np.abs(l-prev)])
        atr=pd.Series(tr).rolling(20,min_periods=20).mean().to_numpy()
        n=len(g)
        for decision in range(20,n-65):
            entry=float(o[decision+1]);exitopen=float(o[decision+64])
            if not np.isfinite(entry) or entry<=0 or not np.isfinite(exitopen) or exitopen<=0:continue
            bars=[]
            valid=True
            for k in range(decision+1,decision+64):
                if not np.isfinite(o[k]) or not np.isfinite(h[k]) or not np.isfinite(l[k]) or l[k]>o[k] or o[k]>h[k]:
                    valid=False;break
                bars.append({"open":o[k],"high":h[k],"low":l[k]})
            if not valid:continue
            for side in ("LONG","SHORT"):
                sign=1 if side=="LONG" else -1
                uncapped=sign*(exitopen/entry-1)
                for kind,threshold in cuts:
                    if kind=="atr20":
                        if not np.isfinite(atr[decision]) or atr[decision]<=0:continue
                        distance=threshold*atr[decision]
                    else:distance=threshold*entry
                    stop=entry-sign*distance
                    if stop<=0:continue
                    rec=results[f"{side}:{kind}:{threshold:g}"]
                    rec["eligible"]+=1
                    fill=emergency_exit(side,entry,stop,bars)
                    rec["sum_uncapped_gross_return"]+=uncapped
                    if fill is None:
                        rec["sum_realized_gross_return"]+=uncapped
                    else:
                        rec["breached"]+=1
                        rec["sum_realized_gross_return"]+=fill["return"]
                        if fill["type"]=="GAP_THROUGH":
                            rec["gap_fills"]+=1
                            if (side=="LONG" and fill["fill"]<stop) or (side=="SHORT" and fill["fill"]>stop):
                                rec["gap_loss_worse_than_stop"]+=1
                        else:rec["intraday_fills"]+=1
    for rec in results.values():
        n=rec["eligible"]
        rec["uncapped_mean_gross"]=rec["sum_uncapped_gross_return"]/n if n else None
        rec["capped_mean_gross"]=rec["sum_realized_gross_return"]/n if n else None
    return results

def main():
    policy=json.loads(POLICY.read_text())
    src=ROOT/policy["provenance"]["source"]
    if sha256_file(src)!=policy["provenance"]["source_sha256"]:raise ValueError("source mismatch")
    raw=pd.read_parquet(BASE/"cache/dev117_raw_aligned_v3.parquet")
    result={"policy_hash":policy["policy_hash"],"source_hash_verified":True,
            "raw_sha256":sha256_file(BASE/"cache/dev117_raw_aligned_v3.parquet"),
            "max_horizon":63,"results":replay(raw,policy),
            "independently_verified":False,
            "limitations":["Gross return replay; frozen causal roundtrip costs not yet applied to stopped trades",
                           "Independent external recalculation and candidate-level certification pending"]}
    dest=BASE/"calibration/ga4_observed_stop_replay.json"
    dest.write_text(json.dumps(result,indent=2,allow_nan=False))
    print("OBSERVED_STOP_REPLAY",len(result["results"]),dest)
if __name__=="__main__":main()
