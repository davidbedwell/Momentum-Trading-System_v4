"""DEV80-only per-genome attribution of exit-pilot eligibility failures."""
import json,pathlib,collections
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008');P=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint')
f=pd.read_parquet(P/'dev80_predictors.parquet');raw=pd.read_parquet(P/'dev80_raw.parquet')
assert len(f)==len(raw) and np.array_equal(f.security_id.to_numpy(),raw.security_id.to_numpy()) and np.array_equal(pd.to_datetime(f.effective_date).to_numpy(),pd.to_datetime(raw.date).to_numpy())
a=np.load(R/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz');end=a['endpoint_return'][:,62];d=pd.to_datetime(f.effective_date)
train=(d<'2016-01-01').to_numpy();test=(d>='2021-01-01').to_numpy()
compiler=CausalSignalCompiler(f);g=[json.loads(x) for x in (R/'all_candidates.jsonl').open()];out=[]
for row in g:
 mask=np.logical_and.reduce([compiler.compile(family,gene) for family,gene in row['chromosomes']]);cost=a['long_roundtrip'] if row['side']=='LONG' else a['short_roundtrip'];cost=cost[:,62] if cost.ndim==2 else cost
 ok=np.isfinite(end)&np.isfinite(cost)
 out.append({'index':row['index'],'side':row['side'],'all_signals':int(mask.sum()),'train_signals':int((mask&train).sum()),'test_signals':int((mask&test).sum()),'train_valid63':int((mask&train&ok).sum()),'test_valid63':int((mask&test&ok).sum()),'train_missing63':int((mask&train&~ok).sum()),'test_missing63':int((mask&test&~ok).sum())})
 if len(out)%250==0:print('AUDITED',len(out),flush=True)
summary={'genomes':len(out),'zero_train_signals':sum(x['train_signals']==0 for x in out),'zero_test_signals':sum(x['test_signals']==0 for x in out),'train_insufficient63':sum(x['train_valid63']<40 for x in out),'test_insufficient63':sum(x['test_valid63']<20 for x in out),'train_signal_count':sum(x['train_signals'] for x in out),'test_signal_count':sum(x['test_signals'] for x in out),'train_missing63':sum(x['train_missing63'] for x in out),'test_missing63':sum(x['test_missing63'] for x in out),'example_indices':{str(i):next(x for x in out if str(x['index'])==str(i)) for i in (1,865,1748,2615,3487,4350)},'interpretation':'Eligibility requires a 63-session endpoint even when a shorter exit could be executable. Zero signal counts are distinct from path gaps. 63-session missingness includes ticker end-of-series and any invalid prices or costs.'}
folder=R/'exit_ga_bounded_pilot_20261009';folder.mkdir(exist_ok=True);(folder/'path_rejection_audit.json').write_text(json.dumps({'summary':summary,'per_genome':out},indent=2));print(json.dumps(summary,indent=2))
