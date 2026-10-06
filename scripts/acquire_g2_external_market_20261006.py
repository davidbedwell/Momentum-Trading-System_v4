from pathlib import Path
import json,hashlib
import pandas as pd
import yfinance as yf
ROOT=Path("/home/ubuntu/Momentum-Trading-System_v4")
OUT=ROOT/"Research/Data/ExternalMarket/G2"
OUT.mkdir(parents=True,exist_ok=True)
tickers=["XLB","XLE","XLF","XLI","XLK","XLP","XLU","XLV","XLY"]
x=yf.download(tickers,start="2005-09-01",end="2026-09-15",auto_adjust=False,progress=False,threads=True)
if x.empty: raise RuntimeError("sector ETF download empty")
rows=[]
for t in tickers:
    y=pd.DataFrame({
      "date":pd.to_datetime(x.index),
      "open":x["Open",t].to_numpy(float),
      "high":x["High",t].to_numpy(float),
      "low":x["Low",t].to_numpy(float),
      "close":x["Close",t].to_numpy(float),
      "adj_close":x["Adj Close",t].to_numpy(float),
      "volume":x["Volume",t].to_numpy(float),
      "ticker":t})
    rows.append(y.dropna(subset=["adj_close"]))
panel=pd.concat(rows,ignore_index=True).sort_values(["date","ticker"])
panel.to_parquet(OUT/"legacy_sector_etf_panel_2005_2026.parquet",index=False)
d10=pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10")
d10.to_csv(OUT/"FRED_DGS10_20261006.csv",index=False)
manifest={"format":"MTS_G2_EXTERNAL_MARKET_V1","date":"2026-10-06",
 "sector_etfs":tickers,"reason":"legacy long-history market/sector breadth universe, disjoint from stock partitions",
 "start":str(panel.date.min().date()),"end":str(panel.date.max().date()),
 "rows":int(len(panel)),"tickers":int(panel.ticker.nunique()),
 "files":{}}
for f in [OUT/"legacy_sector_etf_panel_2005_2026.parquet",OUT/"FRED_DGS10_20261006.csv"]:
    manifest["files"][f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
(OUT/"manifest_20261006.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
print(json.dumps(manifest,indent=2,sort_keys=True))
