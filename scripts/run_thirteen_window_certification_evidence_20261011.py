#!/usr/bin/env python3
"""Execute evidence tests and record explicit scientific gaps. Never grant certification."""
import datetime,hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
TESTS=['test_thirteen_window_oct09_seed_policy_20261011.py','test_thirteen_window_real_data_invariants_20261011.py','test_thirteen_window_calendar_integrity_20261011.py','test_thirteen_window_empirical_null_20261011.py','test_thirteen_window_historical_cash_20261011.py','test_thirteen_window_interrupted_worker_20261011.py','test_thirteen_window_regime_execution_20261011.py','test_thirteen_window_multistock_execution_20261011.py','test_thirteen_window_statistical_guard_20261011.py']
checks=[]
for name in TESTS:
 p=ROOT/'scripts'/name
 try:
  r=subprocess.run([sys.executable,str(p)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=90)
  checks.append({'test':name,'passed':r.returncode==0,'exit_code':r.returncode,'stdout':r.stdout[-1500:],'stderr':r.stderr[-1000:],'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 except subprocess.TimeoutExpired:
  checks.append({'test':name,'passed':False,'reason':'TIMEOUT'})
# All gates require evidence from the actual frozen runner, not independent smoke tests.
gaps=['CAUSAL_POINT_IN_TIME_PROVENANCE_NOT_CERTIFIED','FROZEN_ORACLE_CRASH_INTERVALS_USE_RETROSPECTIVE_PEAK_TROUGH_NOT_LIVE_CAUSAL_SIGNALS','ADAPTIVE_GA_MULTIPLE_TESTING_NOT_IN_SELECTION','ADAPTIVE_MARKET_BLOCK_BOOTSTRAP_CALIBRATION_MISSING','HISTORICAL_EXECUTION_AND_CATASTROPHIC_RISK_NOT_CERTIFIED','FULL_PRODUCTION_EVALUATOR_KILL_RESTART_NOT_CERTIFIED','FULL_AUTHORIZED_RUNNER_DRY_RUN_NOT_PERFORMED']
report={'status':'BLOCKED','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'test_count':len(checks),'tests_passed':sum(c['passed'] for c in checks),'tests':checks,'scientific_gaps':gaps,'certification_granted':False,'protected_heldouts_accessed':False,'horizon_ga_launched':False}
out=ROOT/'Research/Preparation/horizon_generational_20261010/thirteen_window_executable_evidence_20261011.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'BLOCKED','tests_passed':report['tests_passed'],'tests_total':len(checks),'failures':[x['test'] for x in checks if not x['passed']],'scientific_gaps':gaps},indent=2))
sys.exit(2)
