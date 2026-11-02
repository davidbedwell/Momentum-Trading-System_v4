"""Chronological synthetic learning smoke test with proxy signals, NOT native GA chromosomes."""
import json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from .daily_shadow_training import DailyShadowTrainer,ShadowPrediction

PATH=Path('/opt/mts/synthetic-market-lab/runs/batch001/fsynth/train/seed_1000/stock_prices.parquet')
OUT=Path('/opt/mts/synthetic-market-lab/reports/daily_shadow_learning_pilot.json')

def run():
 df=pd.read_parquet(PATH).sort_values(['Ticker','Date']).copy()
 df['r5']=df.groupby('Ticker').Close.pct_change(5)
 df['r20']=df.groupby('Ticker').Close.pct_change(20)
 df['future_open']=df.groupby('Ticker').Open.shift(-1)
 df['future_close']=df.groupby('Ticker').Close.shift(-2)
 df['net_return']=df.future_close/df.future_open-1-.002
 dates=sorted(df.Date.unique());trainer=DailyShadowTrainer();pending={};daily=[];selected=[];frozen=[]
 # Two deliberately simple proxy chromosomes, not GA6/GA7 executable strategies.
 for day,date in enumerate(dates):
  matured={key:value for due,key,value in pending.pop(day,[])}
  today=df[df.Date==date]
  records=[];options=[]
  for row in today.itertuples(index=False):
   if not np.isfinite(row.r20) or not np.isfinite(row.net_return):continue
   niche='TREND' if row.r20>0 else 'REVERSION'
   for family,chromosome,signal in [('NICHE','trend_proxy',row.r5>0 and niche=='TREND'),('NON_NICHE','reversal_proxy',row.r5<0)]:
    if not signal:continue
    p=ShadowPrediction(day,row.Ticker,chromosome,family,float(abs(row.r5)),2)
    records.append(p);options.append((p,float(row.net_return)))
  # Frozen niche-first baseline; adaptive uses only matured chromosome scores.
  def score(p):
   stats=trainer.weights.get((p.family,p.chromosome))
   return (stats['mean_net_return'] if stats and stats['observations']>=10 else 0)+(p.predicted_edge*.01)
  baseline=sorted((z for z in options if z[0].family=='NICHE'),key=lambda z:-z[0].predicted_edge)[:10]
  adaptive=sorted(options,key=lambda z:-score(z[0]))[:10]
  selected.extend((day,p.ticker,p.family) for p,_ in adaptive)
  for p,r in options:pending.setdefault(day+2,[]).append((day+2,(day,p.ticker,p.chromosome),r))
  trainer.record_close(day,records)
  trainer.mature(day,matured)
  if options:daily.append({'session':day,'signals':len(options),'adaptive_mean_net':float(np.mean([r for _,r in adaptive])) if adaptive else 0,'frozen_mean_net':float(np.mean([r for _,r in baseline])) if baseline else 0,'matured_before_decision':len(trainer.matured)})
 result={'scope':'synthetic 100-stock 756-session TRAIN seed_1000; proxy chromosome signals only','sessions':len(dates),'sessions_with_signals':len(daily),'shadow_predictions':len(trainer.matured)+len(trainer.predictions),'matured':len(trainer.matured),'remaining_unmatured':len(trainer.predictions),'adaptive_mean_daily_signal_return':float(np.mean([r['adaptive_mean_net'] for r in daily])),'frozen_mean_daily_signal_return':float(np.mean([r['frozen_mean_net'] for r in daily])),'learning_weights':{str(k):v for k,v in trainer.weights.items()},'limitations':['Proxy momentum/reversal signals, not native GA6/GA7 chromosome execution','Return is next open to following close minus 20bp, not shared-capital portfolio NAV','No cash constraints, defense, corporate actions, or live execution','Shadow outcomes only become available after two sessions; generator latent regime is never read','Training scenario only; no holdouts touched']}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
