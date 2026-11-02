import json,hashlib,time,secrets,gzip,copy,sys,subprocess,traceback,csv,os
from datetime import datetime,timezone
import engine as z
O=z.O

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(O/n).write_text(json.dumps(v,indent=2))
def main():
 start=time.monotonic();count=0;rows=[];audits=[]
 if (O/'commitment.json').exists():raise SystemExit('Refusing fresh holdout reuse')
 try:
  test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(O),'-v'],capture_output=True,text=True,timeout=120)
  (O/'tests.log').write_text(test.stdout+test.stderr)
  if test.returncode:raise RuntimeError('Tests failed; see tests.log')
  assert sha(O/'frozen/iteration6_engine.py')==sha(O.parent/'discrimination_iteration6/engine.py')
  assert sha(O/'frozen/iteration5_reference.py')==sha(O.parent/'discrimination_iteration5/experiment.py')
  sources={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and (p.suffix=='.py' or p.name in ('preregister.json','claude_review.md'))}
  dump('commitment.json',dict(utc=datetime.now(timezone.utc).isoformat(),sources=sources,public_timestamp=False))
  seeds=[secrets.randbits(63) for _ in range(8)];offsets=[secrets.randbelow(61)+20 for _ in seeds]
  assert len(set(seeds))==8
  dump('seeds.json',dict(seeds=seeds,switch_offsets=offsets))
  plan=json.loads((O/'preregister.json').read_text())
  with gzip.open(O/'replays.jsonl.gz','wt') as rp,gzip.open(O/'opportunities.jsonl.gz','wt') as op:
   for num,(seed,off) in enumerate(zip(seeds,offsets)):
    extended=num>=6;z.configure(extended);stratum='extended_secondary' if extended else 'primary'
    for scenario in plan['scenarios']:
     change=z.x.START+off if scenario=='random_reversal' else z.x.START
     p,f,truth=z.x.generate(seed,scenario,change)
     old,mb,old_events=z.e.predict(p,f)
     for arm in plan['arms']:
      if count>=120 or time.monotonic()-start>1170:raise RuntimeError('Budget reached before completion')
      m=mb if arm=='iteration6' else z.fit(p,f,arm)
      ss=copy.deepcopy(old['candidate']) if arm=='iteration6' else z.states(p,f,m)
      gate=z.x.Gate(p,f,m) if arm=='iteration6' else (z.A if arm=='A' else z.B)(p,f,m)
      count+=1;metric,trades,daily=z.x.replay(p,ss,gate=gate)
      events=sorted(gate.events+(old_events if arm=='iteration6' else []),key=lambda v:v['index'])
      rev=scenario in ('reversal','random_reversal');first=events[0]['index'] if events else None
      prealarm=bool(rev and first is not None and first<change)
      delay=first-change if rev and first is not None and not prealarm else None
      before=next((d['nav'] for d in daily if d['index']==change-1),100000.)
      vals=[before]+[d['nav'] for d in daily if d['index']>=change]+[metric['final_nav']];peak=before;dd=0
      for v in vals:peak=max(peak,v);dd=max(dd,1-v/peak)
      mat=[[0]*6 for _ in range(5)];real=[[0]*6 for _ in range(5)];fg3=fgpost=0
      funded={(t['signal'],t['j']):t for t in trades}
      key=dict(seed=seed,stratum=stratum,scenario=scenario,arm=arm)
      for k,i in enumerate(range(z.x.START,z.x.END)):
       for j,a in enumerate(ss[k]):
        ti=z.e.TIERS.index(z.e.tier(truth[i][j]));pi=z.e.TIERS.index(a['label']) if a['label']!='UNKNOWN' else 5
        actual=z.e.observed(p,i,j);mat[ti][pi]+=1;real[z.e.TIERS.index(z.e.tier(actual))][pi]+=1
        if ti==0 and pi==4 and rev and i>=change:
         if i<change+3:fg3+=1
         else:fgpost+=1
        op.write(json.dumps(dict(**key,index=i,j=j,truth=truth[i][j],realized=actual,**a,funded=(i,j) in funded))+'\n')
      assigned=sum(sum(r[:5]) for r in mat);support=[sum(r[c] for r in mat) for c in range(5)]
      row=dict(**key,**metric,change=change if rev else None,adverse_return=metric['final_nav']/before-1,adverse_mdd=dd,coverage=assigned/3024,conditional_accuracy=sum(mat[c][c] for c in range(5))/assigned if assigned else None,false_great=mat[0][4],false_great_first3=fg3,false_great_post3=fgpost,support=support,confusion_latent=mat,confusion_realized=real,first_alarm=first,delay=delay,prechange_alarm=prealarm,false_alarm=bool(events) if not rev else prealarm,events=events,models=m,baseline_ci_radius=getattr(gate,'bound',None))
      rows.append(row)
      a=dict(**key,min_cash=min(d['cash'] for d in daily),pnl_error=abs(metric['final_nav']-100000-sum(t['debit']*t['net'] for t in trades)),net_error=max((abs(t['net']-z.e.observed(p,t['signal'],t['j'])) for t in trades),default=0),cost_error=abs(metric['costs']-sum(t['shares']*(t['entry_open']+t['exit_open'])*z.e.COST/2 for t in trades)),horizon=all(t['exit_index']==t['entry_index']+1 for t in trades),no_funded_after_alarm=all(t['signal']<first for t in trades) if first is not None else True)
      audits.append(a);rp.write(json.dumps(dict(**key,trades=trades,daily=daily,trace=gate.trace))+'\n')
      with (O/'per_seed.jsonl').open('a') as out:out.write(json.dumps(row)+'\n')
     print(stratum,num+1,scenario,'replays',count,flush=True)
  assert all(sha(O/p)==h for p,h in sources.items())
  assert sha(O/'frozen/iteration6_engine.py')==sha(O.parent/'discrimination_iteration6/engine.py')
  assert sha(O/'frozen/iteration5_reference.py')==sha(O.parent/'discrimination_iteration5/experiment.py')
  dump('results.json',dict(execution_status='COMPLETE',portfolio_replays=count,elapsed_seconds=time.monotonic()-start,tests=6,rows=rows,audits=audits,frozen_hashes_match=True))
 except Exception:
  dump('report.json',dict(execution_status='INFRASTRUCTURE_OR_EXECUTION_ERROR',portfolio_replays=count,elapsed_seconds=time.monotonic()-start,error=traceback.format_exc(),partial_rows=rows,audits=audits))
  (O/'summary.md').write_text('Execution stopped on infrastructure/execution error. No success claimed. See report.json.\n')
  raise
if __name__=='__main__':main()
