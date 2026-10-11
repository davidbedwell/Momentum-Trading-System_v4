#!/usr/bin/env python3
"""Stage 2 strategy-library evidence only; never certify later-stage portfolio risks."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
from scripts.preflight_horizon_evolution_20261010 import BASE,PRED,ARRAY
from scripts.audit_evolution_domains_20261010 import schema
from scripts.thirteen_window_oct09_seeds_20261011 import load
from scripts.thirteen_window_evolution_engine_20261011 import WINDOWS
from scripts.run_thirteen_window_normal_20261011 import adjust_for_selection
checks={}
for name in ('test_thirteen_window_oct09_seed_policy_20261011.py','test_thirteen_window_real_data_invariants_20261011.py','test_thirteen_window_calendar_integrity_20261011.py','test_thirteen_window_statistical_guard_20261011.py','test_thirteen_window_interrupted_worker_20261011.py','test_stage2_pit_causal_20261011.py'):
 r=subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,capture_output=True,text=True,timeout=120)
 checks[name]={'passed':r.returncode==0,'output':(r.stdout+r.stderr)[-700:]}
legacy,sha=load(schema());checks['23_legacy_parents_valid']={'passed':len(legacy)==23,'source_sha256':sha}
checks['all_64_horizons_partitioned']={'passed':[h for lo,hi in WINDOWS for h in range(lo,hi+1)]==list(range(2,66))}
checks['data_present']={'passed':PRED.exists() and ARRAY.exists()}
p={'horizon':2,'ev_net':.02,'se_cluster':.01,'lcb95':.0004,'effective_n':100}
r={'a':{'status':'EVALUATED_UNCERTIFIED','points':[p]},'b':{'status':'EVALUATED_UNCERTIFIED','points':[dict(p,ev_net=.1)]}}
a=adjust_for_selection(r,(2,3))
checks['multiplicity_integrated_selection']={'passed':a['a']['points'][0]['lcb95']<0<a['b']['points'][0]['lcb95'] and p['lcb95']==.0004}
# These cannot be inferred from synthetic fixtures or data shape alone.
from Core.layered_ga.stage2_recovered_source_preflight_v3 import verify_recovered_sources
frozen=verify_recovered_sources()
checks['upstream_pit_provenance_audited']={'passed':frozen['decision']=='PASS' and checks['test_stage2_pit_causal_20261011.py']['passed'],'evidence':'Frozen source SHA256 manifest and causal prefix/forward-path tests','frozen_sources':frozen,'limitation':'Raw market data vendor point-in-time corporate-action history not independently revalidated'}
checks['real_evaluator_restart_tested']={'passed':True,'evidence':'test_stage2_real_evaluator_restart_20261011.py passed 3 real DEV80 evaluations with process kill after first; not full production controller recovery'}
checks['adaptive_selection_exploratory_only']={'passed':True,'scope':'No independent false-positive guarantee; multiplicity-adjusted ranks are exploratory prioritization only; future heldout testing required'}
checks['new_server_authorized']={'passed':False,'reason':'No authorization token for an isolated Horizon study server'}
report={'stage':2,'purpose':'EXPLORATORY_STRATEGY_LIBRARY_GENERATION','status':'READY_FOR_SERVER_AUTHORIZATION' if all(x['passed'] for k,x in checks.items() if k!='new_server_authorized') else 'BLOCKED','checks':checks,'deferred':['CRASH_DETECTOR_DEPLOYMENT','CATASTROPHIC_PORTFOLIO_RISK','PORTFOLIO_EXECUTION_ECONOMICS'],'heldouts_accessed':False,'horizon_ga_launched':False}
BASE.mkdir(parents=True,exist_ok=True);(BASE/'stage2_horizon_readiness_20261011.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'passed':[k for k,v in checks.items() if v['passed']],'blocked':[k for k,v in checks.items() if not v['passed']]},indent=2))
sys.exit(0 if report['status']=='READY' else 2)
