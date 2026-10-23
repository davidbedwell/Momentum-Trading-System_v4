import os,json,pathlib,urllib.request,urllib.error,time
import pandas as pd
p=pathlib.Path('/opt/mts/ga6/runs/independent_review')
d=pd.read_parquet(p/'trade_entries_prior_features.parquet')
# Deterministic random sample of distinct stock-entry events, preserving all outcomes without selecting on returns.
d['event']=d.ticker.astype(str)+'|'+d.entry_date.astype(str)
events=d[['event']].drop_duplicates().sample(frac=1,random_state=20261022).head(350).event
sample=d[d.event.isin(events)].drop(columns='event').sort_values(['ticker','entry_date'])
# Cap request size; preserve full sample rows and unbiased event selection.
fields=['chromosome','ticker','entry_date','exit_date','sessions','trade_return','mae','mfe','exit_reason','prior_ga4_return_20__v1','prior_ga4_return_63__v1','prior_ga4_return_126__v1','prior_ga4_return_252__v1','prior_ga4_close_to_sma_50__v1','prior_ga4_close_to_sma_200__v1','prior_ga4_natr_14__v1','prior_ga4_realized_vol_20__v1','prior_ga4_realized_vol_63__v1','prior_ga4_range_position_50__v1','prior_ga4_range_position_252__v1','prior_ga4_sector_vs_universe_return_63__v1','prior_ga4_relative_strength_change_20__v1','prior_ga4_breadth_above_sma_200__v1','prior_trend','prior_breadth','prior_relative_strength']
assert set(fields).issubset(sample.columns)
sample=sample[fields].copy();sample['entry_date']=sample.entry_date.astype(str);sample['exit_date']=sample.exit_date.astype(str)
sample=sample.round(5).where(pd.notna(sample),None)
rows=sample.to_dict(orient='records')
brief=(p/'REVIEW_BRIEF.txt').read_text()
message=brief+'\n\nHere is a deterministic, outcome-unfiltered random sample of distinct stock-entry events with all associated chromosome trades. The full 8218 rows and complete panel are in the server archive, but cannot fit in this API message. Treat the sample as exploratory, and identify which analyses require full data.\n'+json.dumps({'total_observations':8218,'sample_observations':len(rows),'distinct_sample_events':len(events),'columns':fields,'rows':rows},separators=(',',':'),default=str)
(p/'OPENROUTER_REQUEST_METADATA.json').write_text(json.dumps({'model':'anthropic/claude-sonnet-4.6','total_trade_rows':8218,'submitted_trade_rows':len(rows),'submitted_distinct_events':len(events),'prompt_bytes':len(message.encode()),'sample_seed':20261022},indent=2))
key=os.environ.get('OPENROUTER_API_KEY');assert key
payload={'model':'anthropic/claude-sonnet-4.6','messages':[{'role':'user','content':message}],'max_tokens':4500,'temperature':0.2}
request=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(payload,allow_nan=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','HTTP-Referer':'https://chatgpt.com','X-Title':'GA6 Independent Blind Audit'})
try:
 with urllib.request.urlopen(request,timeout=240) as response:result=json.load(response)
except urllib.error.HTTPError as e:
 print('API_HTTP_ERROR',e.code,e.read(1000).decode(errors='replace'));raise
(p/'OPENROUTER_RESPONSE.json').write_text(json.dumps(result,indent=2))
answer=result.get('choices',[{}])[0].get('message',{}).get('content','')
(p/'CLAUDE_INDEPENDENT_REVIEW.md').write_text(answer or json.dumps(result,indent=2))
print('MODEL',result.get('model'),'SAMPLED',len(rows),'OUTPUT_CHARS',len(answer),'USAGE',result.get('usage'));print(answer[:16000])
