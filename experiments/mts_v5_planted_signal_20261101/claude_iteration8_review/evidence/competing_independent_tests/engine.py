"""Frozen references loaded without edits; all competing changes isolated here."""
import importlib.util, math, copy
from pathlib import Path
O=Path(__file__).resolve().parent

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
# Reference engine's relative import expects its original directory. Retain original
# immutable dependency and verify its hash against archived copy before/after run.
x=load('six',O.parent/'discrimination_iteration6/engine.py');e=x.e

def configure(extended=False):
 e.FIT=range(600) if extended else range(400)
 e.CAL=range(603,903) if extended else range(403,603)
 e.START=x.START=906 if extended else 606
 e.END=x.END=e.START+126;e.N=e.END+2

def fit(p,f,arm):
 m=e.fit(p,f)
 if arm=='A':
  for c,z in enumerate(m):
   tr=[v for _,v in e.dates(p,f,e.FIT,c)];ca=[v for _,v in e.dates(p,f,e.CAL,c)]
   if abs(e.mean(ca)-e.mean(tr))<e.se(ca):z['radius']=2.576*math.sqrt(e.se(tr)**2+e.se(ca)**2)
 return m

def states(p,f,m):
 # Same classifier and disagreement rule. Monitor replacement is exclusive: do
 # not accidentally leave iteration5's old gate active beneath either new gate.
 out=[];ident=max(z['mean'] for z in m)-min(z['mean'] for z in m)>.003
 for i in range(x.START,x.END):
  row=[]
  for j,c in enumerate(f[i]):
   z=m[c];mu=z['mean']+z['slope']*(p[i][j]/p[i-1][j]-1-z['center']);r=z['radius']+abs(mu-z['mean'])
   lab=e.label(mu,r,z['ntrain'],z['ncal']);reason='INTERVAL'
   if not ident:lab='UNKNOWN';reason='NO_IDENTIFIABLE_SIGNAL'
   if abs(mu-z['mean'])>z['threshold']:lab='UNKNOWN';reason='SENSOR_FULL_DISAGREEMENT'
   row.append(dict(mean=mu,radius=r,label=lab,reason=reason))
  out.append(row)
 return out

def contrast(p,f,d):
 g=[[e.observed(p,d,j) for j in range(24) if f[d][j]==c] for c in (0,4)]
 return e.mean(g[1])-e.mean(g[0]) if min(map(len,g))>=2 else None

class A:
 """Literal class update pseudocode, including sign error/current-data lambda."""
 def __init__(self,p,f,m):
  self.p=p;self.f=f;self.mu=m[4]['mean']-m[0]['mean'];self.logs={w:0. for w in (2,4,8)};self.events=[];self.trace=[];self.latched=False
 def __call__(self,n,row,trades):
  if not self.latched:
   for w in self.logs:
    vals=[contrast(self.p,self.f,d) for d in range(n-2-w,n-2)]
    if any(v is None for v in vals):continue
    delta=e.mean(vals)-self.mu;sigma=.018/math.sqrt(w);lam=max(0,min(delta/sigma**2,1/sigma))
    self.logs[w]+=lam*delta-.5*(lam*sigma)**2
    if self.logs[w]>=math.log(300):self.latched=True;self.events.append(dict(index=n,window=w,log_e=self.logs[w]));break
  self.trace.append(dict(index=n,logs=dict(self.logs),latched=self.latched,last_available=n-3))
  return [dict(z,label='UNKNOWN',reason='DRIFT_LATCH') for z in row] if self.latched else row

class B:
 """Date increments; fixed-lambda/start-time mixture and baseline CI budget."""
 def __init__(self,p,f,m):
  self.p=p;self.f=f;self.events=[];self.trace=[];self.latched=False;self.seen=[]
  v=[contrast(p,f,d) for d in e.FIT];v=[z for z in v if z is not None]
  self.bound=.018*math.sqrt(2*math.log(1/.002)/len(v))
  self.lower=e.mean(v)-self.bound
  self.components=[dict(start=s,lam=l,log=0.) for s in range(x.START,x.END,8) for l in (16.,32.,64.,96.)]
 def __call__(self,n,row,trades):
  d=n-3
  if not self.latched and d>=x.START:
   v=contrast(self.p,self.f,d)
   if v is not None:
    assert d not in self.seen;self.seen.append(d)
    for c in self.components:
     if d>=c['start']:c['log']+=c['lam']*(self.lower-v)-.5*(c['lam']*.018)**2
   a=max(c['log'] for c in self.components);logmix=a+math.log(sum(math.exp(c['log']-a) for c in self.components)/len(self.components))
   if logmix>=math.log(1/.008):self.latched=True;self.events.append(dict(index=n,log_e=logmix,last_signal=d))
  else:logmix=None
  self.trace.append(dict(index=n,last_available=d,log_e=logmix,latched=self.latched))
  return [dict(z,label='UNKNOWN',reason='DRIFT_LATCH') for z in row] if self.latched else row
