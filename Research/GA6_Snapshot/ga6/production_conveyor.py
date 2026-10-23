#!/usr/bin/env python3
"""Fail-closed GA6 production conveyor. No unverified scientific gates waived."""
import json,subprocess,sys,time,traceback
from pathlib import Path
root=Path('/opt/mts/ga6');out=root/'runs'/'production_conveyor_v1';out.mkdir(parents=True,exist_ok=True)
state=out/'status.json';log=out/'conveyor.log';diagnostic=root/'runs'/'automated_recovery_v1'/'automation_status.json'
def mark(phase,**extra):state.write_text(json.dumps({'phase':phase,'time':time.time(),**extra},indent=2))
def wait_for_diagnostic():
 while True:
  if diagnostic.exists():
   s=json.loads(diagnostic.read_text());phase=s.get('phase')
   if phase=='PASS':return
   if phase=='FAILED':raise RuntimeError('Automated diagnostic failed: '+str(s.get('error')))
  mark('WAITING_FOR_DIAGNOSTIC',diagnostic_status=phase if diagnostic.exists() else 'NOT_STARTED')
  time.sleep(15)
def preflight():
 checks={
  'checkpoint_resume':'PASS',
  'portfolio_accounting':'PENDING_INTEGRATION',
  'chronological_out_of_sample':'PENDING_CERTIFICATION',
  'research_governance':'PENDING_CERTIFICATION',
  'production_500_population':'PENDING_PREFLIGHT'}
 (out/'production_gate.json').write_text(json.dumps(checks,indent=2))
 if any(v!='PASS' for v in checks.values()):raise RuntimeError('Production blocked by incomplete required checks; see production_gate.json')
def launch():
 cmd=['/opt/mts/.venv/bin/python','-u',str(root/'production_runner.py'),'--features','/opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet','--policy-file','/opt/mts/ga5_redesign/exploratory79_policy.json','--output',str(root/'runs'/'ga6_production_v1'),'--population','200','--workers','8','--generations','1000','--stagnation','100','--entry-mode','unrestricted','--production']
 mark('PRODUCTION_RUNNING',command=cmd)
 with log.open('a') as f:
  result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Production runner failed exit '+str(result.returncode))
 mark('PRODUCTION_COMPLETED')
try:
 mark('STARTED');wait_for_diagnostic();mark('PREFLIGHT');preflight();launch()
except Exception as e:
 mark('BLOCKED',reason=str(e),traceback=traceback.format_exc());sys.exit(1)
