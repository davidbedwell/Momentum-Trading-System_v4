import pathlib,json,hashlib,os,urllib.request,urllib.error
import pandas as pd,numpy as np
p=pathlib.Path('/opt/mts/ga6/runs/independent_review');d=pd.read_parquet(p/'trade_entries_prior_features.parquet');e=pd.read_parquet(p/'daily_equity.parquet');h=pd.read_parquet(p/'daily_holdings.parquet');f=pd.read_parquet(p/'executed_fills.parquet');m=pd.read_parquet(p/'market_indicator_panel.parquet')
features=[c for c in d if c.startswith('prior_') and pd.api.types.is_numeric_dtype(d[c])]
rows=[]
for col in features:
 x=d[[col,'trade_return','mae','ticker','entry_date']].dropna().copy()
 if len(x)<100 or x[col].nunique()<5:continue
 x['event']=x.ticker.astype(str)+'|'+x.entry_date.astype(str)
 event=x.groupby('event',sort=False).agg(feature=(col,'first'),ret=('trade_return','mean'),mae=('mae','mean'))
 if len(event)<30:continue
 event['bucket']=pd.qcut(event.feature,5,labels=False,duplicates='drop')
 groups=event.groupby('bucket').agg(events=('ret','size'),mean_return=('ret','mean'),median_return=('ret','median'),loss_rate=('ret',lambda a:float((a<0).mean())),severe_loss_rate=('ret',lambda a:float((a<=-.10).mean())),mean_mae=('mae','mean'),feature_min=('feature','min'),feature_max=('feature','max')).round(6).reset_index().to_dict('records')
 rows.append({'feature':col,'event_count':len(event),'spearman_return':round(float(event.feature.corr(event.ret,method='spearman')),5),'spearman_mae':round(float(event.feature.corr(event.mae,method='spearman')),5),'quintiles':groups})
port=[]
for key,g in e.groupby('chromosome'):
 g=g.sort_values('date');v=g.nav.astype(float);initial=float(v.iloc[0]);last=float(v.iloc[-1]);days=(pd.Timestamp(g.date.iloc[-1])-pd.Timestamp(g.date.iloc[0])).days
 port.append({'chromosome':key,'days':days,'observations':len(g),'cagr':round(float((last/initial)**(365.25/max(days,1))-1),6),'mdd':round(float((v/v.cummax()-1).min()),6)})
summary={'trade_observations':len(d),'unique_events':int(d[['ticker','entry_date']].drop_duplicates().shape[0]),'chromosomes':d.chromosome.nunique(),'tickers':d.ticker.nunique(),'equity_rows':len(e),'holdings_rows':len(h),'fill_rows':len(f),'market_rows':len(m),'market_columns':list(m.columns),'trade_columns':list(d.columns),'trade_return_distribution':d.trade_return.describe(percentiles=[.05,.25,.5,.75,.95]).round(6).to_dict(),'portfolio_results':port,'feature_full_population_event_level_quintiles':rows,'missingness':{c:round(float(d[c].isna().mean()),6) for c in features},'exit_reasons':d.groupby('exit_reason').agg(n=('trade_return','size'),mean_return=('trade_return','mean'),loss_rate=('trade_return',lambda a:float((a<0).mean()))).round(6).reset_index().to_dict('records')}
(p/'FULL_POPULATION_ANALYSIS.json').write_text(json.dumps(summary,default=str,separators=(',',':')))
print('FULL_POPULATION_READY',len(d),summary['unique_events'],len(rows),len(port),flush=True)
brief=(p/'REVIEW_BRIEF.txt').read_text();payload_text=brief+'\n\nFull-population computed evidence follows. Every row in all 8218 trades and every daily NAV was used in these calculations. Feature analyses deduplicate repeated stock-entry events by averaging returns per event; the raw parquet data remains archived on server. Do not claim to have directly read raw rows not included here. Independently interrogate these full-population statistics, identify candidate patterns and defects, and specify further exact full-data computations needed. Distinguish descriptive association from predictive evidence.\n'+json.dumps(summary,default=str,separators=(',',':'))
(p/'FULL_POPULATION_REQUEST_METADATA.json').write_text(json.dumps({'trade_rows_analyzed':len(d),'events_analyzed':summary['unique_events'],'features_analyzed':len(rows),'portfolios_analyzed':len(port),'prompt_bytes':len(payload_text.encode()),'prompt_sha256':hashlib.sha256(payload_text.encode()).hexdigest()},indent=2))
keyline=next(line for line in pathlib.Path('/root/.openrouter_api_env').read_text().splitlines() if line.startswith('OPENROUTER_API_KEY='));key=keyline.split('=',1)[1].strip().strip('"').strip("'")
payload={'model':'anthropic/claude-sonnet-4.6','messages':[{'role':'user','content':payload_text}],'max_tokens':8000,'temperature':0.2}
request=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(payload,allow_nan=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','HTTP-Referer':'https://chatgpt.com','X-Title':'GA6 Full Population Independent Audit'})
try:
 with urllib.request.urlopen(request,timeout=240) as r:answer=json.load(r)
 (p/'FULL_POPULATION_CLAUDE_RESPONSE.json').write_text(json.dumps(answer,indent=2))
 content=answer.get('choices',[{}])[0].get('message',{}).get('content','');(p/'FULL_POPULATION_CLAUDE_REVIEW.md').write_text(content if isinstance(content,str) else json.dumps(content))
 print('SUBMITTED_SUCCESS',answer.get('model'),'RESPONSE_CHARS',len(content),'USAGE',answer.get('usage'))
except Exception as ex:print('SUBMISSION_FAILED',type(ex).__name__,str(ex));raise
