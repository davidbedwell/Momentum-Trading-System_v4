#!/usr/bin/env python3
"""Generate fail-closed, non-executing transition manifest for benchmark."""
import json,pathlib,datetime
from scripts.stage2_window_conveyor_20261011 import BASE,WINDOWS,state
active=[]
for w in WINDOWS:
 d=BASE if w==WINDOWS[0] else BASE/f'window_{w[0]:02d}_{w[1]:02d}'
 s=state(d)
 if s and not s.get('completed'):active.append({'window':list(w),'generation':s['generation'],'pending':(d/'pending.json').exists()})
assert len(active)==2,active
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PREPARED_NOT_EXECUTED','active':active,'plans':[{'slots':2,'workers_per_window':14},{'slots':3,'workers_per_window':9},{'slots':4,'workers_per_window':7}],'guardrails':{'minimum_mem_available_gib':16,'maximum_swap_used_gib':4,'abort_on_oom':True,'abort_on_checkpoint_or_journal_failure':True,'no_duplicate_window_launch':True,'keep_frozen_scientific_config':True},'transition_requirements':['pause controller scheduling without losing existing jobs','stop existing runners only after checkpoint and pending journal integrity verified','ensure no orphan worker children remain','resume same windows with changed worker counts','measure equal-duration evaluations and generations per hour','restore two-window configuration on guardrail breach'],'automated_transition_armed':False}
p=BASE/'concurrency_transition_plan.json';p.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
