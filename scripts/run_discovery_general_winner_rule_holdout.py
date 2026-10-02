#!/usr/bin/env python3
import argparse,json,heapq
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
SEED=20261002;BOOT=2000;MINN=100

def stat(h):
 a=np.asarray([x[0] for x in h],float);w=a>0
 return {'ev':float(a.mean()),'win_rate':float(w.mean()),'p10_loss':max(1e-12,-float(np.quantile(a,.10)))}
def causal_all(rows):
 # score every trade using only outcomes whose exits predate its signal date; Development naturally seeds Holdout histories.
 by=defaultdict(list)
 for i,r in enumerate(rows):by[r['signal_date']].append(i)
 gh=defaultdict(list);fh=defaultdict(list);glob=[];pending=[];ev=np.full(len(rows),np.nan);wr=np.full(len(rows),np.nan);p10=np.full(len(rows),np.nan);src=np.empty(len(rows),object)
 for d in sorted(by):
  while pending and pending[0][0]<d:
   _,i=heapq.heappop(pending);r=rows[i];x=(float(r['ret']),float(r['mae']));gh[r['genome']].append(x);fh[r['family']].append(x);glob.append(x)
  cache={}
  for i in by[d]:
   r=rows[i]
   if len(gh[r['genome']])>=MINN:key=('genome',r['genome']);h=gh[r['genome']]
   elif len(fh[r['family']])>=MINN:key=('family',r['family']);h=fh[r['family']]
   elif len(glob)>=MINN:key=('global','global');h=glob
   else:key=('unavailable','x');h=None
   src[i]=key[0]
   if h is not None:
    if key not in cache:cache[key]=stat(h)
    q=cache[key];ev[i]=q['ev'];wr[i]=q['win_rate'];p10[i]=q['p10_loss']
  for i in by[d]:heapq.heappush(pending,(rows[i]['path'][-1]['date'],i))
 return ev,wr,p10,src
def fit_scale(score,mask,floor,cap):
 a=np.asarray(score);m=mask&np.isfinite(a);raw=np.zeros(len(a));raw[m]=np.maximum(a[m],0);pos=raw[m&(raw>0)];base=float(np.median(pos));lo,hi=0.,1000/max(base,1e-12)
 for _ in range(80):
  mid=(lo+hi)/2;w=np.ones(len(a));w[m]=np.clip(raw[m]*mid,floor,cap)
  if w[m].mean()>1:hi=mid
  else:lo=mid
 return (lo+hi)/2
def weights(score,scale,floor,cap):
 a=np.asarray(score);m=np.isfinite(a);w=np.ones(len(a));w[m]=np.clip(np.maximum(a[m],0)*scale,floor,cap);return w
def groups(rows,d,key):
 s=defaultdict(float)
 for r,x in zip(rows,d):s[r[key]]+=float(x)
 pos=[v for v in s.values() if v>0];tot=sum(pos)
 return {'groups':len(s),'positive':len(pos),'fraction':len(pos)/len(s) if s else 0,'max_positive_share':max(pos)/tot if pos and tot>0 else None}
def boot(rows,d):
 tick=sorted(set(r['ticker'] for r in rows));ix={t:i for i,t in enumerate(tick)};s=np.zeros(len(tick));n=np.zeros(len(tick),int)
 for r,x in zip(rows,d):j=ix[r['ticker']];s[j]+=x;n[j]+=1
 rng=np.random.default_rng(SEED);v=[]
 for _ in range(BOOT):q=rng.integers(0,len(tick),len(tick));v.append(s[q].sum()/n[q].sum())
 return [float(np.quantile(v,.025)),float(np.quantile(v,.975))]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--nominees',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();z,m=load(a.cache,a.manifest);rows=z['rows'];nom=json.load(open(a.nominees));devmask=np.array([r['signal_date']<SPLIT for r in rows]);holdmask=~devmask;ev,wr,p10,src=causal_all(rows);scores={'ev_p10':np.maximum(ev,0)/p10,'ev_p10_x_winrate':np.maximum(ev,0)*wr/p10};hold=[r for r,x in zip(rows,holdmask) if x];ret=np.array([r['ret'] for r in hold]);Ws=[np.ones(len(hold))];meta=[]
 for n in nom['nominees']:
  sc=fit_scale(scores[n['score']],devmask,n['floor'],n['cap']);wall=weights(scores[n['score']],sc,n['floor'],n['cap']);Ws.append(wall[holdmask]);meta.append((n,sc))
 W=np.column_stack(Ws);dates,en,ex,up,lens,ass=build_events(hold);wa,ga,ca=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False);base=metrics(dates,wa[:,0],ga[:,0],ca[:,0]);res=[];req=nom['holdout_pass_requirements']
 for j,(n,sc) in enumerate(meta,1):
  w=W[:,j];d=ret*(w-1);g={k:groups(hold,d,k) for k in ['ticker','year','family','genome']};ci=boot(hold,d);pm=metrics(dates,wa[:,j],ga[:,j],ca[:,j]);gate={'positive_mean_sizing_contribution':float(d.mean())>0,'positive_ticker_fraction_min':g['ticker']['fraction']>=req['positive_ticker_fraction_min'],'positive_year_fraction_min':g['year']['fraction']>=req['positive_year_fraction_min'],'positive_family_fraction_min':g['family']['fraction']>=req['positive_family_fraction_min'],'max_positive_ticker_share':(g['ticker']['max_positive_share'] or 1)<=req['max_positive_ticker_share'],'max_positive_genome_share':(g['genome']['max_positive_share'] or 1)<=req['max_positive_genome_share'],'ticker_cluster_ci95_lower_gt_zero':ci[0]>0,'terminal_wealth_gt_equal':pm['terminal_wealth']>base['terminal_wealth'],'not_both_max_drawdown_and_cvar05_worse':not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05'])};res.append({'id':n['id'],'score':n['score'],'floor':n['floor'],'cap':n['cap'],'development_fitted_scale':sc,'mean_sizing_contribution':float(d.mean()),'groups':g,'ticker_cluster_ci95':ci,'portfolio':pm,'gates':gate,'pass':all(gate.values())})
 out={'stage':'GENERAL_WINNER_RULE_DISCOVERY_HOLDOUT_ONCE','protocol_sha256':sha(a.protocol),'nominee_manifest_sha256':sha(a.nominees),'population':{'holdout':len(hold),'tickers':len(set(r['ticker'] for r in hold))},'baseline':base,'holdout_score_sources':dict(Counter(src[holdmask])),'results':res,'verification_a_accessed':False,'verification_b_accessed':False,'holdout_replayed_once':True};Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('BASE',base)
 for x in res:print(x['id'],'PASS',x['pass'],'meanD',x['mean_sizing_contribution'],'T',x['groups']['ticker']['positive'],'/',x['groups']['ticker']['groups'],'Y',x['groups']['year']['positive'],'/',x['groups']['year']['groups'],'F',x['groups']['family']['positive'],'/',x['groups']['family']['groups'],'CI',x['ticker_cluster_ci95'],'wealth',x['portfolio']['terminal_wealth'],'DD',x['portfolio']['max_drawdown'],'CVaR',x['portfolio']['daily_cvar05'],'GATES',x['gates'])
 print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()
