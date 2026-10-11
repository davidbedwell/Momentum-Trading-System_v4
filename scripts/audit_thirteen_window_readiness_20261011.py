#!/usr/bin/env python3
"""Read-only, lightweight gate audit; never fabricates scientific certification."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.preflight_horizon_evolution_20261010 import check,BASE,PRED,ARRAY,WINDOWS
from scripts.prepare_horizon_generation_study_20261010 import sha
r=check()
checks={'source_archive_checksums':bool(r['source_manifest_sha256']),'dev80_predictors_present':PRED.is_file(),'dev80_execution_arrays_present':ARRAY.is_file(),'window_count_13':len(WINDOWS)==13,'all_64_horizons_required':r['required_horizons']==list(range(2,66)),'protected_heldouts_not_accessed':r['protected_heldouts_accessed'] is False}
cert=BASE/'thirteen_window_evaluator_certification.json'
checks['scientific_certification_present']=cert.is_file()
checks['scientific_certification_valid']=r['status']=='READY'
checks['evaluator_smoke_pass']=False
p=subprocess.run([sys.executable,str(ROOT/'scripts/test_thirteen_window_horizon_evaluator_20261011.py')],cwd=ROOT,capture_output=True,text=True)
if p.returncode==0:
 try: checks['evaluator_smoke_pass']=json.loads(p.stdout)['status']=='PASS_HORIZON_COVERAGE_ONLY'
 except (ValueError,KeyError):pass
report={'status':'READY_FOR_SECOND_SERVER' if all(checks.values()) else 'ENGINEERING_INCOMPLETE','checks':checks,'blockers':r['reasons'],'smoke_stdout':p.stdout[-400:],'smoke_stderr':p.stderr[-400:],'dev80_predictor_sha256':sha(PRED) if PRED.exists() else None,'dev80_execution_array_sha256':sha(ARRAY) if ARRAY.exists() else None,'protocol':'13 windows; DEV80 only; no crash masking; no protected heldout access'}
( BASE/'second_server_readiness_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
