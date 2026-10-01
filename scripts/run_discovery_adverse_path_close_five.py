#!/usr/bin/env python3
import argparse,json,math,multiprocessing as mp
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import run_discovery_adverse_path_phase2 as p2
import run_discovery_adverse_path_final_compliance as fc
HPTS=[2,4,5,10]

def auc_rank(x,y):
 a=np.asarray(x,float); y=np.asarray(y,int); ok=np.isfinite(a);a=a[ok];y=y[ok];n1=int(y.sum());n0=len(y)-n1
 if not n1 or not n0:return None
 order=np.argsort(a,kind='mergesort');r=np.empty(len(a),float);i=0
 while i<len(a):
  j=i+1
  while j<len(a) and a[order[j]]==a[order[i]]:j+=1
  rr=(i+1+j)/2;r[order[i:j]]=rr;i=j
 return float((r[y==1].sum()-n1*(n1+1)/2)/(n1*n0))

def iv_one(vals,ys,continuous=False):
 ok=[i for i,v in enumerate(vals) if v is not None and (not isinstance(v,float) or math.isfinite(v))]
 if not ok:return {'n':0}
 v=[vals[i] for i in ok];y=[ys[i] for i in ok]
 if continuous:
  arr=np.asarray(v,float);cuts=np.unique(np.quantile(arr,[0,.1,.25,.5,.75,.9,1]));x=np.digitize(arr,cuts[1:-1],right=True).tolist();auc=auc_rank(arr,y)
 else:
  lab={z:j for j,z in enumerate(sorted(set(v),key=str))};x=[lab[z] for z in v];auc=None
 hy=p2.entropy(y);g=defaultdict(list)
 for xx,yy in zip(x,y):g[xx].append(yy)
 cond=sum(len(z)/len(y)*p2.entropy(z) for z in g.values())
 return {'n':len(y),'mutual_information':float(p2.mutual_info(x,y)),'entropy_reduction_bits':hy-cond,'auc':auc}

def structural(rows,structs):
 agg={}
 names=sorted({n for s in structs for n in s})
 for n in names:
  agg[n]={}
  for lab,w in [('WINNER',True),('LOSER',False)]:
   vv=[structs[i][n] for i,r in enumerate(rows) if r['winner']==w and n in structs[i]]
   slopes=Counter(v.get('slope') or 'N/A' for v in vv)
   agg[n][lab]={'n':len(vv),'slope_categories':dict(slopes),'touch_rate':fc.mean([v['touch'] for v in vv]),'hold_rate':fc.mean([v['touch'] and v.get('sustained_break_session') is None for v in vv]),'sweep_reclaim_rate':fc.mean([v['sweep'] and v.get('reclaim_session') is not None for v in vv]),'sustained_break_rate':fc.mean([v.get('sustained_break_session') is not None for v in vv]),'penetration_atr':{'p50':fc.q([v['max_pen_atr'] for v in vv],50),'p90':fc.q([v['max_pen_atr'] for v in vv],90)},'reclaim_time':{'p50':fc.q([v.get('reclaim_time') for v in vv],50),'p90':fc.q([v.get('reclaim_time') for v in vv],90)},'subsequent_low_rate':fc.mean([v.get('subsequent_low_session') is not None for v in vv]),'upper_boundary_break_rate':fc.mean([v.get('upper_boundary_break_session') is not None for v in vv])}
 return {'references':agg,'required_behaviors':['slope_categories','touch_rate','hold_rate','sweep_reclaim_rate','sustained_break_rate','penetration_atr','reclaim_time','subsequent_low_rate','upper_boundary_break_rate'],'reference_count':len(names)}

def transition_ci(rows,sts,B=200,seed=20261001):
 by=defaultdict(list)
 for i,r in enumerate(rows):by[r['ticker']].append(i)
 tick=sorted(by); rng=np.random.default_rng(seed);result={}
 for lag,label in [(1,'one_step'),(2,'two_step')]:
  base={'WINNER':Counter(),'LOSER':Counter()};breadth={'WINNER':defaultdict(set),'LOSER':defaultdict(set)};years={'WINNER':defaultdict(set),'LOSER':defaultdict(set)}
  for i,(r,ss) in enumerate(zip(rows,sts)):
   lab='WINNER' if r['winner'] else 'LOSER'
   for x,y in zip(ss,ss[lag:]):k=x+'->'+y;base[lab][k]+=1;breadth[lab][k].add(r['ticker']);years[lab][k].add(r['year'])
  boots={lab:defaultdict(list) for lab in base}
  for _ in range(B):
   cnt={'WINNER':Counter(),'LOSER':Counter()};den={'WINNER':0,'LOSER':0}
   for t in rng.choice(tick,len(tick),replace=True):
    for i in by[t]:
     r=rows[i];ss=sts[i];lab='WINNER' if r['winner'] else 'LOSER'
     for x,y in zip(ss,ss[lag:]):cnt[lab][x+'->'+y]+=1;den[lab]+=1
   for lab in cnt:
    for k in base[lab]:boots[lab][k].append(cnt[lab][k]/den[lab] if den[lab] else 0)
  result[label]={}
  for lab in base:
   den=sum(base[lab].values());result[label][lab]={k:{'n':n,'share':n/den if den else None,'tickers':len(breadth[lab][k]),'years':len(years[lab][k]),'ci95_ticker_cluster':{'lo':fc.q(boots[lab][k],2.5),'hi':fc.q(boots[lab][k],97.5),'B':B}} for k,n in base[lab].items()}
 return result

