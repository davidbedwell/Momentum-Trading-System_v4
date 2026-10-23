#!/usr/bin/env python3
"""Unattended GA6 diagnostic generation and checkpoint recovery verification; never production."""
import json,subprocess,sys,time,traceback
from pathlib import Path
root=Path('/opt/mts/ga6');out=root/'runs'/'automated_recovery_v1';out.mkdir(parents=True,exist_ok=True)
log=out/'automation.log';status=out/'automation_status.json'
base=[str(Path('/opt/mts/.venv/bin/python')),'-u',str(root/'runner.py'),'--features','/opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet','--policy-file','/opt/mts/ga5_redesign/exploratory79_policy.json','--output',str(out),'--population','26','--workers','8','--entry-mode','unrestricted','--diagnostic-only']
def mark(phase,**kw):
 status.write_text(json.dumps({'phase':phase,'time':time.time(),**kw},indent=2))
def execute(cmd,phase):
 mark(phase,command=cmd)
 with log.open('a') as f:
  f.write('\nSTART '+phase+' '+repr(cmd)+'\n');f.flush()
  result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=3600)
 if result.returncode:raise RuntimeError(f'{phase} failed exit={result.returncode}; see {log}')
try:
 cp=out/'checkpoint_unified.json'
 if not cp.exists():execute(base+['--generations','1'],'initial_generation')
 execute([base[0],str(root/'test_checkpoint_resume_integrity.py'),str(cp)],'checkpoint_validation')
 execute(base+['--generations','2'],'resume_generation_two')
 execute([base[0],str(root/'test_checkpoint_resume_integrity.py'),str(cp)],'resumed_checkpoint_validation')
 report=json.loads((out/'report.json').read_text())
 assert len(report['history'])==2 and report['evaluations']==52
 assert all(h['niches_represented']==13 for h in report['history'])
 mark('PASS',generations=2,evaluations=52,niches=13)
except Exception as e:
 mark('FAILED',error=str(e),traceback=traceback.format_exc())
 sys.exit(1)
