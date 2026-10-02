#!/usr/bin/env python3
import argparse,json,math,hashlib,multiprocessing as mp,pickle,gzip,os
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_discovery_adverse_path_phase2 as p2

REFS=['PRIOR_LOW_5','PRIOR_LOW_10','PRIOR_LOW_20','SWING_LOW']
PENS=[0,.25,.5,.75,1.0]; PERS=[1,2,3]; RECLAIMS=[1,2,3,5]; RECS=[.25,.5,.75]
CAPS=[('NONE',None),('ATR6',('atr',6)),('ATR8',('atr',8)),('ATR10',('atr',10)),('ATR12',('atr',12)),('PCT20',('pct',.20)),('PCT25',('pct',.25)),('PCT30',('pct',.30)),('PCT40',('pct',.40))]
SPLIT='2021-09-13'
CACHE_FORMAT='MTS_V4_DISCOVERY_RESEARCH_CACHE_V1'
CACHE_EXPECTED_TRADES=125002
CACHE_EXPECTED_TICKERS=67

def cache_identity(td):
 files=sorted(Path(td).glob('*.json.gz'));h=hashlib.sha256()
 for f in files:
  h.update(f.name.encode());h.update(hashlib.sha256(f.read_bytes()).digest())
 return {'checkpoint_count':len(files),'checkpoint_set_sha256':h.hexdigest()}
def slim_rows(rows):
 # Preserve all reconstructed causal market inputs; remove redundant convolution arrays only.
 out=[]
 for r in rows:
  z=dict(r);z.pop('_ma',None);z.pop('_ema',None);out.append(z)
 return out
