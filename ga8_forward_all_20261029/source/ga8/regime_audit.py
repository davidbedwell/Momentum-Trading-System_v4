"""Post-evolution exploratory regime audit. Read-only against GA8 run; never feeds optimizer."""
import argparse, json
from pathlib import Path
from collections import defaultdict
import numpy as np
from .engine import load_panel, replay, Gene, Manager
from .run import RAW

def candidates(journal, limit):
    # Select diversity by unique chromosome ID, retaining annual leaders and strong alternatives.
    best={}
    for line in open(journal):
        entry=json.loads(line)
        for r in entry['rows']:
            m=r['metrics']; score=(bool(m['feasible']),m['cagr'], -m['max_drawdown'])
            if r['id'] not in best or score>best[r['id']][0]:best[r['id']]=(score,r)
    leaders=sorted(best.values(),key=lambda x:x[0],reverse=True)
    return [r for _,r in leaders[:limit]]

def profile(panel, row):
    def tup(x):return tuple(map(tup,x)) if isinstance(x,list) else x
    genes=[Gene(**dict(g,entry_tree=tup(g.get('entry_tree',())))) for g in row['genes']]
    manager=Manager(**row['manager'])
    results={}
    for year in range(2022,2026):
        result=replay(panel,genes,manager,f'{year}-01-01',f'{year+1}-01-01',True)
        equity=result['equity']; buckets=defaultdict(lambda:dict(days=0,active_days=0,returns=[],max_daily_loss=0.))
        # Classify each session using contemporaneous broad-market breadth and volatility.
        for previous,current in zip(equity,equity[1:]):
            ix=panel.dates.get_indexer([current['date']])[0]
            breadth=panel.breadth[ix]
            vol=np.nanmedian(np.abs(panel.returns[max(0,ix-19):ix+1]))
            regime=('bear' if breadth<.4 else 'bull' if breadth>.6 else 'mixed') + ('_volatile' if vol>.018 else '_calm')
            b=buckets[regime]; r=current['nav']/previous['nav']-1
            b['days']+=1;b['active_days']+=int(current['holdings']>0);b['returns'].append(float(r));b['max_daily_loss']=min(b['max_daily_loss'],float(r))
        summary={}
        for name,b in buckets.items():
            rr=np.array(b.pop('returns'));b['net_compound_return']=float(np.prod(1+rr)-1);b['mean_daily_return']=float(rr.mean());summary[name]=b
        results[str(year)]=dict(metrics=result['metrics'],regimes=summary)
    return dict(id=row['id'],genes=row['genes'],manager=row['manager'],discovery_phase=row.get('phase'),years=results,
      caution='Exploratory replays only; regime labels based on current-day breadth and realized trailing volatility. No OOS claims, no automatic specialist certification.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--journal',required=True);ap.add_argument('--output',required=True);ap.add_argument('--limit',type=int,default=20);a=ap.parse_args()
    panel,_=load_panel(RAW,end='2026-01-01')
    output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w') as f:
        for r in candidates(a.journal,a.limit):
            f.write(json.dumps(profile(panel,r),allow_nan=False)+'\n');f.flush()
    print(json.dumps(dict(output=str(output),chromosomes=a.limit,scope='exploratory only')))
if __name__=='__main__':main()
