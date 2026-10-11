"""Prove the real runner cannot create an output directory without authorization."""
import pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
 out=pathlib.Path(d)/'must_not_exist'
 p=subprocess.run([sys.executable,str(ROOT/'scripts/run_thirteen_window_normal_20261011.py'),'--output',str(out),'--generations','1','--workers','1','--batch','20','--seed-size','20'],cwd=ROOT,capture_output=True,text=True,timeout=90)
 assert p.returncode!=0 and not out.exists(),(p.returncode,p.stderr[-500:])
 assert '13_WINDOW_NOT_CERTIFIED' in p.stderr or 'NEW_STUDY_SERVER_NOT_AUTHORIZED' in p.stderr
print('REAL_RUNNER_NO_AUTH_NO_OUTPUT_PASS')
