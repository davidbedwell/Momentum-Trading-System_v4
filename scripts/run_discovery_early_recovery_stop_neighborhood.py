#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,os,statistics
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
DEPTHS=(.03,.035,.04,.05);TIMES=(3,4,5,None);RECS=(.25,.50);STOPS=(.01,.02,.03,None);G={}
def med(x):return statistics.median(x) if x else None
def init(cfg):G.update(cfg)
def cp(t):return Path(G["outdir"])/f"{t}.json.gz"
def process(t):
 p=cp(t)
 if p.exists():
  try:
   with gzip.open(p,"rt") as f:r=json.load(f)
   if r.get("format")=="MTS_V4_EARLY_RECOVERY_STOP_TARGET_V1" and r.get("rows"):return t,True,r
  except:pass
 src=Path(G["trajdir"])/f"{t}.json.gz"
 with gzip.open(src,"rt") as f:tr=json.load(f)
 if not tr.get("rows"):raise RuntimeError(f"{t}: empty trajectory source")
 dates=[r["signal_date"] for r in tr["rows"]];start=min(dates);end="2026-09-15"
 bars=list(YFinanceDailyMarketSource().fetch(ticker=t,start_date=start,end_date=end));bars.sort(key=lambda x:str(x["date"]));bd={str(x["date"])[:10]:i for i,x in enumerate(bars)}
 if not bars:raise RuntimeError(f"{t}: zero bars")
 rows=[]
 for r in tr["rows"]:
  si=bd.get(r["signal_date"]);h=int(r["horizon"])
  if si is None or si+1>=len(bars) or si+h>=len(bars):continue
  path=bars[si+1:si+h+1];ref=float(r["reference"]);exitp=float(path[-1]["close"])
  cells=[]
  for dep in DEPTHS:
   for timing in TIMES:
    for frac in RECS:
     runlow=ref;elig=None;conf=None
     for j,x in enumerate(path[:-1]):
      runlow=min(runlow,float(x["low"]))
      if runlow/ref-1<=-dep and elig is None:elig=j
      if elig is not None:
       if timing is not None and elig>timing:break
       target=runlow+frac*(ref-runlow)
       if float(x["close"])>=target:conf=j;break
     if elig is None or (timing is not None and elig>timing):continue
     base={"depth":dep,"timing":timing,"recovery_fraction":frac,"eligible":True,"eligibility_offset":elig,"confirmation_offset":conf}
     if conf is None or conf+1>=len(path):
      cells.append(base);continue
     ej=conf+1;ep=float(path[ej]["open"]);post=path[ej:]
     base.update({"entry":ep,"original_terminal_return":exitp/ref-1,"nostop_return":exitp/ep-1})
     for stop in STOPS:
      z={"stop":stop};real=exitp/ep-1;stopped=False;sj=None;sp=None
      if stop is not None:
       level=ep*(1-stop)
       for k,x in enumerate(post):
        op=float(x["open"]);lo=float(x["low"])
        if op<=level:stopped=True;sj=k;sp=op;break
        if lo<=level:stopped=True;sj=k;sp=level;break
       if stopped:real=sp/ep-1
      z.update({"stopped":stopped,"realized_return":real,"win":real>0})
      if stopped:
       aft=post[sj:];z["further_1"]=min(float(x["low"]) for x in aft)<=sp*.99;z["further_2"]=min(float(x["low"]) for x in aft)<=sp*.98;z["further_3"]=min(float(x["low"]) for x in aft)<=sp*.97;z["further_5"]=min(float(x["low"]) for x in aft)<=sp*.95
       z["recover_entry"]=max(float(x["high"]) for x in aft)>=ep;z["recover_reference"]=max(float(x["high"]) for x in aft)>=ref;z["would_terminal_win_without_stop"]=exitp>ep
       z["post_stop_mae"]=min(float(x["low"])/sp-1 for x in aft);z["post_stop_mfe"]=max(float(x["high"])/sp-1 for x in aft)
      base.setdefault("stops",[]).append(z)
     cells.append(base)
  rows.append({"ticker":t,"family":r["family"],"candidate_id":r["candidate_id"],"signal_date":r["signal_date"],"horizon":h,"reference":ref,"cells":cells})
 out={"format":"MTS_V4_EARLY_RECOVERY_STOP_TARGET_V1","ticker":t,"rows":rows}
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(".tmp.gz")
 with gzip.open(tmp,"wt") as f:json.dump(out,f,separators=(",",":"))
 os.replace(tmp,p);return t,False,out
