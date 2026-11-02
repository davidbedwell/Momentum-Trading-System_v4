"""Audit whether authentic frozen GA6 candidates can run on synthetic OHLCV.

Does not substitute invented feature values for required native indicators.
"""
import json,sqlite3
from pathlib import Path
from collections import Counter
import pandas as pd
from ga5_feature_adapter import LEGACY
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
from discovery.competitive_ga.synthetic_adapter import load_fsynth
ROOT=Path('/opt/mts/synthetic-market-lab')
DB='/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite'
OUT=ROOT/'reports/synthetic_native_ga6_feature_gate_20261027.json'
def leaves(n):
    return {n['family']} if 'family' in n else set().union(*(leaves(x) for x in n['children']))
def main():
    db=sqlite3.connect(DB)
    ids=[x[0] for x in db.execute('select id from chromosomes limit 400')]
    freq=Counter();examples={}
    for sid in ids:
        row=db.execute('select definition from chromosomes where id=?',(sid,)).fetchone()
        c=StructuralCandidate.restore(json.loads(row[0]));g=c.genome
        needed={getattr(g,k) for k in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature')}|leaves(c.entry_tree)
        for k in needed:
            freq[k]+=1
            examples.setdefault(k,sid)
    synthetic=[]
    for i in range(1,6):
        d=load_fsynth(ROOT/f'runs/five_iteration_inputs/universe_{i}')
        synthetic.append({'universe':i,'rows':len(d),'stocks':int(d.Ticker.nunique()),'sessions':int(d.Date.nunique()),
                          'start':str(d.Date.min().date()),'end':str(d.Date.max().date())})
    output={'status':'FEATURE_PARITY_GATE_NOT_TRAINING','candidate_count':len(ids),
        'synthetic_universes':synthetic,'required_native_features':dict(freq.most_common()),
        'feature_example_chromosome':examples,
        'warning':'Synthetic bars have OHLCV only. Native GA6 chromosomes require additional features, including archived GA4 cross-sectional ranks and breadth. Reconstruct causally with identical definitions and scaling before native proposal replay. Do not impute or substitute momentum-only baseline.'}
    OUT.write_text(json.dumps(output,indent=2))
    print(json.dumps({'status':output['status'],'candidates':len(ids),'features':len(freq),'universes':synthetic,'top_features':freq.most_common(15)},indent=2))
if __name__=='__main__':main()
