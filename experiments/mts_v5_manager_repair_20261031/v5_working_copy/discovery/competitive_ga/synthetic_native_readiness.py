"""Audit real GA6 feature coverage against synthetic causal panels; read-only."""
import json,sqlite3
from pathlib import Path
import pandas as pd
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
from ga5_feature_adapter import LEGACY
from discovery.competitive_ga.synthetic_native_feature_gate import leaves
ROOT=Path('/opt/mts/synthetic-market-lab')
DB='/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite'
def run():
 with sqlite3.connect(DB) as db:
  total=db.execute('select count(*) from chromosomes').fetchone()[0]
  records=db.execute('select id,definition from chromosomes limit 400').fetchall()
 panels=[]
 for i in range(1,6):
  p=ROOT/f'runs/causal_native_features/universe_{i}_ga4_native.parquet'
  schema=pd.read_parquet(p).columns if p.exists() else []
  panels.append({'universe':i,'exists':p.exists(),'features':len(schema)})
 available=set(pd.read_parquet(ROOT/'runs/causal_native_features/universe_1_ga4_native.parquet').columns)
 available.update(pd.read_parquet(ROOT/'runs/causal_native_features/universe_1_eight_family.parquet').columns)
 missing={};covered=0
 for sid,definition in records:
  c=StructuralCandidate.restore(json.loads(definition));g=c.genome
  needed={getattr(g,k) for k in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature')}|leaves(c.entry_tree)
  absent=sorted(str(f) for f in needed if LEGACY.get(f,f) not in available)
  if absent:missing[sid]=absent
  else:covered+=1
 result={'catalogue_total':total,'sampled':len(records),'feature_complete_in_sample':covered,'missing_feature_counts':{k:sum(k in v for v in missing.values()) for k in sorted(set(x for v in missing.values() for x in v))},'panels':panels,'native_execution_certified':False,'note':'Feature-name coverage only; native GA6 feature scaling and evaluator parity still require verification'}
 out=ROOT/'reports/synthetic_native_readiness.json';out.write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
