"""One bounded run. Refuses fresh-seed reuse; all budgeted replay calls counted."""
import copy,csv,gzip,json,math,secrets,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import engine as x
O=x.O

def dump(name,obj):(O/name).write_text(json.dumps(obj,indent=2))
def csvout(name,rows):
 with (O/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def score(ss,truth,seed,scenario,variant,phase,change):
 mat=[[0]*6 for _ in range(5)];real=[[0]*6 for _ in range(5)]
 for k,i in enumerate(range(x.START,x.END)):
  for j,z in enumerate(ss[k]):
   a=x.e.TIERS.index(x.e.tier(truth[i][j]));b=x.e.TIERS.index(z['label']) if z['label']!='UNKNOWN' else 5;mat[a][b]+=1
 n=126*24;assigned=sum(sum(r[:5]) for r in mat)
 return dict(seed=seed,scenario=scenario,variant=variant,phase=phase,coverage=assigned/n,false_great=mat[0][4],false_great_rate=mat[0][4]/max(1,sum(mat[0])),false_terrible=mat[4][0],false_terrible_rate=mat[4][0]/max(1,sum(mat[4])),support=[sum(r[c] for r in mat) for c in range(5)],recall=[mat[c][c]/max(1,sum(mat[c])) for c in range(5)],confusion=mat)

def main():
 start=time.monotonic()
 if (O/'commitment.json').exists():raise SystemExit('Refusing final-seed reuse')
 plan=json.loads((O/'preregister.json').read_text());count=0
 tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(O),'-p','test_*.py','-v'],capture_output=True,text=True)
 (O/'tests.log').write_text(tests.stdout+tests.stderr);count+=3
 if tests.returncode:raise SystemExit(tests.stderr)
 scores=[];metrics=[];detection=[];audits=[];confusions=[];channels=[]
 old=json.loads((O.parent/'discrimination_iteration5/report.json').read_text())
 diagnosis=[]
 with gzip.open(O.parent/'discrimination_iteration5/opportunities.jsonl.gz','rt') as f:
  agg={}
  for line in f:
   z=json.loads(line)
   if z['scenario']=='reversal' and z['variant']=='candidate' and z['true_ev']==-.012 and z['inferred_tier']=='GREAT':
    a=agg.setdefault(z['seed'],dict(first=z['index'],last=z['index'],unavoidable_first3=0,fixable_after_first3=0,count=0,funded=0,funded_pnl=0.))
    a['last']=z['index'];a['count']+=1;a['unavoidable_first3']+=z['index']<609;a['fixable_after_first3']+=z['index']>=609;a['funded']+=z['funded'];a['funded_pnl']+=z['funded_debit']*z['realized_net']
 for seed,a in agg.items():diagnosis.append(dict(seed=seed,**a))
 dump('iteration5_diagnosis.json',dict(rows=diagnosis,first_eligible_outcome=609,first_allowed_scan=628,hard_min_delay=3,explanation='Sensor marginal and complete price paths identical under reversal. Earliest post-switch outcome signal606 available609. First scan628 uses signals606..625; 19 extra sessions are hard-coded. Frozen means and sensor/full agreement cannot detect reversed sign.'))
 rp=gzip.open(O/'replays.jsonl.gz','wt');op=gzip.open(O/'opportunities.jsonl.gz','wt')
 def run(seed,scenario,phase,change=None,paired=True):
  nonlocal count
  p,f,truth=x.generate(seed,scenario,change);base,models,oldalarms=x.e.predict(p,f)
  gate=x.Gate(p,f,models);states=copy.deepcopy(base['candidate'])
  variants=[('iteration6',states,gate)]
  if paired:variants.append(('iteration5',base['candidate'],None))
  for variant,ss,g in variants:
   if count>=64 or time.monotonic()-start>710:raise RuntimeError('Budget exhausted')
   count+=1;m,ts,ds=x.replay(p,ss,gate=g)
   change0=change if change is not None else x.START
   before=next((d['nav'] for d in ds if d['index']==change0-1),100000.)
   adverse_nav=[before]+[d['nav'] for d in ds if d['index']>=change0]+[m['final_nav']]
   peak=adverse_nav[0];dd=0.
   for v in adverse_nav:peak=max(peak,v);dd=max(dd,1-v/peak)
   m.update(adverse_return=m['final_nav']/before-1,adverse_mdd=dd)
   metrics.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,**m))
   sc=score(ss,truth,seed,scenario,variant,phase,change);scores.append(sc)
   for a,row in zip(x.e.TIERS,sc['confusion']):
    confusions.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,truth=a,**dict(zip(x.e.TIERS+['UNKNOWN'],row))))
   alarms=gate.events if g else oldalarms
   first=alarms[0]['index'] if alarms else None
   detection.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,change=change if scenario=='random_reversal' else x.START if scenario=='reversal' else None,first_detection=first,delay=(first-change0) if first is not None and scenario in ['reversal','random_reversal'] else None,false_alarm=bool(alarms) and scenario not in ['reversal','random_reversal'],events=alarms))
   err=max((abs(t['net']-x.e.observed(p,t['signal'],t['j'])) for t in ts),default=0)
   audits.append(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,min_cash=min(d['cash'] for d in ds),net_error=err,pnl_error=abs(m['final_nav']-100000-sum(t['debit']*t['net'] for t in ts)),horizon_ok=all(t['exit_index']==t['entry_index']+1 for t in ts),max_risk=m['max_modeled_risk'],gap_exceed=m['gap_loss_exceedances']))
   rp.write(json.dumps(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,trades=ts,daily=ds))+'\n')
   funded={(t['signal'],t['j']) for t in ts}
   for k,i in enumerate(range(x.START,x.END)):
    for j,z in enumerate(ss[k]):op.write(json.dumps(dict(seed=seed,scenario=scenario,phase=phase,variant=variant,index=i,j=j,label=z['label'],truth=truth[i][j],realized=x.e.observed(p,i,j),funded=(i,j) in funded))+'\n')
  channels.append(dict(seed=seed,scenario=scenario,phase=phase,events=gate.events,trace=gate.trace))
  print(phase,seed,scenario,'replays',count,flush=True)
 # Design probes are separate and fixed: no threshold search or candidate selection.
 for seed in plan['design_seeds']:
  for scenario in ['learnable','reversal']:run(seed,scenario,'design',paired=False)
 for seed in old['seeds']:run(seed,'reversal','paired_regression')
 for seed in old['seeds'][:2]:run(seed,'learnable','paired_regression')
 sources={str(p.resolve()):x.e.sha(p) for p in sorted(O.glob('*.py'))}
 sources[str((O/'preregister.json').resolve())]=x.e.sha(O/'preregister.json')
 sources[str(Path(x.e.__file__).resolve())]=x.e.sha(x.e.__file__)
 dump('commitment.json',dict(utc=datetime.now(timezone.utc).isoformat(),sources=sources,pre_final_replays=count,public_timestamp=False))
 seeds=[secrets.randbits(63) for _ in range(4)];changes=[secrets.randbelow(61)+x.START+20 for _ in seeds];dump('seeds.json',dict(seeds=seeds,random_changes=changes))
 for seed,change in zip(seeds,changes):
  for scenario in plan['final_scenarios']:run(seed,scenario,'final',change if scenario=='random_reversal' else None)
 rp.close();op.close()
 final=[s for s in scores if s['phase']=='final' and s['variant']=='iteration6'];stable=[s for s in final if s['scenario'] in ['learnable','outer_noise']]
 det=[d for d in detection if d['phase']=='final' and d['variant']=='iteration6'];rev=[d for d in det if d['scenario'] in ['reversal','random_reversal']]
 improvements=[]
 for s in [s for s in scores if s['variant']=='iteration6']:
  b=next((b for b in scores if b['seed']==s['seed'] and b['scenario']==s['scenario'] and b['phase']==s['phase'] and b['variant']=='iteration5'),None)
  if b:improvements.append(dict(seed=s['seed'],scenario=s['scenario'],phase=s['phase'],false_great_delta=s['false_great']-b['false_great']))
 reversal_metrics=[m for m in metrics if m['phase']=='final' and m['variant']=='iteration6' and m['scenario'] in ['reversal','random_reversal']]
 checks=dict(stable_coverage=all(s['coverage']>=.15 for s in stable),stable_extreme_errors=all(max(s['false_great_rate'],s['false_terrible_rate'])<=.01 for s in stable),five_tier_support=all(min(s['support'])>=20 for s in stable if s['scenario']=='learnable'),null_abstention=all(s['coverage']==0 for s in final if s['scenario']=='null'),observed_false_alarm=not any(d['false_alarm'] for d in det),rapid_detection=all(d['delay'] is not None and 3<=d['delay']<=8 for d in rev),reversal_false_great_reduced=all(d['false_great_delta']<0 for d in improvements if d['scenario'] in ['reversal','random_reversal']),adverse_loss_limit=all(m['adverse_return']>=-.05 and m['adverse_mdd']<=.05 for m in reversal_metrics),accounting=all(a['min_cash']>=-1e-8 and a['net_error']<1e-12 and a['pnl_error']<1e-6 and a['horizon_ok'] and a['max_risk']<=.02+1e-12 for a in audits),frozen_hashes=all(x.e.sha(p)==h for p,h in sources.items()),budget=count<=64 and time.monotonic()-start<=720)
 dump('report.json',dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,portfolio_replays=count,elapsed_seconds=time.monotonic()-start,tests=6,diagnosis=diagnosis,discrimination=scores,detection=detection,portfolio=metrics,paired=improvements,channels=channels,audits=audits,blocker='Failed checks: '+', '.join(k for k,v in checks.items() if not v),limitations=['Four fresh seeds cannot establish <=5% population false alarm probability.','No safe zero-delay detection is identifiable from this DGP; first3 sessions remain exposed.','Model loss is per trade, not portfolio or realized gap cap.','Fresh seeds use inherited synthetic DGP; no real alpha or production readiness.','No independent sector data exists; market price breadth has exactly no switch information.','Local hash freeze only; no trusted public timestamp.']))
 csvout('confusion.csv',confusions);csvout('portfolio.csv',metrics);csvout('audit.csv',audits);csvout('paired.csv',improvements)
 dump('checksums.json',{p.name:x.e.sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='checksums.json'})
 print(checks,flush=True)
if __name__=='__main__':main()
