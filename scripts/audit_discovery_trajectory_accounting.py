#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,statistics
from pathlib import Path
def load(p):
 with gzip.open(p,"rt") as f:return json.load(f)
def main():
 a=argparse.ArgumentParser();a.add_argument("--recovery-dir",required=True);a.add_argument("--trajectory-dir",required=True);a.add_argument("--output",required=True);q=a.parse_args()
 rd={p.stem.replace(".json",""):load(p) for p in Path(q.recovery_dir).glob("*.json.gz")}
 td={p.stem.replace(".json",""):load(p) for p in Path(q.trajectory_dir).glob("*.json.gz")}
 common=sorted(set(rd)&set(td));missing_r=sorted(set(td)-set(rd));missing_t=sorted(set(rd)-set(td))
 per=[];R=T=0
 for t in common:
  r=rd[t]["rows"];z=td[t]["rows"];R+=len(r);T+=len(z)
  rk={(x["family"],x["candidate_id"],x["signal_date"],int(x["horizon"])) for x in r};tk={(x["family"],x["candidate_id"],x["signal_date"],int(x["horizon"])) for x in z}
  per.append({"ticker":t,"recovery_rows":len(r),"trajectory_rows":len(z),"recovery_only":len(rk-tk),"trajectory_only":len(tk-rk)})
 # Recompute winner-filter accounting correctly: eligible winners minus confirmed winners, independent of whether confirmed trade remains a winner.
 cells=[]
 for dep in (.01,.02,.03,.05,.075,.10):
  for frac in (.25,.5,.75,1.0):
   elig=[];conf=[]
   for t in common:
    for row in td[t]["rows"]:
     c=next((x for x in row["cells"] if x["depth"]==dep and x["recovery_fraction"]==frac),None)
     if c and c["eligible"]:
      elig.append(c)
      if c.get("entry") is not None:conf.append(c)
   ew=sum(c["original_terminal_return"]>0 for c in elig);el=len(elig)-ew
   cw=sum(c["original_terminal_return"]>0 for c in conf);cl=len(conf)-cw
   cells.append({"depth":dep,"recovery_fraction":frac,"eligible":len(elig),"confirmed":len(conf),
    "original_winners_filtered":ew-cw,"original_losers_filtered":el-cl})
 out={"format":"MTS_V4_TRAJECTORY_AUDIT_V1","common_tickers":len(common),"missing_recovery":missing_r,"missing_trajectory":missing_t,
      "recovery_rows":R,"trajectory_rows":T,"row_delta":R-T,"per_ticker":per,"corrected_filter_accounting":cells}
 Path(q.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(f"RECOVERY_ROWS={R} TRAJECTORY_ROWS={T} DELTA={R-T} COMMON_TICKERS={len(common)}")
 bad=[x for x in per if x["recovery_only"] or x["trajectory_only"]]
 print(f"TICKERS_WITH_KEY_MISMATCH={len(bad)}")
 for x in sorted(bad,key=lambda y:y["recovery_only"]+y["trajectory_only"],reverse=True)[:15]:print(f"{x['ticker']} recovery={x['recovery_rows']} trajectory={x['trajectory_rows']} recoveryOnly={x['recovery_only']} trajectoryOnly={x['trajectory_only']}")
 print("FILTER_ACCOUNTING_AUDIT")
 for x in cells:print(f"AE={x['depth']:.1%} REC={x['recovery_fraction']:.0%} filtW={x['original_winners_filtered']} filtL={x['original_losers_filtered']}")
 print("REPORT="+q.output)
if __name__=="__main__":main()
