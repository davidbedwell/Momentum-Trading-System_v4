"""Claude tool execution: unprivileged Python, no network, bounded resources, read-only evidence."""
import json,os,pathlib,resource,subprocess,tempfile
DATA=pathlib.Path('/opt/mts/ga6/runs/independent_review')
FILES=('trade_entries_prior_features.parquet','market_indicator_panel.parquet','daily_equity.parquet','daily_holdings.parquet','executed_fills.parquet')
PY='/opt/mts/.venv/bin/python'
def execute(code):
 if not isinstance(code,str) or len(code)>12000:return {'error':'Code must be a string of at most 12000 characters'}
 with tempfile.TemporaryDirectory(prefix='ga6_claude_',dir='/tmp') as work:
  os.chmod(work,0o777)
  script=pathlib.Path(work)/'analysis.py';script.write_text('import pandas as pd\nimport numpy as np\nimport duckdb\nfrom pathlib import Path\nDATA=Path('+repr(str(DATA))+')\n'+code);os.chmod(script,0o644)
  def limits():
   resource.setrlimit(resource.RLIMIT_CPU,(35,36));resource.setrlimit(resource.RLIMIT_AS,(5*1024**3,5*1024**3));resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2));resource.setrlimit(resource.RLIMIT_NPROC,(30,30))
  try:
   p=subprocess.run(['/usr/bin/unshare','-n','--', '/usr/bin/setpriv','--reuid=65534','--regid=65534','--clear-groups',PY,'-I',str(script)],cwd=work,env={'HOME':work,'TMPDIR':work,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PATH':'/usr/bin:/bin'},capture_output=True,text=True,timeout=45,preexec_fn=limits)
   return {'exit_code':p.returncode,'stdout':p.stdout[:18000],'stderr':p.stderr[-3500:],'truncated':len(p.stdout)>18000}
  except subprocess.TimeoutExpired:return {'error':'45-second execution limit exceeded'}
if __name__=='__main__':
 print(json.dumps(execute('print(pd.read_parquet(DATA/"trade_entries_prior_features.parquet").shape)')))
