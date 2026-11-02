"""Daily synthetic causal shadow learner with two shared-capital replay portfolios.
Proxy strategy smoke only; does not claim native GA6/GA7 parity.
"""
import json
from pathlib import Path
import numpy as np
from .synthetic_adapter import load_fsynth
from .daily_shadow_training import DailyShadowTrainer,ShadowPrediction
from engines.portfolio_replay.kernel import Replay,Bar,Signal
ROOT=Path('/opt/mts/synthetic-market-lab')

def run(seed=1000):
 path=ROOT/f'runs/batch001/fsynth/train/seed_{seed}'
 frame=load_fsynth(path)
 tickers=sorted(frame.Ticker.unique()); dates=sorted(frame.Date.unique())
 closes=frame.pivot(index='Date',columns='Ticker',values='Close').reindex(index=dates,columns=tickers).to_numpy()
 opens=frame.pivot(index='Date',columns='Ticker',values='Open').reindex(index=dates,columns=tickers).to_numpy()
 if not np.isfinite(opens).all() or not np.isfinite(closes).all():raise ValueError('incomplete panel')
 trainer=DailyShadowTrainer();adaptive=Replay();frozen=Replay();queue={};selected_counts={'NICHE':0,'NON_NICHE':0};predictions=0
 for day,date in enumerate(dates):
  bars={t:Bar(float(opens[day,j]),float(closes[day,j])) for j,t in enumerate(tickers)}
  # Pending decisions are executed at today's open; today's decisions cannot trade until tomorrow.
  if day>=22:
   prior=closes[day-1];r5=prior/closes[day-6]-1;r20=prior/closes[day-21]-1
   # Outcome at close(day) for entry open(day-1) and exit close(day), net of 20bp.
   matured={key:float(closes[day,j]/opens[day-1,j]-1-.002) for key,j in queue.pop(day,[])}
  else:matured={}
  trainer.mature(day-1,matured) if day>0 else None
  # No future data is used in decision-making below.
  candidates=[]
  if day>=20 and day+2<len(dates):
   r5=closes[day]/closes[day-5]-1;r20=closes[day]/closes[day-20]-1
   for j,ticker in enumerate(tickers):
    for family,chrom,ok in [('NICHE','trend_proxy',r5[j]>0 and r20[j]>0),('NON_NICHE','reversal_proxy',r5[j]<0)]:
     if not ok:continue
     p=ShadowPrediction(day,ticker,chrom,family,float(abs(r5[j])),2)
     candidates.append((p,j))
  # Record today's predictions, then mature prior outcomes (no same-day learning).
  trainer.record_close(day,[p for p,_ in candidates]);trainer.mature(day,matured)
  def score(p):
   s=trainer.weights.get((p.family,p.chromosome))
   return (s['mean_net_return'] if s and s['observations']>=10 else 0)+.01*p.predicted_edge
  ranked=sorted(candidates,key=lambda z:(-score(z[0]),z[0].ticker))
  niche=sorted((z for z in candidates if z[0].family=='NICHE'),key=lambda z:(-z[0].predicted_edge,z[0].ticker))
  def make_signals(items,tag):
   chosen=[];seen=set()
   for p,j in items:
    if p.ticker in seen:continue
    seen.add(p.ticker);chosen.append(Signal(p.ticker,tag,p.chromosome,.1,score(p)))
    if tag=='ADAPTIVE':selected_counts[p.family]+=1
    if len(chosen)==10:break
   keep={s.ticker for s in chosen}
   portfolio=adaptive if tag=='ADAPTIVE' else frozen
   chosen.extend(Signal(t,tag,'exit',0,-1) for t in portfolio.shares if t not in keep)
   return chosen
  asigs=make_signals(ranked,'ADAPTIVE');fsigs=make_signals(niche,'FROZEN')
  adaptive.day(str(date),bars,asigs);frozen.day(str(date),bars,fsigs)
  for p,j in candidates:queue.setdefault(day+2,[]).append(((day,p.ticker,p.chromosome),j))
  predictions+=len(candidates)
 def stats(port):
  nav=np.array([v[1] for v in port.nav]);peak=np.maximum.accumulate(nav)
  return {'ending_nav':round(float(nav[-1]),2),'total_return_pct':round(float((nav[-1]/nav[0]-1)*100),3),'max_drawdown_pct':round(float(np.max(1-nav/peak)*100),3),'fills':len(port.ledger)}
 result={'market':str(path),'sessions':len(dates),'stocks':len(tickers),'shadow_predictions':predictions,'matured':len(trainer.matured),'unmatured':len(trainer.predictions),'selected_families':selected_counts,'adaptive':stats(adaptive),'frozen_niche':stats(frozen),'certified':False,'limitations':['Two proxy strategies only, not native chromosome adapters','Research Replay kernel lacks production parity','Synthetic training scenario; sealed holdouts untouched','Shadow returns fixed 2-session horizon, manager exits/rebalances daily']}
 out=ROOT/f'reports/synthetic_portfolio_learning_seed_{seed}.json';out.write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
