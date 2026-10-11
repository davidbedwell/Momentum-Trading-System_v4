import os,signal,pathlib
target=[]
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 pid=int(p.name)
 if not 37180<=pid<=37300:continue
 try:
  status=(p/'status').read_text()
  cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
  parent=int(next(x.split(':')[1] for x in status.splitlines() if x.startswith('PPid:')).strip())
  if parent==1 and '--window 2 5 ' in cmd and 'run_thirteen_window_normal_20261011.py' in cmd:target.append(pid)
 except (OSError,ValueError):pass
print('Terminating verified orphan workers:',target,flush=True)
for pid in target:
 try:os.kill(pid,signal.SIGTERM)
 except ProcessLookupError:pass
