"""Run profitability, drawdown and dedup audit after Diversity completes."""
import json,pathlib,subprocess,sys,time,traceback
root=pathlib.Path('/opt/mts/ga6/runs/post_v3_comparison_20261022');status=root/'sequence_status.json';audit=root/'extended_audit_status.json'
def save(stage,**extra):audit.write_text(json.dumps({'stage':stage,'updated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),**extra},indent=2))
save('waiting_for_diversity_completion')
while True:
 try:
  s=json.loads(status.read_text())
  if s['stage']=='analysis_complete':break
  if s['stage']=='failed_closed':raise RuntimeError('Main sequence failed: '+str(s.get('error')))
 except FileNotFoundError:pass
 time.sleep(15)
save('running_profitability_drawdown_dedup_audit')
with (root/'extended_audit.log').open('w') as log:
 r=subprocess.run(['/opt/mts/.venv/bin/python','/opt/mts/ga6/post_diversity_audit_20261022.py'],cwd='/opt/mts',env={'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin','PYTHONPATH':'/opt/mts:/opt/mts/ga5_redesign'},stdout=log,stderr=subprocess.STDOUT)
if r.returncode:save('audit_failed',returncode=r.returncode);sys.exit(r.returncode)
save('audit_complete',report=str(root/'profitability_drawdown_dedup_report.json'))