def main():
 a=argparse.ArgumentParser();a.add_argument("--trajectory-dir",required=True);a.add_argument("--checkpoint-dir",required=True);a.add_argument("--output",required=True);a.add_argument("--workers",type=int,default=8);q=a.parse_args()
 tickers=sorted(p.name[:-8] for p in Path(q.trajectory_dir).glob("*.json.gz"))
 if len(tickers)!=67:raise RuntimeError(f"expected 67 trajectory tickers, got {len(tickers)}")
 cfg={"trajdir":q.trajectory_dir,"outdir":q.checkpoint_dir};rows=[]
 with ProcessPoolExecutor(max_workers=q.workers,initializer=init,initargs=(cfg,)) as ex:
  fs={ex.submit(process,t):t for t in tickers}
  for n,f in enumerate(as_completed(fs),1):
   t,reused,r=f.result();rows.extend(r["rows"]);print(f"[{n}/67] {'RESUMED' if reused else 'COMPLETE'}={t}",flush=True)
 observed={r["ticker"] for r in rows}
 if observed!=set(tickers):raise RuntimeError(f"incomplete output {sorted(set(tickers)-observed)}")
 table=[]
 for dep in DEPTHS:
  for timing in TIMES:
   for frac in RECS:
    c=[x for r in rows for x in r["cells"] if x["depth"]==dep and x["timing"]==timing and x["recovery_fraction"]==frac and x.get("entry") is not None]
    for stop in STOPS:
     zz=[next(z for z in x["stops"] if z["stop"]==stop) for x in c]
     st=[z for z in zz if z["stopped"]]
     table.append({"depth":dep,"timing":timing,"recovery_fraction":frac,"stop":stop,"entries":len(c),
       "win_rate":sum(z["win"] for z in zz)/len(zz) if zz else None,"mean_return":statistics.fmean(z["realized_return"] for z in zz) if zz else None,"median_return":med([z["realized_return"] for z in zz]),
       "stop_rate":len(st)/len(zz) if zz else None,
       "stopped_further_1":sum(z["further_1"] for z in st)/len(st) if st else None,"stopped_further_2":sum(z["further_2"] for z in st)/len(st) if st else None,
       "stopped_further_3":sum(z["further_3"] for z in st)/len(st) if st else None,"stopped_further_5":sum(z["further_5"] for z in st)/len(st) if st else None,
       "stopped_recover_entry":sum(z["recover_entry"] for z in st)/len(st) if st else None,"stopped_recover_reference":sum(z["recover_reference"] for z in st)/len(st) if st else None,
       "stopped_would_terminal_win":sum(z["would_terminal_win_without_stop"] for z in st)/len(st) if st else None,
       "ticker_breadth":len({r["ticker"] for r in rows for x in r["cells"] if x["depth"]==dep and x["timing"]==timing and x["recovery_fraction"]==frac and x.get("entry") is not None}),
       "family_breadth":len({r["family"] for r in rows for x in r["cells"] if x["depth"]==dep and x["timing"]==timing and x["recovery_fraction"]==frac and x.get("entry") is not None})})
 out={"format":"MTS_V4_DISCOVERY_EARLY_RECOVERY_STOP_SUMMARY_V1","ticker_count":67,"trade_rows":len(rows),"table":table,"search_run":False,"refit":False,"rule_selection":False,"verification_a_accessed":False,"verification_b_accessed":False,"sol_calls":0}
 Path(q.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("REPORT="+q.output);print(f"TRADES={len(rows)} CELLS={len(table)}")
 # Keep terminal compact: print the user's central 3/3.5/4/5% × day4 ×25% recovery neighborhood for all stops.
 print("DAY4_REC25_NEIGHBORHOOD")
 for z in table:
  if z["timing"]==4 and z["recovery_fraction"]==.25:
   print(f"AE={z['depth']:.1%} STOP={'NONE' if z['stop'] is None else f'{z["stop"]:.0%}'} n={z['entries']} win={(z['win_rate'] or 0):.3f} meanRet={(z['mean_return'] or 0):+.4f} stopRate={(z['stop_rate'] or 0):.3f} further2={(z['stopped_further_2'] or 0):.3f} recoverEntry={(z['stopped_recover_entry'] or 0):.3f} terminalWin={(z['stopped_would_terminal_win'] or 0):.3f}")
 print("DETAIL=FULL_256_CELL_JSON")
 print("SEARCH_RUN=False REFIT=False RULE_SELECTION=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False SOL_CALLS=0")
if __name__=="__main__":main()
