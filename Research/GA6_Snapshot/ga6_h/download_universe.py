import io, pathlib, re, time, json, argparse
from datetime import datetime, timezone
import pandas as pd
import requests
import yfinance as yf
ROOT=pathlib.Path('/opt/mts/ga6_h/data');ROOT.mkdir(parents=True,exist_ok=True)
URLS={'nasdaq':'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt','other':'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt'}
BAD=re.compile(r'ETF|ETN|EXCHANGE.TRADED|PREFERRED|PREFERENCE|WARRANT|RIGHTS?|DEPOSITARY|DEPOSITORY|UNIT[S ]|ACQUISITION CORP|SPAC|TRUST|FUND|NOTES? DUE|BOND|INDEX',re.I)
def universe():
    frames=[]
    for kind,url in URLS.items():
        r=requests.get(url,timeout=40);r.raise_for_status()
        (ROOT/f'{kind}_raw.txt').write_bytes(r.content)
        df=pd.read_csv(io.BytesIO(r.content),sep='|',dtype=str)
        if kind=='nasdaq':
            df=df[(df['Test Issue']=='N')&(df['ETF']=='N')]
            df=df.assign(symbol=df['Symbol'],exchange='NASDAQ',security_name=df['Security Name'])
        else:
            df=df[(df['Test Issue']=='N')&(df['ETF']=='N')&(df['Exchange'].isin(['N','A']))]
            df=df.assign(symbol=df['ACT Symbol'],exchange=df['Exchange'].map({'N':'NYSE','A':'NYSE American'}),security_name=df['Security Name'])
        frames.append(df[['symbol','exchange','security_name']])
    df=pd.concat(frames,ignore_index=True).dropna().drop_duplicates('symbol')
    df=df[~df.security_name.str.contains(BAD,na=False)]
    df=df[df.symbol.str.fullmatch(r'[A-Z][A-Z0-9.\-]{0,9}',na=False)]
    df['yf_symbol']=df.symbol.str.replace('.','-',regex=False)
    df.sort_values(['exchange','symbol']).to_parquet(ROOT/'current_universe.parquet',index=False)
    return df

def download(df,start,end,batch_size,pause):
    prices=ROOT/'prices';prices.mkdir(exist_ok=True)
    records=[]
    old=ROOT/'download_manifest.parquet'
    if old.exists():records=pd.read_parquet(old).to_dict('records')
    completed={r['symbol'] for r in records if r.get('status')=='ok' and (prices/(r['symbol'].replace('/','_')+'.parquet')).exists()}
    df=df[~df.yf_symbol.isin(completed)].reset_index(drop=True)
    print('remaining symbols',len(df),'already complete',len(completed),flush=True)
    for i in range(0,len(df),batch_size):
        batch=df.iloc[i:i+batch_size]
        tickers=batch.yf_symbol.tolist()
        try:
            raw=yf.download(tickers,start=start,end=end,auto_adjust=False,actions=True,group_by='ticker',threads=4,progress=False,timeout=20)
            for symbol in tickers:
                try:
                    d=raw[symbol].copy() if isinstance(raw.columns,pd.MultiIndex) else raw.copy()
                    d=d.dropna(subset=['Close'])
                    if d.empty:raise ValueError('empty history')
                    d.index=pd.to_datetime(d.index).tz_localize(None) if d.index.tz is None else pd.to_datetime(d.index).tz_convert(None)
                    d=d.reset_index().rename(columns={'Date':'date','Datetime':'date'})
                    d['symbol']=symbol
                    d.to_parquet(prices/(symbol.replace('/','_')+'.parquet'),index=False)
                    records.append({'symbol':symbol,'status':'ok','rows':len(d),'first':str(d.date.min()),'last':str(d.date.max())})
                except Exception as e:records.append({'symbol':symbol,'status':'failed','reason':str(e)[:200]})
        except Exception as e:
            records.extend({'symbol':s,'status':'batch_failed','reason':str(e)[:200]} for s in tickers)
        pd.DataFrame(records).to_parquet(ROOT/'download_manifest.parquet',index=False)
        print(f'batch {i//batch_size+1} / {(len(df)+batch_size-1)//batch_size}, downloaded {sum(r["status"]=="ok" for r in records)} / {len(records)}',flush=True)
        time.sleep(pause)
    return records
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--start',default='2016-01-01');p.add_argument('--end',default='2026-10-23');p.add_argument('--limit',type=int,default=0);p.add_argument('--batch-size',type=int,default=20);p.add_argument('--pause',type=float,default=2);a=p.parse_args()
    df=universe();print('current filtered universe',len(df),df.exchange.value_counts().to_dict(),flush=True)
    if a.limit:df=df.head(a.limit)
    results=download(df,a.start,a.end,a.batch_size,a.pause)
    print(json.dumps({'attempted':len(results),'success':sum(r['status']=='ok' for r in results),'finished_utc':datetime.now(timezone.utc).isoformat()}),flush=True)
