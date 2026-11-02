import pandas as pd
f=pd.read_parquet('/opt/mts/ga6/data/ga6d_defensive_features.parquet',columns=['ticker','date','open','close','stock_splits'])
for ticker in ['BEN','CME','CTSH','DECK','ETN','STLD','SYK']:
 d=f[f.ticker==ticker].sort_values('date').reset_index(drop=True)
 for j in d.index[d.stock_splits.fillna(0)!=0][:3]:
  print(ticker, d.iloc[max(0,j-1):j+2][['date','open','close','stock_splits']].to_string(index=False))
