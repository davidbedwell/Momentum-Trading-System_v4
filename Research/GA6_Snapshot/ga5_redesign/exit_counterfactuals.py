"""Counterfactual exit comparisons on a common, fixed entry cohort.
Exit decisions are evaluated chronologically; outcome metrics computed afterward.
"""
from dataclasses import replace
from ga5_chromosome_decisions import PositionState
from fast_decision import evaluate
from exit_objectives import metrics,pareto_front
def replay(entry, subsequent, genome,fee=.001):
 """subsequent: chronological (date, close, features) after fixed entry.
 Uses close signals; execution is next observed open supplied as 4th tuple element.
 """
 price=float(entry['price']);peak=price;held=0;exit_price=None;exit_date=None
 mfe=0.;mae=0.
 for index,(date,close,features,next_open) in enumerate(subsequent):
  held+=1;close=float(close);peak=max(peak,close)
  change=close/price-1;mfe=max(mfe,change);mae=min(mae,change)
  action,_=evaluate(genome,features,PositionState(1,price,peak,held),close)
  if action in ('EXIT','REPLACE_CANDIDATE'):
   if next_open is None:break
   exit_price=float(next_open);exit_date=date;break
 if exit_price is None:return {'status':'CENSORED','entry':price,'sessions':held,'mfe':mfe,'mae':mae}
 return {'status':'CLOSED','entry':price,'exit':exit_price,'exit_date':exit_date,'sessions':held,'mfe':mfe,'mae':mae,'net_return':exit_price*(1-fee)/(price*(1+fee))-1}
def compare(cohorts,genomes):
 """cohorts contain (entry, future observations); comparison is retrospective only."""
 results=[]
 for genome in genomes:
  trades=[replay(entry,observations,genome) for entry,observations in cohorts]
  score=metrics(trades)
  results.append({'genome':genome.identity(),'metrics':score,'censored':sum(t['status']=='CENSORED' for t in trades)})
 front=pareto_front([r['metrics'] for r in results])
 return {'status':'RETROSPECTIVE_ONLY','results':results,'pareto_indices':front}
