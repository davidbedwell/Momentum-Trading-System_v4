#!/usr/bin/env python3
import json, runpy
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path("/home/ubuntu/Momentum-Trading-System_v4")
src=(ROOT/"scripts/run_defensive_stock_market_router_loeo_20261004.py").read_text()
ns={}
exec(compile(src.split('report={')[0], "router_prefix", "exec"),ns)
rows=ns["rows"]; trades=ns["trades"]; WNAMES=ns["WNAMES"]; select=ns["select"]; predict=ns["predict"]
X=ns["X"]; E=ns["E"]; key=ns["key"]; FEATURES=ns["FEATURES"]; pdf=ns["pdf"]
# Reconstruct each LOEO prediction exactly and attach identity/entry observation.
records=[]
for held in WNAMES:
    tr=[r for r in rows if r["episode"]!=held]; te=[r for r in rows if r["episode"]==held]
    sc,g,th=select(tr); pp=predict(te,g,th)
    held_idx=[i for i,r in enumerate(rows) if r["episode"]==held]
    for local,(r,pred,ri) in enumerate(zip(te,pp,held_idx)):
        t=trades[ri]; ei=key[(t["ticker"],t["signal_date"])]; obs=max(0,t["entry_day"]-1)
        def v(n):
            x=float(X[ei,obs,FEATURES.index(n)])
            return x if np.isfinite(x) else None
        rec={"episode":held,"ticker":t["ticker"],"signal_date":t["signal_date"],"entry_day":t["entry_day"],
             "true_label":r["label"],"predicted_label":pred,"net_return":float(r["ret"]),
             "stock_ret5":v("stock_ret5"),"stock_ret20":v("stock_ret20"),
             "market_ret5":v("market_ret5"),"market_ret20":v("market_ret20"),
             "rel5":r["rel5"],"rel20":r["rel20"],"stock_drawdown252":r["stock_drawdown252"],
             "stock_close_sma20":v("stock_close_sma20"),"stock_range20":v("stock_range20"),
             "stock_rsi14":v("stock_rsi14"),"stock_rv_pct":v("stock_rv_pct"),
             "market_drawdown252":v("market_drawdown252"),"breadth_above_sma200":v("breadth_above_sma200"),
             "breadth_positive20":v("breadth_positive20"),"vix":v("vix"),"vvix":v("vvix"),
             "ofr_funding_lag2":v("ofr_funding_lag2"),"ofr_credit_lag2":v("ofr_credit_lag2")}
        records.append(rec)
# Add strictly trailing causal persistence snapshots from predictor panel.
pdf2=pdf.sort_values(["ticker","date"]).copy()
cols=["return_5__v1","return_20__v1","close_to_sma_20__v1","range_position_20__v1","rsi_14__v1"]
for rec in records:
    h=pdf2[(pdf2.ticker==rec["ticker"])&(pdf2.date<=rec["signal_date"])].tail(10)
    if len(h):
        md=ns["mkt"].loc[h.date]
        rel20=h["return_20__v1"].to_numpy(float)-md["market_ret20"].to_numpy(float)
        rel5=h["return_5__v1"].to_numpy(float)-md["market_ret5"].to_numpy(float)
        rec["trail10_rel20_positive_fraction"]=float(np.mean(rel20>0))
        rec["trail10_rel5_positive_fraction"]=float(np.mean(rel5>0))
        rec["trail10_stock_ret20_positive_fraction"]=float(np.mean(h["return_20__v1"].to_numpy(float)>0))
        rec["trail10_above_sma20_fraction"]=float(np.mean(h["close_to_sma_20__v1"].to_numpy(float)>0))
        rec["trail10_rel20_slope"]=float(np.polyfit(np.arange(len(rel20)),rel20,1)[0]) if len(rel20)>1 else None
# Groups fixed before looking at outcome comparisons.
g2018=[r for r in records if r["episode"]=="2018"]
false2018=[r for r in g2018 if r["true_label"]=="OTHER" and r["predicted_label"]=="B"]
trueB=[r for r in records if r["true_label"]=="B"]
falseBother=[r for r in records if r["episode"]!="2018" and r["true_label"]=="OTHER" and r["predicted_label"]=="B"]
features=["stock_ret5","stock_ret20","market_ret5","market_ret20","rel5","rel20","stock_drawdown252","stock_close_sma20",
"stock_range20","stock_rsi14","stock_rv_pct","market_drawdown252","breadth_above_sma200","breadth_positive20","vix","vvix",
"ofr_funding_lag2","ofr_credit_lag2","trail10_rel20_positive_fraction","trail10_rel5_positive_fraction",
"trail10_stock_ret20_positive_fraction","trail10_above_sma20_fraction","trail10_rel20_slope","net_return"]
def summary(gr):
    out={"n":len(gr)}
    for f in features:
        a=np.array([x.get(f) for x in gr if x.get(f) is not None and np.isfinite(x.get(f))],float)
        if len(a): out[f]={"median":float(np.median(a)),"min":float(a.min()),"max":float(a.max())}
    return out
out={"format":"MTS_DEFENSIVE_2018_FALSE_B_AUTOPSY_V1","protocol":"Research/Protocols/MTS_DEFENSIVE_2018_FALSE_B_AUTOPSY_FREEZE_20261004.json",
"provenance":"NEW_RESEARCH_POST_RECOVERY","protected_accessed":False,"test17_accessed":False,"preserved50_accessed":False,
"label_independence_warning":"B is defined from development-domain stock_drawdown252 and rel20 ranks; those dimensions are therefore not independent economic validation.",
"rows_2018":g2018,"true_B_rows":trueB,"non2018_false_B_rows":falseBother,
"group_summaries":{"2018_false_B":summary(false2018),"true_B":summary(trueB),"non2018_false_B":summary(falseBother)}}
p=ROOT/"Research/Reports/MTS_DEFENSIVE_2018_FALSE_B_AUTOPSY_20261004.json"; p.write_text(json.dumps(out,indent=2))
print("REPORT",p); print("2018_FALSE_B",[(x["ticker"],x["signal_date"],round(x["stock_ret20"],4),round(x["market_ret20"],4),round(x["rel20"],4),round(x["net_return"],4)) for x in false2018])
print("TRUE_B_N",len(trueB),"OTHER_FALSE_B_N",len(falseBother)); print(json.dumps(out["group_summaries"],indent=2))
