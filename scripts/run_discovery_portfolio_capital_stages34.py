#!/usr/bin/env python3
import argparse,gzip,pickle,json,hashlib,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,metrics,SPLIT
INIT=(.25,.50,.75)
REDUCE=(.25,.50,.75)
FRULES=('REC50','REC75','NO_NEW_LOW_2','NO_NEW_LOW_3','LOW_PRESERVE_5','LOW_PRESERVE_10','LOW_PRESERVE_20','LOW_RECLAIM_5','LOW_RECLAIM_10','LOW_RECLAIM_20','HIGH_ATTACK_5','HIGH_ATTACK_10','HIGH_ATTACK_20','HIGH_RECLAIM_5','HIGH_RECLAIM_10','HIGH_RECLAIM_20','FAVORABLE_2OF4')
ARULES=('LOWER_LOW_2','LOWER_LOW_3','REC_LT25_S5','REC_LT50_S5','REC_LT75_S5','LOW_FAIL_5','LOW_FAIL_10','LOW_FAIL_20','ADVERSE_2OF3')
def refs(r):
 b=r['_bars'];si=r['si'];out={}
 for w in (5,10,20):
  if si>=w:
   q=b[si-w+1:si+1];out[f'L{w}']=min(float(x['low']) for x in q);out[f'H{w}']=max(float(x['high']) for x in q)
 return out
def evidence(r):
 rf=refs(r);path=r['path'];ep=float(r['ep']);fav={k:None for k in FRULES};adv={k:None for k in ARULES}
 running=ep;lastnew=None;llrun=0;trough=ep;breach={w:False for w in (5,10,20)};failrun={w:0 for w in (5,10,20)};first3=[]
 for j,z in enumerate(path,1):
  lo=float(z['low']);hi=float(z['high']);cl=float(z['close']);isnew=lo<running
  if isnew:running=lo;lastnew=j;llrun+=1
  else:llrun=0
  trough=min(trough,lo);ae=max(ep-trough,0);rec=(cl-trough)/ae if ae>0 else 1.0
  if fav['REC50'] is None and rec>=.50:fav['REC50']=j
  if fav['REC75'] is None and rec>=.75:fav['REC75']=j
  if lastnew is not None and fav['NO_NEW_LOW_2'] is None and j-lastnew>=2:fav['NO_NEW_LOW_2']=j
  if lastnew is not None and fav['NO_NEW_LOW_3'] is None and j-lastnew>=3:fav['NO_NEW_LOW_3']=j
  if adv['LOWER_LOW_2'] is None and llrun>=2:adv['LOWER_LOW_2']=j
  if adv['LOWER_LOW_3'] is None and llrun>=3:adv['LOWER_LOW_3']=j
  if j==5 and ae>0:
   if rec<.25:adv['REC_LT25_S5']=j
   if rec<.50:adv['REC_LT50_S5']=j
   if rec<.75:adv['REC_LT75_S5']=j
  first3.append(lo)
  for w in (5,10,20):
   lr=rf.get(f'L{w}');hr=rf.get(f'H{w}')
   if lr is not None:
    if lo<lr:breach[w]=True
    if breach[w] and cl>lr and fav[f'LOW_RECLAIM_{w}'] is None:fav[f'LOW_RECLAIM_{w}']=j
    failrun[w]=failrun[w]+1 if cl<lr else 0
    if failrun[w]>=2 and adv[f'LOW_FAIL_{w}'] is None:adv[f'LOW_FAIL_{w}']=j
   if hr is not None:
    if hi>=hr and fav[f'HIGH_ATTACK_{w}'] is None:fav[f'HIGH_ATTACK_{w}']=j
    if cl>hr and fav[f'HIGH_RECLAIM_{w}'] is None:fav[f'HIGH_RECLAIM_{w}']=j
  if j==3:
   for w in (5,10,20):
    lr=rf.get(f'L{w}')
    if lr is not None and min(first3)>lr:fav[f'LOW_PRESERVE_{w}']=j
 def second(vals):
  a=sorted(x for x in vals if x is not None);return a[1] if len(a)>=2 else None
 fav['FAVORABLE_2OF4']=second([fav['NO_NEW_LOW_2'],fav['REC50'],fav['LOW_RECLAIM_10'],fav['HIGH_ATTACK_10']])
 adv['ADVERSE_2OF3']=second([adv['LOWER_LOW_2'],adv['REC_LT50_S5'],adv['LOW_FAIL_10']])
 return fav,adv
