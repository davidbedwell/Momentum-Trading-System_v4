#!/usr/bin/env python3
"""Read-only live concurrency resource probe; no runner modification."""
import pathlib,json,datetime,os
base=pathlib.Path('/home/ubuntu/Momentum-Trading-System_v4/Research/Runs/thirteen-window-normal-20261011')
groups={}
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
  if 'run_thirteen_window_normal_20261011.py' not in cmd or '--window ' not in cmd:continue
  a=cmd.split();i=a.index('--window');w=f'{a[i+1]}-{a[i+2]}'
  roll=(p/'smaps_rollup').read_text()
  fields={}
  for line in roll.splitlines():
   if line.startswith(('Pss:','Rss:','Private_Dirty:','Swap:')):
    k,v,*_=line.split();fields[k[:-1]]=int(v)
  g=groups.setdefault(w,{'processes':0,'pss_gib':0,'rss_gib':0,'swap_gib':0})
  g['processes']+=1
  for k,key in [('Pss','pss_gib'),('Rss','rss_gib'),('Swap','swap_gib')]:g[key]+=fields.get(k,0)/1048576
 except (OSError,ValueError,IndexError):continue
mem={}
for line in pathlib.Path('/proc/meminfo').read_text().splitlines():
 if line.startswith(('MemAvailable:','SwapFree:','SwapTotal:')):
  k,v,*_=line.split();mem[k[:-1]]=round(int(v)/1048576,2)
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':groups,'mem_gib':mem}
print(json.dumps(out,indent=2))
with (base/'concurrency_resource_probe.jsonl').open('a') as f:f.write(json.dumps(out)+'\n')