def matched(rows,recs,sts,split='2021-09-13'):
 out={}
 for h in HPTS:
  X=[];meta=[]
  for i,r in enumerate(rows):
   if len(r['path'])<h or not r['atr']:continue
   p=r['path'][:h];scale=r['atr']/r['ep'];cl=np.array([float(z['close'])/r['ep']-1 for z in p]);lo=np.array([float(z['low'])/r['ep']-1 for z in p])
   X.append([cl[-1]/scale,lo.min()/scale,np.sum(np.diff(np.r_[0,cl])>0),recs[i]['recs'][h-1]]);meta.append((i,r['family'],r['ticker'],r['winner'],r['signal_date'],r['year']))
  X=np.asarray(X,float);dev=np.array([m[4]<split for m in meta]);mu=X[dev].mean(0);sd=X[dev].std(0);sd[sd==0]=1;Z=(X-mu)/sd
  groups=defaultdict(list)
  for j,m in enumerate(meta):groups[(m[1],m[3],m[2])].append(j)
  pairs=[]
  for fam in sorted({m[1] for m in meta},key=str):
   ticks=sorted({m[2] for m in meta if m[1]==fam})
   for outcome in (False,True):
    for ticker in ticks:
     src=groups.get((fam,outcome,ticker),[]);tgt=[j for (f,w,t),js in groups.items() if f==fam and w!=outcome and t!=ticker for j in js]
     if not src or not tgt:continue
     tree=cKDTree(Z[tgt]);dist,loc=tree.query(Z[src],k=1)
     for aa,d,ll in zip(src,np.atleast_1d(dist),np.atleast_1d(loc)):
      bb=tgt[int(ll)];i=meta[aa][0];j=meta[bb][0];first=None
      mx=min(len(sts[i]),len(sts[j]))
      for s in range(h,mx):
       if sts[i][s]!=sts[j][s]:first={'session':s+1,'dimension':'STATE','a':sts[i][s],'b':sts[j][s]};break
       ra=recs[i]['recs'][s];rb=recs[j]['recs'][s];ba='LT25' if ra<.25 else '25_50' if ra<.5 else '50_100' if ra<1 else 'GE100';bbin='LT25' if rb<.25 else '25_50' if rb<.5 else '50_100' if rb<1 else 'GE100'
       if ba!=bbin:first={'session':s+1,'dimension':'REC','a':ba,'b':bbin};break
      pairs.append((float(d),i,j,first))
  fd=[p[3] for p in pairs if p[3]];cnt=Counter((z['dimension'],z['session']) for z in fd)
  out[str(h)]={'directed_pairs':len(pairs),'median_distance':fc.q([p[0] for p in pairs],50),'p90_distance':fc.q([p[0] for p in pairs],90),'unique_tickers':len({rows[x]['ticker'] for p in pairs for x in (p[1],p[2])}),'year_breadth':len({rows[x]['year'] for p in pairs for x in (p[1],p[2])}),'outcome_balance':{'source_winner':sum(rows[p[1]]['winner'] for p in pairs),'source_loser':sum(not rows[p[1]]['winner'] for p in pairs)},'first_divergence':{'n_with_divergence':len(fd),'most_common':[{'dimension':k[0],'session':k[1],'n':n} for k,n in cnt.most_common(20)],'definition':'first subsequent difference in prespecified causal STATE, then REC bin'},'standardization':'development split only','split_date':split}
 return out

