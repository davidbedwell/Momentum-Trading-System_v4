"""Read-only, paired selection comparison on identical evaluated GA8 candidates.
Does not claim new offspring profitability without replay.
"""
import argparse,json,random
from collections import Counter
from .engine import rank
from .long_run import decode

def signature(row):
    genes,_=decode(row)
    return tuple(sorted((g.family,g.niche,g.op,g.exit_family) for g in genes))

def select(rows,n,diverse=False):
    ordered=sorted(rows,key=rank,reverse=True)
    if not diverse:return ordered[:n]
    selected=[];used=set();counts=Counter()
    # Keep champion, then reserve up to 40% for profitable structural coverage.
    if ordered:selected.append(ordered[0]);used.add(ordered[0]['id']);counts[signature(ordered[0])]+=1
    target=max(1,int(n*.4))
    for row in ordered:
        if len(selected)>=target:break
        sig=signature(row)
        if row['id'] in used or counts[sig] or not row['metrics']['feasible']:continue
        selected.append(row);used.add(row['id']);counts[sig]+=1
    for row in ordered:
        if len(selected)>=n:break
        if row['id'] not in used:selected.append(row);used.add(row['id'])
    return selected

def stats(rows):
    return dict(count=len(rows),unique_structures=len({signature(r) for r in rows}),feasible=sum(r['metrics']['feasible'] for r in rows),mean_cagr=sum(r['metrics']['cagr'] for r in rows)/max(1,len(rows)),best_cagr=max((r['metrics']['cagr'] for r in rows),default=None),families=sorted({g['family'] for r in rows for g in r['genes']}),niches=sorted({g['niche'] for r in rows for g in r['genes']}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--journal',required=True);ap.add_argument('--generations',type=int,default=5);ap.add_argument('--parents',type=int,default=100);a=ap.parse_args()
    with open(a.journal) as f:
        for i,line in enumerate(f):
            if i>=a.generations:break
            data=json.loads(line);rows=data['rows'];n=min(a.parents,len(rows));old=select(rows,n);new=select(rows,n,True)
            print(json.dumps(dict(generation=data['generation'],baseline=stats(old),diversity_selection=stats(new),common_ids=len({r['id'] for r in old}&{r['id'] for r in new}))))
if __name__=='__main__':main()