def rule_matrices(rows,dates):
 dm={d:i for i,d in enumerate(dates)};n=len(rows);F=np.full((n,len(FRULES)),-1,np.int16);A=np.full((n,len(ARULES)),-1,np.int16);FS=np.full(F.shape,-1,np.int16);AS=np.full(A.shape,-1,np.int16);FP=np.full(F.shape,np.nan,np.float32);AP=np.full(A.shape,np.nan,np.float32)
 for i,r in enumerate(rows):
  f,a=evidence(r);p=r['path']
  for j,k in enumerate(FRULES):
   s=f[k]
   if s is not None and s<len(p):F[i,j]=dm[p[s]['date']];FS[i,j]=s;FP[i,j]=float(p[s]['open'])
  for j,k in enumerate(ARULES):
   s=a[k]
   if s is not None and s<len(p):A[i,j]=dm[p[s]['date']];AS[i,j]=s;AP[i,j]=float(p[s]['open'])
  if (i+1)%10000==0:print('EVIDENCE',i+1,flush=True)
 return F,A,FS,AS,FP,AP
def build_market(rows):
 dates=sorted({b['date'] for r in rows for b in r['path']});dm={d:i for i,d in enumerate(dates)};D=len(dates);n=len(rows);ec=np.zeros(D,np.int32);xc=np.zeros(D,np.int32);uc=np.zeros(D,np.int32)
 for r in rows:
  ec[dm[r['path'][0]['date']]]+=1;xc[dm[r['path'][-1]['date']]]+=1
  for b in r['path']:uc[dm[b['date']]]+=1
 eo=np.r_[0,np.cumsum(ec,dtype=np.int64)];xo=np.r_[0,np.cumsum(xc,dtype=np.int64)];uo=np.r_[0,np.cumsum(uc,dtype=np.int64)];ei=np.empty(n,np.int32);xi=np.empty(n,np.int32);ui=np.empty(int(uo[-1]),np.int32);ufo=np.empty(int(uo[-1]),float);ufi=np.empty(int(uo[-1]),float);ep=eo[:-1].copy();xp=xo[:-1].copy();up=uo[:-1].copy();lens=np.empty(n,np.int16)
 for i,r in enumerate(rows):
  p=r['path'];lens[i]=len(p);de=dm[p[0]['date']];dx=dm[p[-1]['date']];ei[ep[de]]=i;ep[de]+=1;xi[xp[dx]]=i;xp[dx]+=1;prev=float(r['ep'])
  for b in p:
   d=dm[b['date']];j=up[d];ui[j]=i;op=float(b['open']);cl=float(b['close']);ufo[j]=op/prev;ufi[j]=cl/op;up[d]+=1;prev=cl
 active=0;con=[]
 for d in range(D):active+=int(ec[d]);con.append(active);active-=int(xc[d])
 med=float(np.median([x for x in con if x>0]))
 return dates,(eo,ei),(xo,xi),(uo,ui,ufo,ufi),lens,{'median_concurrency':med,'max_concurrency':int(max(con)),'base_trade_fraction':1.0/med,'days':D}
