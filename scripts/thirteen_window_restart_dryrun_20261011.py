"""Small crash/restart journal exercise, no paid GA or heldout data."""
import json,pathlib,tempfile,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.evolution_safety_20261010 import atomic_json,durable_append,recover_jsonl

def exercise():
 with tempfile.TemporaryDirectory() as d:
  out=pathlib.Path(d);p=out/'candidates.jsonl';s=out/'state.json'
  records=[{'generation':1,'genome_hash':'g1','parent_hashes':['a','b']},{'generation':1,'genome_hash':'g2','parent_hashes':['c','d']}]
  durable_append(p,records)
  atomic_json(s,{'generation':0,'pending_generation':1,'seed':20261011})
  restored=recover_jsonl(p);state=json.loads(s.read_text())
  assert restored==records and state['pending_generation']==1
  durable_append(out/'evaluations.jsonl',[{'genome_hash':'g1','status':'EVALUATED_UNCERTIFIED'}])
  todo=[r for r in restored if r['genome_hash'] not in {x['genome_hash'] for x in recover_jsonl(out/'evaluations.jsonl')}]
  assert [x['genome_hash'] for x in todo]==['g2']
  durable_append(out/'evaluations.jsonl',[{'genome_hash':'g2','status':'EVALUATED_UNCERTIFIED'}])
  atomic_json(s,{'generation':1,'seed':20261011})
  assert len(recover_jsonl(out/'evaluations.jsonl'))==2
 print('RESTART_JOURNAL_SMOKE_PASS_NOT_FULL_RUNNER_CERTIFICATION')
if __name__=='__main__':exercise()
