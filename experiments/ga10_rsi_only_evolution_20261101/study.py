"""GA10 isolated RSI-only evolutionary study. No evaluation feedback to search."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS']: os.environ[k]='1'
from pathlib import Path
import json,time,hashlib,traceback,argparse
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
from numba import njit
import prototype
ROOT=Path(__file__).resolve().parent
SIZE=53

def prepare(c,o):
    d=prototype.prepare(c,o)
    d['screen']=d['rsi'].copy() # RSI bottom floor(N/5), stable ticker ties; no MA/acceleration eligibility
    return d

def load(path=prototype.SOURCE):
    raw=pd.read_parquet(path);raw.date=pd.to_datetime(raw.date)
    raw=raw[raw.date<='2018-12-31'].copy()
    if raw.duplicated(['date','ticker']).any(): raise ValueError('duplicate price keys')
    c=raw.pivot(index='date',columns='ticker',values='adj_close').sort_index().sort_index(axis=1)
    o=raw.assign(ao=raw.open*raw.adj_close/raw.close).pivot(index='date',columns='ticker',values='ao').reindex_like(c)
    return prepare(c,o)

def arrays(d,start,end):
    ids=np.flatnonzero((d['dates']>=start)&(d['dates']<=end));a,b=ids[0],ids[-1]+1
    monthly=np.array([t==a or d['dates'][t].to_period('M')!=d['dates'][t-1].to_period('M') for t in range(a,b)])
    return tuple(np.ascontiguousarray(z) for z in (d['c'][a-1:b-1],d['o'][a:b],d['c'][a:b],d['x'][a-1:b-1],d['screen'][a:b],monthly))

@njit(cache=True)
def simulate(g,prior,opens,closes,x,screen,monthly,baseline=0):
    T,N=closes.shape;shares=np.zeros(N);basis=np.zeros(N);age=np.zeros(N)
    cash=1.;peak=1.;riskpeak=1.;mdd=0.;cooldown=0;fees=0.;turnover=0.
    path=np.zeros((T,6));counts=np.zeros(5,np.int64);events=np.zeros((T,N),np.int8)
    ctl=1/(1+np.exp(-g[45:]));entry=.1+.8*ctl[0];add=.05+.45*ctl[1];reduce=.1+.8*ctl[2]
    cap=.05+.25*ctl[3];exposure=.2+.8*ctl[4];stop=.08+.16*ctl[5]
    wait=1+int(62*ctl[6]);riskpower=2*ctl[7]
    for t in range(T):
        values=np.zeros(N);ov=np.zeros(N);lastnav=cash;onav=cash
        for j in range(N):
            if shares[j]>1e-12:
                if not (np.isfinite(prior[t,j]) and prior[t,j]>0 and np.isfinite(opens[t,j]) and opens[t,j]>0): raise ValueError('missing held prior/open')
                values[j]=shares[j]*prior[t,j];ov[j]=shares[j]*opens[t,j]
            lastnav+=values[j];onav+=ov[j]
        dd=max(0.,1-lastnav/riskpeak);desired=np.zeros(N);acts=np.ones(N,np.int64)
        stopped=False
        if baseline==0:
            if cooldown>0:
                cooldown-=1
                if cooldown==0: riskpeak=lastnav;dd=0.
            if dd>=stop and cooldown==0:
                cooldown=wait;stopped=True
            for j in range(N):
                held=shares[j]>1e-12;w=values[j]/lastnav;want=w
                scores=np.zeros(5);finite=True
                for h in range(5):
                    scores[h]=g[h*9]
                    for k in range(6):
                        v=x[t,j,k]
                        if not np.isfinite(v):finite=False;v=0.
                        scores[h]+=g[h*9+1+k]*v
                    pnl=prior[t,j]/basis[j]-1 if basis[j]>0 else 0.
                    scores[h]+=g[h*9+7]*max(-1.,min(1.,pnl))+g[h*9+8]*min(age[j],252.)/252
                allocation=cap/(1+np.exp(-max(-30.,min(30.,scores[4]))))
                # Volatility-responsive allocation evolves independently of entry eligibility.
                vol=x[t,j,5]
                if np.isfinite(vol) and vol>0: allocation*=min(1.,(.25/vol)**riskpower)
                if held and (scores[3]>0 or stopped):want=0.;acts[j]=4
                elif held and scores[2]>0:want*=1-reduce;acts[j]=3
                elif held and scores[1]>0 and cooldown==0:want=min(cap,w+add*allocation);acts[j]=2
                elif not held and screen[t,j] and scores[0]>0 and cooldown==0:want=entry*allocation;acts[j]=0
                desired[j]=min(cap,want)
            total=desired.sum()
            if total>exposure:desired*=exposure/total
            for j in range(N):
                desired[j]=max(0.,ov[j]+(desired[j]-values[j]/lastnav)*lastnav)/onav
                if acts[j]==4:desired[j]=0.
            if desired.sum()>1:desired/=desired.sum()
        elif baseline==1:
            if monthly[t]:desired=screen[t].astype(np.float64)/max(1,screen[t].sum())
            else:desired=ov/onav
        # baseline=2 stays cash
        trade=baseline==0 or baseline==2 or monthly[t]
        fee=0.
        if trade:
            for j in range(N):
                if not np.isfinite(opens[t,j]) or opens[t,j]<=0:desired[j]=0.
            lo=0.;hi=onav
            for _ in range(40):
                mid=(lo+hi)/2;f=.001*np.abs(desired*mid-ov).sum()
                if mid+f>onav:hi=mid
                else:lo=mid
            dollars=desired*((lo+hi)/2);delta=dollars-ov;fee=.001*np.abs(delta).sum()
            cash=onav-dollars.sum()-fee
            if cash < -1e-9:raise ValueError('negative cash')
            cash=max(0.,cash)
            for j in range(N):
                old=shares[j];new=dollars[j]/opens[t,j] if np.isfinite(opens[t,j]) and opens[t,j]>0 else 0.
                if new>old+1e-12:
                    basis[j]=(old*basis[j]+(new-old)*opens[t,j])/new
                    if old<=1e-12:age[j]=0
                shares[j]=new
                if new<=1e-12:basis[j]=0.
                if abs(delta[j])>1e-11:
                    action=acts[j] if baseline==0 else (0 if delta[j]>0 else 4)
                    counts[action]+=1;events[t,j]=action+1
            fees+=fee;turnover+=np.abs(delta).sum()/onav
        nav=cash;heldcount=0
        for j in range(N):
            if shares[j]>1e-12:
                if not np.isfinite(closes[t,j]) or closes[t,j]<=0:raise ValueError('missing held close')
                nav+=shares[j]*closes[t,j];age[j]+=1;heldcount+=1
                if acts[j]==1:counts[1]+=1
        # Daily close MDD includes initial wealth. Open-mark drawdown recorded separately.
        peak=max(peak,nav);mdd=max(mdd,1-nav/peak);riskpeak=max(riskpeak,nav)
        path[t]=np.array([nav,onav-fee,fee,1-cash/nav,heldcount,cooldown])
    cagr=nav**(252./T)-1;calmar=cagr/mdd if mdd>1e-12 else 0.
    return np.array([cagr,mdd,calmar,nav,fees,turnover]),path,counts,events

DATA=None
def init_worker(a):
    global DATA
    DATA=a

def score(g):return simulate(g,*DATA)[0]
def metric(m):return dict(zip(['cagr','mdd','calmar','final_nav','fees','turnover'],map(float,m)))
def dominates(a,b):return a[0]>=b[0] and a[1]<=b[1] and a[2]>=b[2] and (a[0]>b[0] or a[1]<b[1] or a[2]>b[2])
def frontier_add(front,item):
    m=item['m']
    if any(dominates(z['m'],m) or np.array_equal(z['m'][:3],m[:3]) for z in front):return front,False
    return [z for z in front if not dominates(m,z['m'])]+[item],True

def atomic(path,obj):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2));tmp.replace(path)
def save_front(front,folder):
    atomic(folder/'frontier.json',front)
    pd.DataFrame([dict(generation=z['generation'],candidate=z['candidate'],**metric(z['m']),genome=json.dumps(z['g'])) for z in front]).to_csv(folder/'frontier.csv',index=False)
def report(folder,state,metrics=None):
    hist=pd.read_csv(folder/'generations.csv') if (folder/'generations.csv').exists() else pd.DataFrame()
    lines=['# GA10 RSI-only evolutionary research','',f"Status: {state['status']}. Completed generations: {state['completed']}; consecutive stagnant: {state['stale']}; runtime: {state['elapsed']:.1f} seconds.",'', 'Training: DEV79 2009–2013 only. Evaluation: 2014–2018 after search frozen. Eight worker processes; population 64; maximum 1000 completed generations, early stop at 100 consecutive generations without meaningful best feasible CAGR or frontier improvement. Seed 1010. No GA6/GA7 code or results used.','', 'Fixed screen: prior-session Wilder-style RSI14 bottom floor(20% × eligible count), at least one, stable ticker ties, refreshed monthly. Eligible means finite positive prior adjusted close and finite RSI; no MA20/acceleration eligibility. MA20, acceleration, momentum and volatility remain causal optional policy inputs. Only new positions require screen membership; held stocks can be added/reduced/exited offscreen.','', 'Five evolved action/allocation heads; eight control genes include position cap, exposure, risk stop, cooldown 1–63 sessions, volatility sizing. A stop liquidates and temporarily blocks purchases; cooldown expiry resets the risk reference so cash can re-enter. Daily performance high-water mark never resets. Reduce has priority over add and below exit.','', 'Net returns include 10 bp on each actual buy/sell side. Signals at prior close, executions at next adjusted open. Daily MDD is close-to-close including initial capital; open/close MDD is also reported for saved paths. Initial capital 1, fractional shares, zero cash interest; final holdings marked without liquidation fees.','', 'Meaningful improvement requires feasible CAGR gain >0.0001 (one annual basis point) or a new nondominated point that is not epsilon-covered by the meaningful archive (CAGR 0.0001, MDD 0.0001, Calmar 0.001). Pareto directions: CAGR up, absolute daily MDD down, Calmar up. All exact nondominated points saved, including infeasible MDD ≥25%. Champion selection maximizes CAGR among MDD <25%; all-result maximum CAGR and maximum Calmar also retained.','', 'Adjusted historical archive and retrospective membership are not certified point-in-time. No survivorship-free claim. The 2014–2018 period was examined in prior research and is not pristine validation. Evaluation never selects or modifies genomes. DEV87 is a separate frozen stock transfer, also retrospective.']
    if len(hist):lines+=['',f"Latest generation: `{hist.iloc[-1].to_json()}`.",'','See generations.csv, candidates.csv, frontier.csv/json, champions.json, checkpoint.json, freeze.json, tests.log, smoke/, provenance.json and terminal metrics.csv.']
    if metrics:
        lines+=['','|Universe/split|Policy|CAGR|Daily MDD|Calmar|Feasible <25%|','|---|---|---:|---:|---:|---|']
        for z in metrics:lines.append(f"|{z['split']}|{z['policy']}|{z['cagr']:.2%}|{z['mdd']:.2%}|{z['calmar']:.3f}|{z['mdd']<.25}|")
    (folder/'REPORT.md').write_text('\n'.join(lines)+'\n')

def search(a,folder,maxgen=1000,popsize=64,patience=100):
    folder.mkdir(exist_ok=True,parents=True);started=time.monotonic();rng=np.random.default_rng(1010)
    cp=folder/'checkpoint.json';front=[];meaningful=[];stale=0;completed=0;elapsed=0.;bestfeas=-1e99
    pop=rng.normal(0,.65,(popsize,SIZE))
    # Random initial genomes only; evaluation never seeds the population.
    if cp.exists():
        s=json.loads(cp.read_text());pop=np.array(s['pop']);rng.bit_generator.state=s['rng'];front=s['front'];meaningful=s['meaningful'];stale=s['stale'];completed=s['completed'];elapsed=s['elapsed'];bestfeas=s['bestfeas']
        for name in ['generations.csv','candidates.csv']:
            f=folder/name
            if f.exists():
                df=pd.read_csv(f);df[df.generation<=completed].to_csv(f,index=False)
    with ProcessPoolExecutor(max_workers=8,initializer=init_worker,initargs=(a,)) as pool:
        for gen in range(completed,maxgen):
            if stale>=patience:break
            tick=time.monotonic();ms=list(pool.map(score,pop,chunksize=max(1,popsize//32)))
            if not np.isfinite(ms).all():raise ValueError('nonfinite candidate metrics')
            improved=False;rows=[]
            for k,(g,m) in enumerate(zip(pop,ms)):
                item=dict(g=g.tolist(),m=m.tolist(),generation=gen+1,candidate=k)
                front,added=frontier_add(front,item)
                if m[1]<.25 and m[0]>bestfeas+1e-4:bestfeas=float(m[0]);improved=True
                if added:
                    eps=np.array([1e-4,1e-4,1e-3]);v=m[:3]*np.array([1,-1,1])
                    covered=any(np.all(np.array(z['m'][:3])*np.array([1,-1,1])+eps>=v) for z in meaningful)
                    if not covered:
                        meaningful,_=frontier_add(meaningful,item);improved=True
                rows.append(dict(generation=gen+1,candidate=k,**metric(m),genome=json.dumps(g.tolist())))
            stale=0 if improved else stale+1;completed=gen+1
            feasible=[z for z in front if z['m'][1]<.25]
            champion=max(feasible,key=lambda z:z['m'][0]) if feasible else min(front,key=lambda z:z['m'][1])
            # Elitism combines feasible CAGR leaders and objective extremes; frontier reservoir maintains diversity.
            order=sorted(range(popsize),key=lambda i:(ms[i][1]<.25,ms[i][0] if ms[i][1]<.25 else -ms[i][1]),reverse=True)
            parents=[pop[i] for i in order[:max(4,popsize//4)]]+[np.array(z['g']) for z in front]
            elite=[np.array(champion['g']),np.array(max(front,key=lambda z:z['m'][0])['g']),np.array(min(front,key=lambda z:z['m'][1])['g'])]
            new=elite[:]
            while len(new)<popsize:
                if rng.random()<.08:child=rng.normal(0,1,SIZE)
                else:
                    p,q=rng.integers(len(parents),size=2);child=np.where(rng.random(SIZE)<.5,parents[p],parents[q]).copy()
                    scale=rng.choice(np.array([.03,.1,.3,.7]));mask=rng.random(SIZE)<rng.uniform(.1,.8);child+=mask*rng.normal(0,scale,SIZE)
                new.append(np.clip(child,-8,8))
            pop=np.array(new);total=elapsed+time.monotonic()-started
            row=dict(generation=completed,seconds=time.monotonic()-tick,elapsed_seconds=total,stagnant=stale,meaningful_improvement=improved,frontier_size=len(front),best_feasible_cagr=champion['m'][0] if feasible else None,champion_mdd=champion['m'][1],champion_calmar=champion['m'][2],max_cagr=max(z['m'][0] for z in front))
            pd.DataFrame(rows).to_csv(folder/'candidates.csv',mode='a',header=not (folder/'candidates.csv').exists(),index=False)
            pd.DataFrame([row]).to_csv(folder/'generations.csv',mode='a',header=not (folder/'generations.csv').exists(),index=False)
            save_front(front,folder)
            s=dict(status='running',completed=completed,stale=stale,elapsed=total,bestfeas=bestfeas,pop=pop.tolist(),rng=rng.bit_generator.state,front=front,meaningful=meaningful)
            atomic(cp,s);report(folder,s)
            print(json.dumps(row),flush=True)
    s['status']='stopped: 100 stagnant generations' if stale>=patience else 'completed generation budget';atomic(cp,s);report(folder,s)
    return front,s

def evaluate(d,g,split,policy,folder,baseline=0):
    a=arrays(d,'2009-01-01' if 'train' in split else '2014-01-01','2013-12-31' if 'train' in split else '2018-12-31')
    m,path,counts,events=simulate(np.array(g),*a,baseline)
    dates=d['dates'][(d['dates']>=('2009-01-01' if 'train' in split else '2014-01-01'))&(d['dates']<=('2013-12-31' if 'train' in split else '2018-12-31'))]
    frame=pd.DataFrame(path,columns=['nav','open_nav','fee','exposure','holdings','cooldown']);frame.insert(0,'date',dates);frame.to_csv(folder/f'{split}_{policy}_daily.csv',index=False)
    ti,ji=np.nonzero(events);pd.DataFrame(dict(date=dates[ti],ticker=np.array(d['names'])[ji],action=np.array(['entry','hold','add','reduce','exit'])[events[ti,ji]-1],in_screen=a[4][ti,ji])).to_csv(folder/f'{split}_{policy}_events.csv',index=False)
    marks=np.r_[1.,path[:,[1,0]].ravel()];openmdd=float(np.max(1-marks/np.maximum.accumulate(marks)))
    return dict(split=split,policy=policy,**metric(m),open_close_mdd=openmdd,actions=dict(zip(['entry','hold','add','reduce','exit'],counts.tolist())))

def main():
    wall_started=time.monotonic()
    d=load();a=arrays(d,'2009-01-01','2013-12-31')
    atomic(ROOT/'provenance.json',dict(source=str(prototype.SOURCE),source_sha256=hashlib.sha256(prototype.SOURCE.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),workers=8,seed=1010,fee_side=.001,pit_certified=False))
    if not (ROOT/'smoke_gate.json').exists():
        tick=time.monotonic();front,s=search(tuple(z[:126] for z in a),ROOT/'smoke',2,16,100)
        g=np.array(front[0]['g']);r=simulate(g,*a);r2=simulate(g,*a)
        assert np.array_equal(r[1],r2[1]);assert np.isfinite(r[0]).all()
        atomic(ROOT/'smoke_gate.json',dict(passed=True,elapsed=time.monotonic()-tick,performance_used_as_gate=False))
    front,state=search(a,ROOT)
    feasible=[z for z in front if z['m'][1]<.25]
    champions={'feasible_cagr':max(feasible,key=lambda z:z['m'][0]) if feasible else min(front,key=lambda z:z['m'][1]),'max_cagr':max(front,key=lambda z:z['m'][0]),'max_calmar':max(front,key=lambda z:z['m'][2])}
    atomic(ROOT/'champions.json',champions)
    atomic(ROOT/'freeze.json',dict(completed=state['completed'],stop=state['status'],champions_sha256=hashlib.sha256((ROOT/'champions.json').read_bytes()).hexdigest(),evaluation_started_after_freeze=True))
    metrics=[]
    universes=[('dev79',d)]
    transfer=ROOT.parent/'dev87_rsi_frozen_validation_20261101/dev87_raw.parquet'
    if transfer.exists():
        td=load(transfer)
        if set(td['names']) & set(d['names']):raise ValueError('DEV87 stock overlap: audit transfer before use')
        universes.append(('dev87',td))
    # Evaluate all frozen Pareto genomes after freeze, not only champions.
    for universe,data in universes:
        for split in ['train','evaluation']:
            for name,z in champions.items():metrics.append(evaluate(data,z['g'],universe+'_'+split,name,ROOT))
            for name,b in [('monthly_rsi_buy_hold',1),('cash',2)]:metrics.append(evaluate(data,np.zeros(SIZE),universe+'_'+split,name,ROOT,b))
            out=[];aa=arrays(data,'2009-01-01' if split=='train' else '2014-01-01','2013-12-31' if split=='train' else '2018-12-31')
            for z in front:out.append(dict(generation=z['generation'],candidate=z['candidate'],**metric(simulate(np.array(z['g']),*aa)[0])))
            pd.DataFrame(out).to_csv(ROOT/f'{universe}_{split}_frozen_frontier.csv',index=False)
    pd.DataFrame([{k:v for k,v in z.items() if k!='actions'} for z in metrics]).to_csv(ROOT/'metrics.csv',index=False);atomic(ROOT/'metrics.json',metrics)
    state['status']+='; frozen evaluation complete';state['total_invocation_seconds']=time.monotonic()-wall_started;report(ROOT,state,metrics)
    atomic(ROOT/'terminal.json',state)
    print('TERMINAL',state['status'],flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        (ROOT/'ERROR_AUDIT.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True);raise