def action_csr(fill_day,D):
 n,P=fill_day.shape;flat=fill_day.ravel();fi=np.flatnonzero(flat>=0);days=flat[fi].astype(np.int32);order=np.argsort(days,kind='stable');days=days[order];fi=fi[order];cnt=np.bincount(days,minlength=D);off=np.r_[0,np.cumsum(cnt,dtype=np.int64)]
 return off,(fi//P).astype(np.int32),(fi%P).astype(np.int16)
def simulate(dates,entries,exits,updates,fill_day,init,action_frac,base,target_scale,mode,allow_borrow):
 eo,ei=entries;xo,xi=exits;uo,ui,ufo,ufi=updates;n,P=fill_day.shape;ao,at,ap=action_csr(fill_day,len(dates));cash=np.ones(P);val=np.zeros((n,P));target=np.zeros((n,P));pos=np.zeros(P);wealth=[];gross=[];cashfrac=[]
 for d in range(len(dates)):
  us=ui[uo[d]:uo[d+1]];fo=ufo[uo[d]:uo[d+1]];fi=ufi[uo[d]:uo[d+1]]
  if len(us):
   old=val[us,:];delta=(old*(fo[:,None]-1)).sum(axis=0);val[us,:]=old*fo[:,None];pos+=delta
  ts=at[ao[d]:ao[d+1]];ps=ap[ao[d]:ao[d+1]]
  if mode=='sell' and len(ts):
   for p in np.unique(ps):
    ix=ts[ps==p];amt=val[ix,p]*action_frac[p];v=float(amt.sum());val[ix,p]-=amt;cash[p]+=v;pos[p]-=v
  eq_open=cash+pos;new=ei[eo[d]:eo[d+1]]
  for p in range(P):
   aix=ts[ps==p] if mode=='buy' and len(ts) else np.empty(0,np.int32);addreq=target[aix,p]*action_frac[p] if len(aix) else np.empty(0)
   bt=base*eq_open[p]*target_scale[p];newreq=np.full(len(new),bt*init[p]);tot=float(addreq.sum()+newreq.sum());sc=1.0 if allow_borrow or tot<=cash[p] or tot<=0 else max(0.0,cash[p]/tot)
   if len(new):
    target[new,p]=bt*sc;alloc=target[new,p]*init[p];val[new,p]+=alloc;v=float(alloc.sum());cash[p]-=v;pos[p]+=v
   if len(aix):
    alloc=addreq*sc;val[aix,p]+=alloc;v=float(alloc.sum());cash[p]-=v;pos[p]+=v
  if len(us):
   old=val[us,:];delta=(old*(fi[:,None]-1)).sum(axis=0);val[us,:]=old*fi[:,None];pos+=delta
  outs=xi[xo[d]:xo[d+1]]
  if len(outs):
   v=val[outs,:].sum(axis=0);cash+=v;pos-=v;val[outs,:]=0.0
  eq=cash+pos;wealth.append(eq.copy());gross.append(np.divide(pos,eq,out=np.zeros(P),where=eq!=0));cashfrac.append(np.divide(cash,eq,out=np.zeros(P),where=eq!=0))
 return np.asarray(wealth),np.asarray(gross),np.asarray(cashfrac)
def trade_metric(x):
 a=np.asarray(x,float);q=float(np.quantile(a,.05));eq=np.cumsum(a);pk=np.maximum.accumulate(np.r_[0,eq])[1:]
 return {'mean':float(a.mean()),'p05':q,'cvar05':float(a[a<=q].mean()),'total_return_units':float(a.sum()),'max_drawdown_return_units':float((eq-pk).min())}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();z,m=load(a.cache,a.manifest);allrows=z['rows'];rows=[r for r in allrows if r['signal_date']<SPLIT];dates,entries,exits,updates,lens,ass=build_market(rows);F,A,FS,AS,FP,AP=rule_matrices(rows,dates);base_ret=np.asarray([r['ret'] for r in rows],float)
 n=len(rows);p3names=['equal_weight'];p3init=[1.0];p3rule=[-1]
 for j,k in enumerate(FRULES):
  for q in INIT:p3names.append(f'GRAD_ENTRY_init{q}_{k}');p3init.append(q);p3rule.append(j)
 P3=len(p3names);fd3=np.full((n,P3),-1,np.int16)
 for p,j in enumerate(p3rule):
  if j>=0:fd3[:,p]=F[:,j]
 init3=np.asarray(p3init,float);add3=1-init3;expdays3=np.zeros(P3,float);tr3=[]
 for p,j in enumerate(p3rule):
  if j<0:rret=base_ret.copy();ed=lens.astype(float)
  else:
   mask=F[:,j]>=0;rret=init3[p]*base_ret;rr=np.zeros(n);rr[mask]=np.asarray([rows[i]['exitp'] for i in np.flatnonzero(mask)])/FP[mask,j]-1;rret[mask]+=add3[p]*rr[mask];ed=init3[p]*lens+add3[p]*np.where(mask,np.maximum(lens-FS[:,j],0),0)
  expdays3[p]=float(np.sum(ed));tr3.append(trade_metric(rret))
 scale3=expdays3[0]/expdays3
 wa3,ga3,ca3=simulate(dates,entries,exits,updates,fd3,init3,add3,ass['base_trade_fraction'],np.ones(P3),'buy',False);wb3,gb3,cb3=simulate(dates,entries,exits,updates,fd3,init3,add3,ass['base_trade_fraction'],scale3,'buy',True)
 p4names=['equal_weight'];p4red=[0.0];p4rule=[-1]
 for j,k in enumerate(ARULES):
  for q in REDUCE:p4names.append(f'DERISK_reduce{q}_{k}');p4red.append(q);p4rule.append(j)
 P4=len(p4names);fd4=np.full((n,P4),-1,np.int16)
 for p,j in enumerate(p4rule):
  if j>=0:fd4[:,p]=A[:,j]
 init4=np.ones(P4);red4=np.asarray(p4red,float);expdays4=np.zeros(P4,float);tr4=[]
 for p,j in enumerate(p4rule):
  if j<0:rret=base_ret.copy();expdays4[p]=float(lens.sum())
  else:
   mask=A[:,j]>=0;rret=base_ret.copy();rret[mask]=red4[p]*(AP[mask,j]/np.asarray([rows[i]['ep'] for i in np.flatnonzero(mask)])-1)+(1-red4[p])*base_ret[mask];expdays4[p]=float(np.sum(lens-red4[p]*np.where(mask,np.maximum(lens-AS[:,j],0),0)))
  tr4.append(trade_metric(rret))
 scale4=expdays4[0]/expdays4
 wa4,ga4,ca4=simulate(dates,entries,exits,updates,fd4,init4,red4,ass['base_trade_fraction'],np.ones(P4),'sell',False);wb4,gb4,cb4=simulate(dates,entries,exits,updates,fd4,init4,red4,ass['base_trade_fraction'],scale4,'sell',True)
 def pack(names,tr,wa,ga,ca,wb,gb,cb,scale,fd):
  out=[]
  for p,nm in enumerate(names):out.append({'name':nm,'trigger_rate':float(np.mean(fd[:,p]>=0)) if p else 0.0,'trade_metrics':tr[p],'risk_budget_duration_scale':float(scale[p]),'nonlevered':metrics(dates,wa[:,p],ga[:,p],ca[:,p]),'risk_budget':metrics(dates,wb[:,p],gb[:,p],cb[:,p])})
  return out
 out={'stage':'STAGES3_4_DEVELOPMENT_ONLY','protocol_sha256':sha(a.protocol),'code_sha256':sha(__file__),'cache_manifest':m,'population':{'development':n,'holdout_reserved':sum(r['signal_date']>=SPLIT for r in allrows),'split':SPLIT},'portfolio_assumptions':{**ass,'action_fill':'next observed session open after close-based decision','same_open_order':'de-risk sells, then pro-rata buys/adds','unfilled_adds':'not backfilled'},'stage3':{'candidate_count':P3-1,'policies':pack(p3names,tr3,wa3,ga3,ca3,wb3,gb3,cb3,scale3,fd3)},'stage4':{'candidate_count':P4-1,'policies':pack(p4names,tr4,wa4,ga4,ca4,wb4,gb4,cb4,scale4,fd4)},'holdout_accessed_for_results':False,'verification_a_accessed':False,'verification_b_accessed':False}
 Path(a.output).write_text(json.dumps(out,sort_keys=True)+'\n');print('STAGE3',P3-1,'STAGE4',P4-1);print('OUTPUT',a.output);print('HOLDOUT_ACCESSED_FOR_RESULTS=False');print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()

