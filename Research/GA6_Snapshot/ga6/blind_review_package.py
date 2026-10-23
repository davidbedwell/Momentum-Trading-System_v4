import pathlib,json,zipfile,hashlib
import pandas as pd
root=pathlib.Path('/opt/mts');src=root/'ga6/runs/post_v3_comparison_20261022';out=root/'ga6/runs/independent_review';out.mkdir(exist_ok=True)
records=[json.loads(line) for line in (src/'dev87_drawdown_autopsy.jsonl').open()]
assert len(records)==53
nav=[];holdings=[];fills=[]
for record in records:
 key=record['hash']
 for day in record['daily']:
  nav.append({'chromosome':key,'date':day['date'],'nav':day['nav']})
  for ticker,position in day['holdings'].items():holdings.append({'chromosome':key,'date':day['date'],'ticker':ticker,**position})
 for trade in record['trades']:
  for fill in trade['fills']:fills.append({'chromosome':key,**fill})
for name,rows in [('daily_equity',nav),('daily_holdings',holdings),('executed_fills',fills)]:pd.DataFrame(rows).to_parquet(out/(name+'.parquet'),index=False)
trades=pd.read_csv(src/'dev87_trade_level_drawdown_features.csv');trades['entry_date']=pd.to_datetime(trades.entry_date)
market=pd.read_parquet(root/'thunder-migration/mts-certification-20261011/dev87/dev87_ga6_enriched.parquet');market['date']=pd.to_datetime(market.date);market=market.sort_values(['ticker','date']);market['following_date']=market.groupby('ticker').date.shift(-1)
features=[c for c in market.columns if c.startswith('ga4_') or c in ['trend','momentum','volatility','volume','sector','breadth','relative_strength','recursive']]
prior=market[['ticker','following_date',*features]].rename(columns={c:'prior_'+c for c in features})
cols=['chromosome','ticker','entry_date','exit_date','sessions','exit_reason','trade_return','mae','mfe','entry_price','exit_price','buy_notional']
joined=trades[cols].merge(prior,left_on=['ticker','entry_date'],right_on=['ticker','following_date'],validate='many_to_one').drop(columns='following_date')
assert len(joined)==8218
joined.to_parquet(out/'trade_entries_prior_features.parquet',index=False)
market.drop(columns='following_date').to_parquet(out/'market_indicator_panel.parquet',index=False,compression='zstd')
print('DATA_READY',len(joined),len(nav),len(holdings),len(fills),flush=True)
