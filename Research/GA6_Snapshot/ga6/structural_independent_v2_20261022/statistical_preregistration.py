"""Immutable statistical-test plan, requiring an independently reconciled family."""
import hashlib
import json
from pathlib import Path

REQUIRED=('benchmark','loss_differential','candidate_family_hash','data_fingerprint',
          'calendar_start','calendar_end','block_length','replications','seed',
          'alpha','method','selection_rule','family_trial_count')

def register(path,plan):
 if not isinstance(plan,dict) or any(k not in plan for k in REQUIRED):
  raise ValueError("Missing preregistration field")
 if plan['method'] not in ('synchronized_max_t_screen','synchronized_stepdown_max_t_research'):
  raise ValueError("Unreviewed method")
 if not isinstance(plan['family_trial_count'],int) or plan['family_trial_count']<1:
  raise ValueError("Unreconciled candidate family")
 if not 0<plan['alpha']<1 or plan['replications']<199 or plan['block_length']<2:
  raise ValueError("Invalid statistical plan")
 data=json.dumps(plan,sort_keys=True,separators=(',',':'))
 digest=hashlib.sha256(data.encode()).hexdigest()
 target=Path(path)
 if target.exists():
  previous=target.read_text()
  if previous!=data:raise PermissionError("Preregistered test plan cannot change")
 else:
  target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('x') as stream:stream.write(data)
 return digest

def verify(path,expected_digest):
 data=Path(path).read_text()
 if hashlib.sha256(data.encode()).hexdigest()!=expected_digest:
  raise PermissionError("Statistical preregistration fingerprint changed")
 return json.loads(data)
