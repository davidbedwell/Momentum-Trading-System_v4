"""Parallel, native GA6 structural decision smoke test on causal synthetic panels.
This checks actual decision execution, NOT trading performance or portfolio parity.
"""
import json,sqlite3
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
from ga5_feature_adapter import LEGACY
from ga5_chromosome_decisions import PositionState
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
from ga6.structural_evolution_v3_20261022.structural_decision import decision
from discovery.competitive_ga.synthetic_native_feature_gate import leaves
ROOT=Path('/opt/mts/synthetic-market-lab')
DB='/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite'
def worker(task):
    ident,record,rows=task
    c=StructuralCandidate.restore(json.loads(record));g=c.genome
    fields={getattr(g,k) for k in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature')}|leaves(c.entry_tree)
    result={'id':ident,'niche':g.niche,'evaluated':0,'entries':0,'missing':0,'errors':[]}
    for r in rows:
        features={f:float(r[LEGACY.get(f,f)]) for f in fields if pd.notna(r.get(LEGACY.get(f,f)))}
        if len(features)!=len(fields):result['missing']+=1;continue
        try:
            action,weight=decision(g,features,PositionState(0,0,0,0),float(r['close']),c.entry_tree)
            result['evaluated']+=1
            if action=='ENTER' and weight>0:result['entries']+=1
        except Exception as e:
            result['errors'].append(str(e));break
    return result

def run(universe=1,count=32,workers=8):
    base=ROOT/'runs/causal_native_features'
    a=pd.read_parquet(base/f'universe_{universe}_ga4_native.parquet')
    b=pd.read_parquet(base/f'universe_{universe}_eight_family.parquet')
    keys=['date','ticker']
    a['date']=pd.to_datetime(a['date']);b['date']=pd.to_datetime(b['date'])
    assert not a.duplicated(keys).any() and not b.duplicated(keys).any()
    cols=keys+[c for c in b if c not in a and c not in keys]
    merged=a.merge(b[cols],on=keys,how='inner',validate='one_to_one')
    assert len(merged)==len(a)==len(b),'native panel key mismatch'
    # One common decision close across stocks; no future-return screening.
    valid_dates=sorted(merged['date'].unique())
    sample=merged.loc[merged['date']==valid_dates[min(300,len(valid_dates)-1)]].sort_values('ticker').head(500)
    rows=sample.to_dict('records')
    with sqlite3.connect(DB) as db: records=db.execute('select id,definition from chromosomes limit ?', (count,)).fetchall()
    with ProcessPoolExecutor(max_workers=workers) as pool: results=list(pool.map(worker,[(ident,definition,rows) for ident,definition in records]))
    report={'universe':universe,'chromosomes':len(results),'workers':workers,'sample_rows':len(rows),'evaluated':sum(x['evaluated'] for x in results),'entries':sum(x['entries'] for x in results),'missing':sum(x['missing'] for x in results),'errors':[x for x in results if x['errors']],'native_signal_executed':True,'portfolio_parity_certified':False}
    out=ROOT/'reports/native_signal_smoke.json';out.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':run()
