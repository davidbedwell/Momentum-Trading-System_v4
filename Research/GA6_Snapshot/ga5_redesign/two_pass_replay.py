"""GA5 frozen shadow library and chronological selector diagnostic."""
import argparse,json
from pathlib import Path
import pandas as pd
from ga5_chromosome_contract import Genome
from guarded_evaluator import PreparedSessions
from shadow_signals import ShadowBook
from ga5_feature_adapter import extract

def run():
 p=argparse.ArgumentParser()
 for arg in ('features','policy-file','checkpoints','output'):p.add_argument('--'+arg,required=True)
 a=p.parse_args()
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 frame=pd.read_parquet(a.features)
 frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
 policy=json.loads(Path(a.policy_file).read_text())
 membership={(d,t):v for d,t,v in policy['membership']}
 blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
 veto=policy['risk_veto']
 genomes={}
 for path in sorted(Path(a.checkpoints).glob('checkpoint_*.json')):
  cp=json.loads(path.read_text())
  if cp.get('best'):genomes[cp['niche']]=Genome(**cp['best']['genome'])
 if not genomes:raise ValueError('No frozen chromosomes')
 books={name:ShadowBook(g) for name,g in genomes.items()}
 candidates=[]
 for date,rows,opens,closes in PreparedSessions(frame).sessions:
  for book in books.values():book.start(date,opens,blocked,membership,veto)
  for name,book in books.items():
   book.finish(date,rows,closes,blocked,membership,veto)
   for ticker,(action,signal_date) in book.pending.items():
    if action!='BUY' or signal_date!=date:continue
    g=genomes[name];features=extract(rows[ticker],book.fields)
    if features is None:continue
    candidates.append({'date':date,'niche':name,'ticker':ticker,'signal':float(features[g.entry_feature]),'chromosome':str(g.identity())})
 trades=[{'niche':name,**trade} for name,book in books.items() for trade in book.closed]
 pd.DataFrame(trades).to_parquet(out/'shadow_trades.parquet',index=False)
 pd.DataFrame(candidates).to_parquet(out/'candidate_signals.parquet',index=False)
 # Strict chronology: only trades exited before date enter ranking history.
 by_date={}
 for c in candidates:by_date.setdefault(c['date'],[]).append(c)
 closed=sorted(trades,key=lambda t:t['exit_date'])
 lookup={(t['niche'],t['ticker'],t['signal_date']):t for t in trades}
 cursor=0;history={};decisions=[]
 for date in sorted(by_date):
  while cursor<len(closed) and closed[cursor]['exit_date']<date:
   t=closed[cursor];history.setdefault(t['niche'],[]).append(t['net_return']);cursor+=1
  choices=by_date[date]
  def score(c):
   h=history.get(c['niche'],[])
   return (sum(h)/(len(h)+30)) if h else 0.
  selected=max(choices,key=lambda c:(score(c),c['signal'],c['niche'],c['ticker']))
  outcomes=[(c,lookup.get((c['niche'],c['ticker'],c['date']))) for c in choices]
  observed=[(c,t) for c,t in outcomes if t is not None]
  best=max(observed,key=lambda pair:pair[1]['net_return']) if observed else None
  actual=lookup.get((selected['niche'],selected['ticker'],date))
  decisions.append({'date':date,'candidate_count':len(choices),'selected_niche':selected['niche'],'selected_ticker':selected['ticker'],'predicted_score':score(selected),'history_count':len(history.get(selected['niche'],[])),'selected_net_return':actual['net_return'] if actual else None,'oracle_best_net_return':best[1]['net_return'] if best else None,'oracle_best_niche':best[0]['niche'] if best else None,'oracle_best_ticker':best[0]['ticker'] if best else None,'oracle_match':bool(best and selected['niche']==best[0]['niche'] and selected['ticker']==best[0]['ticker'])})
 pd.DataFrame(decisions).to_parquet(out/'selector_decisions.parquet',index=False)
 valid=[r for r in decisions if r['selected_net_return'] is not None and r['oracle_best_net_return'] is not None]
 report={'status':'DIAGNOSTIC_ONLY','chromosomes':list(genomes),'shadow_closed_trades':len(trades),'candidate_signals':len(candidates),'decision_days':len(decisions),'scored_days':len(valid),'oracle_match_rate':sum(r['oracle_match'] for r in valid)/len(valid) if valid else None,'selector_mean_net_return':sum(r['selected_net_return'] for r in valid)/len(valid) if valid else None,'oracle_mean_net_return':sum(r['oracle_best_net_return'] for r in valid)/len(valid) if valid else None,'limitations':'One opportunity/day; no capital-constrained execution, scaling, or out-of-sample certification. Oracle only for retrospective comparison.'}
 (out/'report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':run()
