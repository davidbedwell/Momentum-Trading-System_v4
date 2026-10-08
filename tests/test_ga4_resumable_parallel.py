import tempfile,unittest
from Core.layered_ga.ga4_resumable_parallel import run
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces
from Core.layered_ga.stage2_evaluator_v3 import CurveEvaluation

def synthetic(ch):
 score=float(sum(len(str(x)) for x in ch))/1000
 return CurveEvaluation('LONG',({'horizon':1,'ev_net':score,'lcb95':score-0.01,'mae_mean':-0.1,'mae_tail5':-0.2},),(),())

def synthetic_pair(ch):
 return synthetic(ch),{"chromosomes":str(ch)}

class ParallelResumeTests(unittest.TestCase):
 def test_replay_and_config_guard(self):
  with tempfile.TemporaryDirectory() as tmp:
   kw=dict(seed=42,population_size=6,generations=3,workers=2,checkpoint_dir=tmp,identity='synthetic-test-v1')
   a=run(stage2_search_spaces(),synthetic,**kw)
   b=run(stage2_search_spaces(),synthetic,**kw)
   self.assertEqual(a,b)
   self.assertEqual(a['individuals'],18)
   self.assertEqual(len(a['generations']),3)
   with self.assertRaisesRegex(ValueError,'mismatch'):
    run(stage2_search_spaces(),synthetic,**(kw|{'seed':43}))
 def test_coordinator_persistence_and_resume(self):
  with tempfile.TemporaryDirectory() as tmp:
   records=[]
   def persist(record):records.append(record)
   def pair(ch):return synthetic(ch),{"key":str(ch)}
   # Local functions cannot be pickled with spawn, so use a module-level worker.
   a=run(stage2_search_spaces(),synthetic_pair,seed=7,population_size=4,generations=2,workers=2,checkpoint_dir=tmp,identity="persist",persist=persist)
   self.assertEqual(len(records),a["unique_evaluations"])
   b=run(stage2_search_spaces(),synthetic_pair,seed=7,population_size=4,generations=2,workers=2,checkpoint_dir=tmp,identity="persist",persist=persist)
   self.assertEqual(a,b)
   self.assertEqual(len(records),a["unique_evaluations"])
 def test_crash_before_checkpoint_recovers_without_duplicate_records(self):
  with tempfile.TemporaryDirectory() as tmp:
   persisted={}
   calls=[0]
   def interrupt_once(record):
    calls[0]+=1
    if calls[0]==2:raise RuntimeError('injected interruption')
    persisted[str(record)]=record
   kw=dict(seed=21,population_size=4,generations=3,workers=2,checkpoint_dir=tmp,identity='crash-recovery')
   with self.assertRaisesRegex(RuntimeError,'injected interruption'):
    run(stage2_search_spaces(),synthetic_pair,**kw,persist=interrupt_once)
   def persist(record):persisted[str(record)]=record
   recovered=run(stage2_search_spaces(),synthetic_pair,**kw,persist=persist)
   self.assertEqual(len(persisted),recovered['unique_evaluations'])
   again=run(stage2_search_spaces(),synthetic_pair,**kw,persist=persist)
   self.assertEqual(recovered,again)
 def test_explicit_budget_required(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):
    run(stage2_search_spaces(),synthetic,seed=1,population_size=0,generations=3,workers=2,checkpoint_dir=tmp,identity='x')

if __name__=='__main__':unittest.main()