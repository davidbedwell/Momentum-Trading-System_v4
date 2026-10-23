"""Sequential stock niche recognition pilot. Historical labels use forward returns ONLY after predictions are logged.
Online classifier trains solely on previously matured outcomes; a global chronological clock prevents cross-stock time travel.
"""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score,balanced_accuracy_score,log_loss,brier_score_loss

STOCKS=['ACN','AMGN','XOM','COST','ATO','DIS','DECK','CME','UPS','ARE']
FEATURES=['trend','momentum','volatility','recursive','sector','breadth','relative_strength','ga4_return_20__v1','ga4_return_63__v1','ga4_natr_20__v1','ga4_close_to_sma_200__v1','ga4_realized_vol_20__v1','ga4_relative_volume_20__v1']
HORIZON=20
LABELS=['decline','range','advance']

def label_of(r):
 return 0 if r < -.05 else (2 if r > .05 else 1)

def run():
 p=argparse.ArgumentParser();p.add_argument('--input',default='ga5_redesign/exploratory79_ga4_enriched.parquet');p.add_argument('--output',default='ga5_redesign/sequential_niche_pilot_20261019');p.add_argument('--stocks',nargs='+',default=STOCKS);a=p.parse_args()
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 df=pd.read_parquet(a.input)
 df=df[df.ticker.isin(a.stocks)].copy().sort_values(['date','ticker'])
 df['date']=pd.to_datetime(df.date)
 # The label is strictly an ex-post 20-session forward outcome, never a feature.
 df['forward_return']=df.groupby('ticker').adj_close.shift(-HORIZON)/df.adj_close-1
 df['maturity_date']=df.groupby('ticker').date.shift(-HORIZON)
 df['label']=df.forward_return.map(lambda v:label_of(v) if pd.notna(v) else np.nan)
 # No data from other stocks at future dates may be used: each new stock is
 # introduced at a later chronological start date; previously learned stocks
 # are revisited in the same global time stream.
 start_dates=pd.date_range('2007-01-01','2016-01-01',periods=len(a.stocks))
 introductions=dict(zip(a.stocks,start_dates))
 df=df[df.apply(lambda r:r.date>=introductions[r.ticker],axis=1)]
 # Use fixed feature transforms known at time t, not full-history fitted scaler.
 x=df[FEATURES].replace([np.inf,-np.inf],np.nan).fillna(0).clip(-10,10).to_numpy(dtype=float)
 x=np.tanh(x)
 df=df.reset_index(drop=True)
 model=SGDClassifier(loss='log_loss',alpha=.001,random_state=1700,learning_rate='optimal')
 trained=False;queue=[];predictions=[];updates=[];seen_stocks=set();training_n=0
 for date,group in df.groupby('date',sort=True):
  # Train only after outcomes have matured strictly before today's close.
  mature=[j for j in queue if df.at[j,'maturity_date'] < date]
  if mature:
   xx=x[mature];yy=df.loc[mature,'label'].astype(int).to_numpy()
   model.partial_fit(xx,yy,classes=np.arange(3)) if not trained else model.partial_fit(xx,yy)
   trained=True;training_n+=len(mature);updates.append({'date':str(date.date()),'matured_training_samples':len(mature),'cumulative_training_samples':training_n})
   mature_set=set(mature);queue=[j for j in queue if j not in mature_set]
  for j in group.index:
   stock=df.at[j,'ticker'];first=stock not in seen_stocks;seen_stocks.add(stock)
   if trained:
    probs=model.predict_proba(x[j:j+1])[0];prediction=int(np.argmax(probs));confidence=float(max(probs))
   else:probs=np.array([1/3]*3);prediction=1;confidence=1/3
   true=df.at[j,'label'];valid=pd.notna(true)
   predictions.append({'date':str(date.date()),'ticker':stock,'new_stock_introduction':first,'training_samples_available':training_n,'predicted_niche':LABELS[prediction],'confidence':confidence,'prob_decline':float(probs[0]),'prob_range':float(probs[1]),'prob_advance':float(probs[2]),'actual_20d_niche':LABELS[int(true)] if valid else None,'actual_20d_return':float(df.at[j,'forward_return']) if valid else None,'maturity_date':str(df.at[j,'maturity_date'].date()) if valid else None,'correct':bool(prediction==int(true)) if valid else None})
   if valid:queue.append(j)
 log=pd.DataFrame(predictions);log.to_csv(out/'daily_predictions.csv',index=False)
 pd.DataFrame(updates).to_csv(out/'learning_updates.csv',index=False)
 summaries=[]
 for ticker in a.stocks:
  sub=log[(log.ticker==ticker)&log.correct.notna()]
  if len(sub)==0:continue
  actual=sub.actual_20d_niche;pred=sub.predicted_niche
  base=actual.value_counts(normalize=True).max()
  summaries.append({'ticker':ticker,'introduction':str(introductions[ticker].date()),'predictions':len(sub),'accuracy':float((actual==pred).mean()),'majority_class_baseline':float(base),'lift_vs_baseline':float((actual==pred).mean()-base),'mean_confidence':float(sub.confidence.mean()),'brier_multiclass':float(np.mean(sum((sub['prob_'+k]-(actual==k).astype(float))**2 for k in LABELS)))})
 report={'status':'DIAGNOSTIC_ONLY','method':'global chronological online incremental learning; future 20-session labels revealed after maturity','label_definition':{'decline':'20d forward return below -5%','range':'-5% to +5%','advance':'above +5%'},'stock_order':a.stocks,'features':FEATURES,'prediction_count':len(log),'training_updates':len(updates),'by_stock':summaries,'warnings':['Outcome labels are retrospective and are not intrinsic market regimes','Existing feature columns require independent point-in-time leakage audit','Fixed feature clipping is heuristic','Repeated daily overlapping labels are correlated','This measures predictive classification, not profitability or validated micro-niche discovery']}
 (out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':run()
