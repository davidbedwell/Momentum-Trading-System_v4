"""Isolated structural candidate evaluator with cache and immutable trial provenance."""
import hashlib,json,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6.structural_independent_v2_20261022.development_feedback_ledger import DevelopmentLedger
from ga6.portfolio_pareto_20261021 import fitness
from ga6.structural_independent_v2_20261022.structural_manifest import StructuralManifest
from ga5_redesign.canonical_engine import ResultCache

_WORKER_PREPARED=None
_WORKER_POLICY=None

def _init_worker(prepared,policy):
 global _WORKER_PREPARED,_WORKER_POLICY
 _WORKER_PREPARED=prepared;_WORKER_POLICY=policy

def _replay_worker(candidate):
 return candidate.replay(_WORKER_PREPARED,**_WORKER_POLICY)

class StructuralBatch:
 def __init__(self,directory,data_hash,policy_hash,code_hash):
  self.root=Path(directory);self.root.mkdir(parents=True,exist_ok=True)
  self.data_hash=data_hash;self.policy_hash=policy_hash;self.code_hash=code_hash
  self.cache=ResultCache(self.root/'structural_evaluations.sqlite')
  self.ledger=DevelopmentLedger(self.root/'structural_trials.sqlite')
  self.manifest=StructuralManifest(self.root/'structural_manifest.sqlite')
 def evaluate(self,candidates,prepared,policy,generation,origins=None,workers=1):
  if origins is None:origins=['new_structures']*len(candidates)
  if len(origins)!=len(candidates):raise ValueError('Missing activity provenance')
  if workers<1:raise ValueError('workers must be positive')
  results=[];pending=[];metadata=[]
  for index,(candidate,activity) in enumerate(zip(candidates,origins)):
   if not isinstance(candidate,StructuralCandidate):raise TypeError('Expected structural candidate')
   trial_id=hashlib.sha256(f'{self.code_hash}:{self.data_hash}:{self.policy_hash}:{generation}:{index}:{candidate.identity()}'.encode()).hexdigest()
   cache_key=hashlib.sha256(f'{self.code_hash}:{self.data_hash}:{self.policy_hash}:{candidate.identity()}'.encode()).hexdigest()
   result=self.cache.get(cache_key)
   if result is None:pending.append((index,candidate,cache_key))
   metadata.append((trial_id,cache_key,candidate,activity,result))
  started=time.monotonic()
  if pending:
   if workers==1:completed=[c.replay(prepared,**policy) for _,c,_ in pending]
   else:
    with ProcessPoolExecutor(max_workers=workers,initializer=_init_worker,initargs=(prepared,policy)) as pool:
     completed=list(pool.map(_replay_worker,(c for _,c,_ in pending)))
   for (index,candidate,cache_key),result in zip(pending,completed):
    self.cache.put(cache_key,result)
    trial_id,ck,c,a,_=metadata[index];metadata[index]=(trial_id,ck,c,a,result)
  elapsed=max(0.,time.monotonic()-started)/max(1,len(pending))
  for trial_id,cache_key,candidate,activity,result in metadata:
   existing=self.ledger.db.execute('SELECT chromosome_id,activity,niche,generation,role FROM trials WHERE trial_id=?',(trial_id,)).fetchone()
   expected=(candidate.identity(),activity,candidate.genome.niche,generation,'discovery')
   self.manifest.record(trial_id,candidate,activity,generation,'discovery')
   if existing is None:self.ledger.record_trial(trial_id,*expected[:3],generation,'discovery','full_replay',elapsed)
   elif existing!=expected:raise ValueError('Conflicting replay provenance')
   results.append((fitness(result),candidate,result))
  return results
 def close(self):
  self.cache.close();self.ledger.close();self.manifest.close()
