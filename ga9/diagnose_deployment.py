"""Read-only GA9 development replay attribution; no sealed forward data."""
import json,sys,collections,statistics
from pathlib import Path

def diagnose(path):
 d=json.loads(Path(path).read_text()); out={'source':str(path),'family':d['family'],'horizon':d['horizon'],'folds':[]}
 for fold, replay in zip(d['folds'],d['replays']):
  fills=replay['fills']; events=replay['events']; equity=replay['equity']; opens=collections.defaultdict(list);closed=[]
  for f in fills:
   key=f['ticker']
   if f['action'] in ('ENTRY','ADD'):opens[key].append([f['quantity'],f['price'],f['date'],f['cost']])
   elif f['action'] in ('EXIT','REDUCE','REPLACE'):
    remaining=f['quantity'];cost=0.;pnl=0.;basis=0.
    while remaining>1e-8 and opens[key]:
     lot=opens[key][0];qty=min(remaining,lot[0]);basis+=qty*lot[1];pnl+=qty*(f['price']-lot[1])-lot[3]*qty/lot[0];lot[0]-=qty;remaining-=qty
     if lot[0]<1e-8:opens[key].pop(0)
    pnl-=f['cost'];closed.append({'ticker':key,'action':f['action'],'date':f['date'],'pnl_usd':round(pnl,2),'return_on_cost':round(pnl/basis,5) if basis else None})
  decisions=[x for x in events if x['ranked_candidates']]
  flat=[c for x in decisions for c in x['ranked_candidates']]
  negative=sum(c['momentum_screen_score']<=0 for c in flat if c['momentum_screen_score'] is not None)
  order_count=sum(len(x['order_details']) for x in events)
  out['folds'].append({'period':[fold['start'],fold['end_exclusive']],'cagr':fold['metrics']['cagr'],'benchmark':fold['benchmarks'],'exposure':fold['metrics']['exposure'],'fills':len(fills),'decisions':len(events),'orders':order_count,'mean_ranked_screen_score':round(statistics.mean(c['momentum_screen_score'] for c in flat if c['momentum_screen_score'] is not None),5) if flat else None,'nonpositive_screen_score_fraction':round(negative/len(flat),4) if flat else None,'closed_trades':len(closed),'closed_pnl_usd':round(sum(x['pnl_usd'] for x in closed),2),'winners':sum(x['pnl_usd']>0 for x in closed),'losers':sum(x['pnl_usd']<0 for x in closed),'top_winners':sorted(closed,key=lambda x:x['pnl_usd'],reverse=True)[:5],'top_losers':sorted(closed,key=lambda x:x['pnl_usd'])[:5],'screened_symbols':sorted({x['ticker'] for e in events for x in e['screened_candidates']}),'position_target':d['manager']['size_scale']*.06,'notes':['Replay contains only a 16-symbol alphabetically selected development subset','No counterfactual attribution to individual stock benchmark available from this replay']})
 return out
if __name__=='__main__':
 r=diagnose(sys.argv[1]);target=Path(sys.argv[2]);target.write_text(json.dumps(r,indent=2));print(json.dumps({'output':str(target),'folds':[{k:v for k,v in x.items() if k in ('period','exposure','fills','closed_pnl_usd','nonpositive_screen_score_fraction','mean_ranked_screen_score')} for x in r['folds']]},indent=2))