def write_cache(path,rows,td):
 ident=cache_identity(td); payload={'format':CACHE_FORMAT,'trade_count':len(rows),'ticker_count':len({r['ticker'] for r in rows}),'split_date':SPLIT,'source':ident,'rows':slim_rows(rows)}
 raw=pickle.dumps(payload,protocol=5);payload_hash=hashlib.sha256(raw).hexdigest();tmp=str(path)+'.tmp'
 with gzip.open(tmp,'wb',compresslevel=3) as f:f.write(raw)
 os.replace(tmp,path)
 meta={k:v for k,v in payload.items() if k!='rows'};meta['uncompressed_payload_sha256']=payload_hash;meta['cache_file_sha256']=hashlib.sha256(Path(path).read_bytes()).hexdigest();Path(str(path)+'.manifest.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
 return meta
def load_cache(path,td):
 with gzip.open(path,'rb') as f:payload=pickle.loads(f.read())
 if payload.get('format')!=CACHE_FORMAT:raise RuntimeError('wrong cache format')
 if payload.get('trade_count')!=CACHE_EXPECTED_TRADES or payload.get('ticker_count')!=CACHE_EXPECTED_TICKERS:raise RuntimeError('cache population mismatch')
 if payload.get('split_date')!=SPLIT:raise RuntimeError('cache split mismatch')
 if payload.get('source')!=cache_identity(td):raise RuntimeError('cache source checkpoint hash mismatch')
 return payload['rows']
def load_rows_cached(td,cache_path,write_if_missing=False):
 cp=Path(cache_path) if cache_path else None
 if cp and cp.exists():
  rows=load_cache(cp,td);print('DISCOVERY_CACHE=HIT '+str(cp),flush=True);return rows
 rows=p2.load_rows(td)
 if cp and write_if_missing:
  m=write_cache(cp,rows,td);print('DISCOVERY_CACHE=CREATED '+str(cp)+' SHA256='+m['cache_file_sha256'],flush=True)
 return rows

def q(a,p):
 a=np.asarray(a,float);return float(np.percentile(a,p)) if len(a) else None
def econ(v):
 a=np.asarray(v,float);pos=a[a>0].sum();neg=-a[a<0].sum();eq=np.cumsum(a);peak=np.maximum.accumulate(np.r_[0,eq])[1:];dd=float(np.min(eq-peak)) if len(a) else None
 w=a[a>0];l=a[a<=0]
 return {'n':len(a),'mean':float(a.mean()),'median':q(a,50),'win_rate':float((a>0).mean()),'profit_factor':float(pos/neg) if neg else None,'avg_winner':float(w.mean()) if len(w) else None,'avg_loser':float(l.mean()) if len(l) else None,'payoff_ratio':float(w.mean()/-l.mean()) if len(w) and len(l) and l.mean()<0 else None,'total_return_units':float(a.sum()),'p01':q(a,1),'p05':q(a,5),'p10':q(a,10),'worst':float(a.min()),'max_drawdown_return_units':dd}
def exit_fill(r,s):
 z=r['path'][s-1];return float(z['close'])/r['ep']-1

def ref_value(r,name):
 b=r['_bars'];si=r['si']
 if name.startswith('PRIOR_LOW_'):
  w=int(name.rsplit('_',1)[1]);return min(float(x['low']) for x in b[si-w+1:si+1]) if si>=w else None
 sl=[v for k,v in r['_sl'].items() if k<=si];return sl[-1][1] if sl else None

def prep(r):
 at=r['atr']; path=r['path']; ep=r['ep']; refs={}
 if not at:return {'refs':{},'cap':{},'recovery':[],'newlow_after':[]}
 # causal running recovery fraction and lower-low event sequence
 trough=ep; rec=[]; running_low=ep; newlow=[]
 for j,z in enumerate(path,1):
  lo=float(z['low']);cl=float(z['close']); isnew=lo<running_low;running_low=min(running_low,lo);newlow.append(isnew)
  trough=min(trough,lo);ae=max(ep-trough,0);rec.append((cl-trough)/ae if ae>0 else 1.)
 for name in REFS:
  rv=ref_value(r,name)
  if rv is None:continue
  rr={}
  for pen in PENS:
   level=rv-pen*at
   closes=[float(z['close']) for z in path]; run=0; first={1:None,2:None,3:None}
   for j,c in enumerate(closes,1):
    run=run+1 if c<level else 0
    for per in PERS:
     if first[per] is None and run>=per:first[per]=j
   rr[pen]={'level':level,'break':first}
  refs[name]=rr
 cap={}
 for lab,spec in CAPS[1:]:
  typ,x=spec;level=ep-x*at if typ=='atr' else ep*(1-x);hit=None;ret=None
  for j,z in enumerate(path,1):
   op=float(z['open']);lo=float(z['low'])
   if op<=level:hit=j;ret=op/ep-1;break
   if lo<=level:hit=j;ret=level/ep-1;break
  cap[lab]=(hit,ret)
 return {'refs':refs,'cap':cap,'recovery':rec,'newlow':newlow}

def stop_session(r,pr,pol):
 rr=pr['refs'].get(pol['ref'],{}).get(pol['pen']);
 if not rr:return None
 br=rr['break'][pol['persist']]
 if br is None:return None
 if pol['family']=='A':return br
 deadline=br+pol['reclaim']
 # failed reclaim means no close above fixed broken threshold through allowance
 for s in range(br,min(deadline,len(r['path']))+1):
  if float(r['path'][s-1]['close'])>rr['level']:return None
 decision=min(deadline,len(r['path']))
 if deadline>len(r['path']):return None
 if pol['lower']:
  base=min(float(z['low']) for z in r['path'][:br]); later=None
  for s in range(decision+1,len(r['path'])+1):
   if float(r['path'][s-1]['low'])<base:later=s;break
  if later is None:return None
  decision=later
 if pol['rec'] is not None:
  if decision>len(pr['recovery']) or pr['recovery'][decision-1]>=pol['rec']:return None
 return decision

def policies():
 out=[]
 for ref in REFS:
  for pen in PENS:
   for per in PERS:
    out.append({'family':'A','ref':ref,'pen':pen,'persist':per,'reclaim':None,'lower':False,'rec':None})
    for rw in RECLAIMS:
     out.append({'family':'B','ref':ref,'pen':pen,'persist':per,'reclaim':rw,'lower':False,'rec':None})
     out.append({'family':'C','ref':ref,'pen':pen,'persist':per,'reclaim':rw,'lower':True,'rec':None})
     for rec in RECS:
      out.append({'family':'D','ref':ref,'pen':pen,'persist':per,'reclaim':rw,'lower':False,'rec':rec})
      out.append({'family':'E','ref':ref,'pen':pen,'persist':per,'reclaim':rw,'lower':True,'rec':rec})
 for i,p in enumerate(out):p['id']=f'DAS{i:04d}'
 return out

def apply(rows,pre,ix,pol,cap='NONE'):
 vals=[]; trig=[]; sessions=[]
 for i in ix:
  r=rows[i];s=stop_session(r,pre[i],pol);v=r['ret'];why=None
  if s is not None:v=exit_fill(r,s);why='DYNAMIC'
  if cap!='NONE':
   cs,cv=pre[i]['cap'].get(cap,(None,None))
   if cs is not None and (s is None or cs<=s):s=cs;v=cv;why='CAP'
  vals.append(v);trig.append((i,v,s,why))
 return np.asarray(vals),trig

def report(rows,ix,vals,trig,base):
 e=econ(vals); stopped=[x for x in trig if x[2] is not None];wk=[x for x in stopped if rows[x[0]]['winner']];lc=[x for x in stopped if not rows[x[0]]['winner']]
 fore=sum(max(0,rows[i]['ret']-v) for i,v,_,_ in wk); avoided=sum(max(0,v-rows[i]['ret']) for i,v,_,_ in lc)
 sev=avoided-fore; by=defaultdict(float)
 for i,v,_,_ in lc:by[rows[i]['ticker']]+=max(0,v-rows[i]['ret'])
 for i,v,_,_ in wk:by[rows[i]['ticker']]-=max(0,rows[i]['ret']-v)
 breadth={'tickers':len({rows[i]['ticker'] for i in ix}),'years':len({rows[i]['year'] for i in ix}),'families':len({rows[i]['family'] for i in ix}),'genomes':len({rows[i]['genome'] for i in ix})}
 return {'economics':e,'exits_triggered':len(stopped),'participation':len(stopped)/len(ix),'median_exit_session':q([x[2] for x in stopped],50),'original_winners_killed':len(wk),'original_winner_kill_rate':len(wk)/sum(rows[i]['winner'] for i in ix),'foregone_winner_profit_total':fore,'foregone_winner_profit_mean':fore/len(wk) if wk else 0,'original_losers_truncated':len(lc),'original_loser_truncate_rate':len(lc)/sum(not rows[i]['winner'] for i in ix),'loss_avoided_total':avoided,'loss_avoided_mean':avoided/len(lc) if lc else 0,'stop_economic_value':sev,'max_ticker_sev_share':max([x for x in by.values() if x>0],default=0)/sev if sev>0 else None,'delta':{'expectancy':e['mean']-base['mean'],'profit_factor':e['profit_factor']-base['profit_factor'],'avg_loser':e['avg_loser']-base['avg_loser'],'p05':e['p05']-base['p05'],'worst':e['worst']-base['worst'],'max_drawdown':e['max_drawdown_return_units']-base['max_drawdown_return_units']},'breadth':breadth}

_G={}
def init_eval(rows,pre,ix,base):
 global _G;_G={"rows":rows,"pre":pre,"ix":ix,"base":base}
def eval_policy_allcaps(pol):
 rows=_G["rows"];pre=_G["pre"];ix=_G["ix"];base=_G["base"];vals={c:[] for c,_ in CAPS};trs={c:[] for c,_ in CAPS}
 for i in ix:
  r=rows[i];s=stop_session(r,pre[i],pol);dv=r["ret"] if s is None else exit_fill(r,s)
  vals["NONE"].append(dv);trs["NONE"].append((i,dv,s,"DYNAMIC" if s else None))
  for cap,_ in CAPS[1:]:
   cs,cv=pre[i]["cap"].get(cap,(None,None));v=dv;ss=s;why="DYNAMIC" if s else None
   if cs is not None and (s is None or cs<=s):v=cv;ss=cs;why="CAP"
   vals[cap].append(v);trs[cap].append((i,v,ss,why))
 z=report(rows,ix,np.asarray(vals["NONE"]),trs["NONE"],base);z["policy"]=pol;z["eligible"]=eligible(z)
 caps={}
 for cap,_ in CAPS[1:]:
  rr=report(rows,ix,np.asarray(vals[cap]),trs[cap],base);caps[cap]={"mean":rr["economics"]["mean"],"pf":rr["economics"]["profit_factor"],"p05":rr["economics"]["p05"],"worst":rr["economics"]["worst"],"stop_economic_value":rr["stop_economic_value"],"winner_kill_rate":rr["original_winner_kill_rate"]}
 return z,caps

def eligible(z):
 e=z['economics'];d=z['delta'];b=z['breadth'];return z['stop_economic_value']>0 and d['expectancy']>0 and d['profit_factor']>=0 and d['avg_loser']>0 and d['p05']>0 and b['tickers']>=20 and b['years']>=5 and b['families']>=4 and (z['max_ticker_sev_share'] is None or z['max_ticker_sev_share']<=.20)
def dominates(a,b):
 va=[a['delta']['expectancy'],a['stop_economic_value'],a['delta']['p05'],a['delta']['max_drawdown'],-a['original_winner_kill_rate']];vb=[b['delta']['expectancy'],b['stop_economic_value'],b['delta']['p05'],b['delta']['max_drawdown'],-b['original_winner_kill_rate']]
 return all(x>=y for x,y in zip(va,vb)) and any(x>y for x,y in zip(va,vb))
def cluster_ci(rows,pre,ix,pol,B=200):
 by=defaultdict(list)
 for i in ix:by[rows[i]['ticker']].append(i)
 ts=sorted(by);rng=np.random.default_rng(20261001);dm=[];ds=[]
 for _ in range(B):
  samp=[]
  for t in rng.choice(ts,len(ts),replace=True):samp.extend(by[t])
  base=econ([rows[i]['ret'] for i in samp]);v,tr=apply(rows,pre,samp,pol);z=report(rows,samp,v,tr,base);dm.append(z['delta']['expectancy']);ds.append(z['stop_economic_value']/len(samp))
 return {'method':'ticker-cluster bootstrap; 200 deterministic resamples','expectancy_delta_ci95':[q(dm,2.5),q(dm,97.5)],'stop_economic_value_per_trade_ci95':[q(ds,2.5),q(ds,97.5)]}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--trajectory-dir',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--output',required=True);ap.add_argument('--markdown',required=True);ap.add_argument('--cache');ap.add_argument('--write-cache',action='store_true');a=ap.parse_args()
 proto=Path(a.protocol).read_bytes();ph=hashlib.sha256(proto).hexdigest();rows=load_rows_cached(a.trajectory_dir,a.cache,a.write_cache);print('DYNAMIC_STOP_ROWS='+str(len(rows)),flush=True)
 pre=[prep(r) for r in rows];dev=[i for i,r in enumerate(rows) if r['signal_date']<SPLIT];hold=[i for i,r in enumerate(rows) if r['signal_date']>=SPLIT];baseD=econ([rows[i]['ret'] for i in dev]);baseH=econ([rows[i]['ret'] for i in hold]);ps=policies();print('DYNAMIC_STOP_POLICIES='+str(len(ps)),flush=True)
 devres=[];caps={c:[] for c,_ in CAPS[1:]}
 workers=min(6,mp.cpu_count());print('DYNAMIC_STOP_WORKERS='+str(workers),flush=True)
 with mp.get_context('fork').Pool(workers,initializer=init_eval,initargs=(rows,pre,dev,baseD)) as pool:
  for n,(z,cz) in enumerate(pool.imap(eval_policy_allcaps,ps,chunksize=4),1):
   devres.append(z)
   for cap in caps:caps[cap].append({'policy_id':z['policy']['id'],**cz[cap]})
   if n%100==0:print(f'DYNAMIC_STOP_DEV={n}/{len(ps)}',flush=True)
 elig=[z for z in devres if z['eligible']];front=[z for z in elig if not any(dominates(x,z) for x in elig if x is not z)]
 # Nominate up to 3: conservative=min kill, balanced=max SEV, aggressive=max p05 among frontier.
 nom=[]
 for key in [lambda z:-z['original_winner_kill_rate'],lambda z:z['stop_economic_value'],lambda z:z['delta']['p05']]:
  if front:
   z=max(front,key=key)
   if z['policy']['id'] not in [x['policy']['id'] for x in nom]:nom.append(z)
 nom=nom[:3]
 holdres=[]
 for z in nom:
  pol=z['policy'];v,tr=apply(rows,pre,hold,pol);h=report(rows,hold,v,tr,baseH);h['policy']=pol;h['survives_holdout']=h['stop_economic_value']>0 and h['delta']['expectancy']>=0 and h['delta']['avg_loser']>0 and h['delta']['p05']>0 and h['breadth']['tickers']>=15 and h['breadth']['years']>=3;h['degradation']={'expectancy_delta':h['delta']['expectancy']-z['delta']['expectancy'],'sev_per_trade':h['stop_economic_value']/len(hold)-z['stop_economic_value']/len(dev)};h['uncertainty']=cluster_ci(rows,pre,hold,pol);holdres.append(h)
 # Catastrophic sensitivity for every policy was computed in the same causal pass above.
 survivors=[x for x in holdres if x['survives_holdout']]
 conclusion='DISCOVERY CANDIDATE' if survivors else 'DISCOVERY NULL'
 out={'format':'MTS_V4_DYNAMIC_ADVERSE_PATH_STOP_DISCOVERY_V1','protocol_sha256':ph,'protocol_commit':'4f759a6245672941488d5c1e29697fb0663761b9','population':{'trades':len(rows),'tickers':len({r['ticker'] for r in rows}),'development':len(dev),'holdout':len(hold),'split_date':SPLIT},'verification_a_accessed':False,'verification_b_accessed':False,'baseline':{'development':baseD,'holdout':baseH},'candidate_count':len(ps),'eligible_development_count':len(elig),'pareto_frontier_count':len(front),'development_results':devres,'pareto_frontier':[z['policy']['id'] for z in front],'nominated_development':nom,'holdout_replay':holdres,'catastrophic_cap_sensitivity_development':caps,'conclusion':conclusion,'governance':'DISCOVERY ONLY — NOT VALIDATED OR PROMOTED'}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 md=['# MTS Dynamic Adverse-Path Stop Discovery — 2026-10-01','',f'**Conclusion:** {conclusion}',f'**Verification A accessed:** False  ','**Verification B accessed:** False',f'**Candidates:** {len(ps)}; Development eligible: {len(elig)}; Pareto frontier: {len(front)}','',f'Development baseline mean {baseD["mean"]:.6f}, PF {baseD["profit_factor"]:.4f}, p05 {baseD["p05"]:.6f}.',f'Holdout baseline mean {baseH["mean"]:.6f}, PF {baseH["profit_factor"]:.4f}, p05 {baseH["p05"]:.6f}.','','## Nominated policies']
 for z,h in zip(nom,holdres):md += [f'- **{z["policy"]["id"]}** {z["policy"]}: Dev Δmean {z["delta"]["expectancy"]:+.6f}, SEV {z["stop_economic_value"]:+.3f}, Δp05 {z["delta"]["p05"]:+.6f}; Holdout Δmean {h["delta"]["expectancy"]:+.6f}, SEV {h["stop_economic_value"]:+.3f}, Δp05 {h["delta"]["p05"]:+.6f}, survives={h["survives_holdout"]}.']
 md += ['','No Verification evidence was accessed. No policy is promoted by this experiment.']
 Path(a.markdown).write_text('\n'.join(md)+'\n');print('DYNAMIC_STOP_CONCLUSION='+conclusion,flush=True);print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False',flush=True)
if __name__=='__main__':main()
