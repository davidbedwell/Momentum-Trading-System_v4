"""Fail-closed unattended GA6 integration test and readiness pipeline.
Runs only verified tests; never changes production or claims to implement missing code.
"""
import datetime,json,os,pathlib,sqlite3,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'automation';OUT.mkdir(exist_ok=True)
REQUIRED={'structural_grammar_full_portfolio':'test_structural_portfolio_integration.py','sobol_structure_parameters':'test_sobol_structure_integration.py','cheap_medium_full_calibration':'test_multifidelity_calibration.py','adaptive_scheduler':'test_adaptive_scheduler.py','protected_niche_archive':'test_elite_archive.py','end_to_end_launch_preflight':'test_launch_preflight.py'}

def run():
 checks={};env=dict(os.environ,PYTHONPATH='/opt/mts:/opt/mts/ga5_redesign')
 for name,command in [('logic_unit',['-m','unittest','discover','-s',str(ROOT),'-p','test_family_logic.py','-v']),('real_data_signal',['-u',str(ROOT/'signal_replay_smoke.py')])]:
  try:
   p=subprocess.run([sys.executable,*command],cwd='/opt/mts',env=env,capture_output=True,text=True,timeout=120)
   checks[name]={'passed':p.returncode==0,'returncode':p.returncode,'tail':(p.stdout+'\n'+p.stderr)[-1200:]}
  except Exception as e:checks[name]={'passed':False,'error':repr(e)}
 try:
  db=sqlite3.connect(ROOT/'structural_coverage.sqlite');n,unique=db.execute('select count(*),count(distinct id) from structures').fetchone();db.close()
  checks['catalog_integrity']={'passed':n==14652 and unique==n,'count':n,'unique':unique}
 except Exception as e:checks['catalog_integrity']={'passed':False,'error':repr(e)}
 for name,filename in REQUIRED.items():
  path=ROOT/filename
  if not path.exists():checks[name]={'passed':False,'reason':'REQUIRED_INTEGRATION_TEST_NOT_IMPLEMENTED'};continue
  try:
   p=subprocess.run([sys.executable,'-m','unittest',f'ga6.structural_independent_v2_20261022.{path.stem}','-v'],cwd='/opt/mts',env=env,capture_output=True,text=True,timeout=600)
   checks[name]={'passed':p.returncode==0,'returncode':p.returncode,'tail':(p.stdout+'\n'+p.stderr)[-1500:]}
  except Exception as e:checks[name]={'passed':False,'error':repr(e)}
 ready=all(v['passed'] for v in checks.values())
 report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ready':ready,'checks':checks,'production_policy':'NEVER_STOP_OR_SWITCH_AUTOMATICALLY'}
 tmp=OUT/'readiness.tmp';tmp.write_text(json.dumps(report,indent=2));tmp.replace(OUT/'readiness.json')
 with (OUT/'history.jsonl').open('a') as f:f.write(json.dumps({'utc':report['utc'],'ready':ready,'passed':sum(v['passed'] for v in checks.values()),'total':len(checks)})+'\n')
 print(json.dumps({'ready':ready,'passed':sum(v['passed'] for v in checks.values()),'total':len(checks),'missing':[k for k,v in checks.items() if not v['passed']]}))
if __name__=='__main__':run()
