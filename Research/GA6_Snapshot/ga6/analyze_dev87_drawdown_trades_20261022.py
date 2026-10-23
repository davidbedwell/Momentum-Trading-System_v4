import json,pathlib,collections
import numpy as np,pandas as pd
P=pathlib.Path('/opt/mts/ga6/runs/post_v3_comparison_20261022');a=[json.loads(x) for x in (P/'dev87_drawdown_autopsy.jsonl').open()];assert len(a)==53
rows=[];episodes=[]
for rec in a:
 h=rec['hash'];t=rec['trough'];peak=t['peak_date'];trough=t['trough_date'];episode={'chromosome':h,**t};episodes.append(episode)
 nav=pd.DataFrame(rec['daily']); nav['date']=pd.to_datetime(nav.date); peakdt=pd.Timestamp(peak);troughdt=pd.Timestamp(trough)
 for tr in rec['trades']:
  entry=pd.Timestamp(tr['entry_date']);exit=pd.Timestamp(tr['exit_date']);fees=sum(f['fee'] for f in tr['fills']);buys=sum(f['shares']*f['price'] for f in tr['fills'] if f['side']=='BUY');sells=sum(f['shares']*f['price'] for f in tr['fills'] if f['side']=='SELL');ret=(sells-buys-fees)/buys if buys else np.nan
  overlap=(entry<=troughdt and exit>=peakdt)
  # Close-to-close exposure at peak/trough, ignoring interim fill cash flow; use interval P&L instead.
  pnl_interval=0.
  for day in rec['daily']:
   dt=pd.Timestamp(day['date']);
   if dt<peakdt or dt>troughdt:continue
   if tr['ticker'] not in day['holdings']:continue
  r={'chromosome':h,'ticker':tr['ticker'],'entry_date':tr['entry_date'],'exit_date':tr['exit_date'],'sessions':tr['held_sessions'],'exit_reason':tr['exit_reason'],'trade_return':ret,'mae':tr['mae_low'],'mfe':tr['mfe_high'],'peak_to_trough_overlap':overlap,'portfolio_mdd':tr['portfolio_mdd'],'peak_date':peak,'trough_date':trough,'entry_price':tr['entry_price'],'exit_price':tr['exit_price'],'buy_notional':buys}
  for prefix in ['entry','exit']:
   for k,v in tr[prefix+'_features'].items():
    try:r[prefix+'_'+k]=float(v)
    except (ValueError,TypeError):pass
  rows.append(r)
d=pd.DataFrame(rows);d.to_csv(P/'dev87_trade_level_drawdown_features.csv',index=False);pd.DataFrame(episodes).to_csv(P/'dev87_peak_trough_episodes.csv',index=False)
# Compare adverse excursion, not just realized losses; these groups are diagnostic, not causal.
d['high_adverse_excursion']=d.mae<=-.10
d['low_adverse_excursion']=d.mae>-.10
summ={}
for label,group in [('high_adverse',d[d.high_adverse_excursion]),('low_adverse',d[d.low_adverse_excursion]),('overlap_peak_trough',d[d.peak_to_trough_overlap]),('not_overlap',d[~d.peak_to_trough_overlap])]:
 summ[label]={'trades':len(group),'median_trade_return':float(group.trade_return.median()),'median_mae':float(group.mae.median()),'median_mfe':float(group.mfe.median()),'median_sessions':float(group.sessions.median()),'exit_reasons':group.exit_reason.value_counts().to_dict()}
for feature in [x for x in d.columns if x.startswith('entry_') or x.startswith('exit_')]:
 if feature in ['entry_date','exit_date','entry_price','exit_price']:continue
 if not pd.api.types.is_numeric_dtype(d[feature]):continue
 a=d.loc[d.high_adverse_excursion,feature].dropna();b=d.loc[d.low_adverse_excursion,feature].dropna()
 if len(a)>=20 and len(b)>=20 and a.std()>0 and b.std()>0:
  pooled=np.sqrt((a.var()+b.var())/2)
  if pooled>0:summ.setdefault('feature_differences',[]).append({'feature':feature,'high_median':float(a.median()),'low_median':float(b.median()),'standardized_mean_difference':float((a.mean()-b.mean())/pooled),'high_n':len(a),'low_n':len(b)})
summ['feature_differences']=sorted(summ.get('feature_differences',[]),key=lambda x:abs(x['standardized_mean_difference']),reverse=True)[:20]
summ['total_trade_records']=len(d);summ['chromosomes']=len(a) if False else len(episodes);summ['cautions']=['MAE is price low excursion relative to first fill, not portfolio maximum drawdown','Multiple chromosomes can repeat identical ticker/time trades','Exit reasons are approximate for mandatory risk: a gap and time-cap are distinguished, discretionary exits are grouped','Unrealized open positions are not in completed trade comparison','Features measured on execution date, not necessarily the prior decision date; avoid interpreting as predictive entry conditions','This is retrospective exploratory analysis; test any new filter on a fresh holdout']
(P/'dev87_drawdown_trade_comparison.json').write_text(json.dumps(summ,indent=2));print(json.dumps({k:v for k,v in summ.items() if k!='feature_differences'},indent=2));print('TOP DIFFERENCES',json.dumps(summ['feature_differences'][:12],indent=2))