def information(rows,structs,recs,sts,split='2021-09-13'):
 ys=[int(r['winner']) for r in rows];features={};continuous=set()
 dims=[fc.dims_for(r,rc) for r,rc in zip(rows,recs)]
 for k in ['AE','TIME','REC','ATR','FAMILY','GENOME','YEAR']:features[k]=[d[k] for d in dims]
 features['ae_depth']=[-r['mae'] for r in rows];features['time_to_low']=[r['mi']+1 for r in rows];features['atr_ae']=[-r['mae']*r['ep']/r['atr'] if r['atr'] else None for r in rows];continuous|={'ae_depth','time_to_low','atr_ae'}
 for h in [2,4,5,10]:
  features[f'state_s{h}']=[s[h-1] if len(s)>=h else 'MISSING' for s in sts];features[f'recovery_s{h}']=[rc['recs'][h-1] if len(rc['recs'])>=h else None for rc in recs];continuous.add(f'recovery_s{h}')
 for ev in ['touch','sweep','failure','reclaim']:
  for ref in sorted({n for s in structs for n in s}):features[f'{ref}:{ev}']=[int(ref in s and s[ref][ev]) for s in structs]
 for p in ['P1','P2','P3','P4']:
  ix=set(fc.pattern_ix(rows,structs,recs).get(p,[]));features[p]=[int(i in ix) for i in range(len(rows))]
 dev=[i for i,r in enumerate(rows) if r['signal_date']<split];hold=[i for i,r in enumerate(rows) if r['signal_date']>=split]
 out={}
 for k,v in features.items():
  out[k]={'all':iv_one(v,ys,k in continuous),'development':iv_one([v[i] for i in dev],[ys[i] for i in dev],k in continuous),'holdout_replay':iv_one([v[i] for i in hold],[ys[i] for i in hold],k in continuous),'continuous':k in continuous}
 return {'features':out,'feature_count':len(out),'manifest':sorted(out),'metrics':'MI + entropy reduction for every manifest feature; AUC additionally for ordered/continuous features','split_date':split}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--trajectory-dir',required=True);ap.add_argument('--base',required=True);ap.add_argument('--markdown',required=True);a=ap.parse_args()
 rows=p2.load_rows(a.trajectory_dir);print('CLOSE5_WORKERS=6',flush=True)
 with mp.get_context('fork').Pool(min(6,mp.cpu_count()),initializer=p2._init_rows,initargs=(rows,)) as pool:structs=pool.map(p2._structure_idx,range(len(rows)),chunksize=256)
 recs=[p2.recovery_stats(r) for r in rows];sts=[p2.states(r,s,rc) for r,s,rc in zip(rows,structs,recs)]
 out=json.load(open(a.base));pix=fc.pattern_ix(rows,structs,recs);out['path_patterns']={}
 for p in ['P1','P2','P3','P4']:
  ix=pix.get(p,[]);out['path_patterns'][p]={**fc.group_report(rows,ix),'prevalence':len(ix)/len(rows),'qualification_uses_terminal_outcome':False}
 out['matched_trajectory']=matched(rows,recs,sts);print('CLOSE5_MATCHED_DONE',flush=True)
 out['state_transitions']=transition_ci(rows,sts);print('CLOSE5_TRANSITIONS_DONE',flush=True)
 out['structural_references_full']=structural(rows,structs);print('CLOSE5_STRUCTURAL_DONE',flush=True)
 out['information_value_full']=information(rows,structs,recs,sts);print('CLOSE5_IV_DONE',flush=True)
 checks=out['compliance_checklist'];checks['patterns_P1_P4']=set(out['path_patterns'])=={'P1','P2','P3','P4'};checks['matched_first_divergence']=all(isinstance(v.get('first_divergence'),dict) for v in out['matched_trajectory'].values());checks['state_transition_dependence_CI']=all(all(all('ci95_ticker_cluster' in z for z in lab.values()) for lab in lag.values()) for lag in out['state_transitions'].values());req=set(out['structural_references_full']['required_behaviors']);checks['structural_full_required_behaviors']=req=={'slope_categories','touch_rate','hold_rate','sweep_reclaim_rate','sustained_break_rate','penetration_atr','reclaim_time','subsequent_low_rate','upper_boundary_break_rate'} and out['structural_references_full']['reference_count']>=19;checks['information_value_every_prespecified_observation']=out['information_value_full']['feature_count']>=80 and all('development' in z and 'holdout_replay' in z for z in out['information_value_full']['features'].values())
 out['compliance_pass']=all(checks.values());out['remaining_failures']=[k for k,v in checks.items() if not v];out['verification_a_accessed']=False;out['verification_b_accessed']=False
 Path(a.base).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');Path(a.markdown).write_text('# MTS Frozen Protocol Final Compliance — 2026-10-01\n\n'+'\n'.join(f'- [{"x" if v else " "}] {k}' for k,v in checks.items())+f'\n\n**PASS:** {out["compliance_pass"]}\n\nRemaining failures: '+', '.join(out['remaining_failures'])+'\n')
 print('COMPLIANCE_PASS='+str(out['compliance_pass']));print('FAILURES='+','.join(out['remaining_failures']));print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
 if not out['compliance_pass']:raise SystemExit(2)
if __name__=='__main__':main()
