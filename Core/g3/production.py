from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import hashlib, json, math, pickle, random
import numpy as np

FORBIDDEN_GENES={"ticker","ticker_id","company","company_id","calendar_year","portfolio_cagr","portfolio_mdd","slot_count","safe_fraction","sector_weight"}
THRESHOLDS=(-1.5,-1.0,-.5,0.0,.5,1.0,1.5)

@dataclass(frozen=True)
class Predicate:
    feature:int; threshold:float; direction:int
    def fires(self,X):
        z=X[:,self.feature]; return z>=self.threshold if self.direction>0 else z<=self.threshold

@dataclass(frozen=True)
class Module:
    applicability:tuple[Predicate,...]
    signal_features:tuple[int,...]
    signal_weights:tuple[float,...]
    side:int                 # -1 short, +1 long, 0 conditional from signal sign
    entry_threshold:float
    persistence:int
    take_profit:float
    stop_loss:float
    max_horizon:int
    add_at:float
    reduce_at:float
    trail_retain:float
    abandon_feature:int|None
    abandon_threshold:float
    abandon_direction:int

@dataclass(frozen=True)
class Genome:
    modules:tuple[Module,...]
    abstain_threshold:float

@dataclass
class Event:
    ticker:str; t:int; module:int; side:int; net_return:float; mfe:float; mae:float
    duration:int; turnover:float; costs:float; actions:tuple[str,...]; path:tuple[float,...]

@dataclass
class Evidence:
    events:list[Event]; mean:float; tail5:float; mean_mae:float; duration:float; n:int; clusters:int

def stable_seed(*parts)->int:
    return int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8],'little')

def genome_key(g:Genome)->str:
    return hashlib.sha256(json.dumps(asdict(g),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def validate_genome(g:Genome,n_features:int)->None:
    if not 2<=len(g.modules)<=8: raise ValueError('module count')
    if not 0<=g.abstain_threshold<=4: raise ValueError('abstain')
    for m in g.modules:
        if not 1<=len(m.applicability)<=4 or not 1<=len(m.signal_features)<=6: raise ValueError('grammar')
        if len(m.signal_features)!=len(m.signal_weights): raise ValueError('weights')
        ids=[p.feature for p in m.applicability]+list(m.signal_features)+([] if m.abandon_feature is None else [m.abandon_feature])
        if any(i<0 or i>=n_features for i in ids): raise ValueError('feature')
        if m.side not in (-1,0,1) or not 1<=m.persistence<=5 or not 2<=m.max_horizon<=60: raise ValueError('lifecycle')

def random_pred(r,nf): return Predicate(r.randrange(nf),r.choice(THRESHOLDS),r.choice((-1,1)))
def random_module(r,nf):
    ns=r.randint(1,min(6,nf)); return Module(
      tuple(random_pred(r,nf) for _ in range(r.randint(1,4))),
      tuple(r.randrange(nf) for _ in range(ns)),tuple(r.uniform(-2,2) for _ in range(ns)),r.choice((-1,0,1)),
      r.uniform(.1,2.0),r.randint(1,5),r.uniform(.01,.20),r.uniform(.005,.12),r.randint(2,60),
      r.uniform(.005,.08),r.uniform(.005,.10),r.uniform(0,.8),
      (r.randrange(nf) if r.random()<.5 else None),r.choice(THRESHOLDS),r.choice((-1,1)))
def random_genome(seed,nf):
    r=random.Random(seed); return Genome(tuple(random_module(r,nf) for _ in range(r.randint(2,8))),r.uniform(.1,2.5))

def mutate(g:Genome,seed:int,nf:int)->Genome:
    r=random.Random(seed); mods=list(g.modules); k=r.randrange(8)
    if k==0 and len(mods)<8: mods.append(random_module(r,nf))
    elif k==1 and len(mods)>2: mods.pop(r.randrange(len(mods)))
    else:
        j=r.randrange(len(mods)); m=mods[j]
        if k==2: m=replace(m,entry_threshold=max(.05,min(3,m.entry_threshold+r.gauss(0,.15))))
        elif k==3: m=replace(m,take_profit=max(.01,min(.20,m.take_profit+r.gauss(0,.01))))
        elif k==4: m=replace(m,stop_loss=max(.005,min(.12,m.stop_loss+r.gauss(0,.008))))
        elif k==5: m=replace(m,max_horizon=max(2,min(60,m.max_horizon+r.choice((-5,-2,2,5)))))
        elif k==6:
            w=list(m.signal_weights); q=r.randrange(len(w)); w[q]=max(-4,min(4,w[q]+r.gauss(0,.3))); m=replace(m,signal_weights=tuple(w))
        else:
            a=list(m.applicability); q=r.randrange(len(a)); a[q]=random_pred(r,nf); m=replace(m,applicability=tuple(a))
        mods[j]=m
    return Genome(tuple(mods),max(0,min(4,g.abstain_threshold+r.gauss(0,.1))))

def crossover(a:Genome,b:Genome,seed:int)->Genome:
    r=random.Random(seed); pool=list(a.modules)+list(b.modules); r.shuffle(pool); n=r.randint(2,min(8,len(pool)))
    return Genome(tuple(pool[:n]),(a.abstain_threshold+b.abstain_threshold)/2)

def _runs(mask,persistence):
    if persistence<=1:return mask
    x=mask.astype(np.int16); c=np.convolve(x,np.ones(persistence,dtype=np.int16),'full')[:len(x)]
    return c>=persistence

def evaluate_genome(g:Genome,data:dict[str,tuple[np.ndarray,np.ndarray]],cost_bps=10.0)->Evidence:
    events=[]; cost=cost_bps/10000
    for ticker,(X,Y) in data.items():
        validate_genome(g,X.shape[1])
        for mi,m in enumerate(g.modules):
            app=np.ones(len(X),bool)
            for p in m.applicability: app &= p.fires(X)
            score=sum(w*X[:,f] for f,w in zip(m.signal_features,m.signal_weights))
            fire=_runs(app & (np.abs(score)>=max(g.abstain_threshold,m.entry_threshold)),m.persistence)
            for t in np.flatnonzero(fire):
                side=m.side if m.side else (1 if score[t]>=0 else -1)
                path=np.asarray(Y[t,:min(m.max_horizon,Y.shape[1])],float)*side
                wealth=1.; peak=0.; trough=0.; exposure=1.; turn=1.; actions=['enter']; highwater=0.
                for j,rtn in enumerate(path,1):
                    wealth*=1+exposure*rtn; pnl=wealth-1; peak=max(peak,pnl); trough=min(trough,pnl); highwater=max(highwater,pnl)
                    if pnl<=-m.add_at and exposure<1.5: exposure=1.5;turn+=.5;actions.append('add')
                    if pnl>=m.reduce_at and exposure>0.5: turn+=abs(exposure-.5);exposure=.5;actions.append('reduce')
                    abandon=False
                    if m.abandon_feature is not None:
                        z=X[t,m.abandon_feature]; abandon=(z>=m.abandon_threshold if m.abandon_direction>0 else z<=m.abandon_threshold)
                    trail=(highwater>0 and pnl < highwater*m.trail_retain)
                    if pnl>=m.take_profit or pnl<=-m.stop_loss or abandon or trail: actions.append('exit'); break
                    actions.append('hold')
                if actions[-1] != 'exit': actions.append('exit')
                turn+=exposure; net=(wealth-1)-turn*cost
                events.append(Event(ticker,int(t),mi,side,float(net),float(peak),float(trough),j,float(turn),float(turn*cost),tuple(actions),tuple(map(float,path[:j]))))
    if not events:return Evidence([], -1e9,-1e9,1e9,1e9,0,0)
    r=np.array([e.net_return for e in events]); mae=np.array([e.mae for e in events]); dur=np.array([e.duration for e in events])
    clusters=cluster_count(events)
    return Evidence(events,float(r.mean()),float(np.quantile(r,.05)),float(mae.mean()),float(dur.mean()),len(events),clusters)

def event_clusters(events:list[Event])->list[list[Event]]:
    # Conservative dependence rule: any time-overlapping holdings across any design-panel stocks
    # are one transitive market-exposure cluster. This intentionally understates ESS.
    if not events:return []
    xs=sorted(events,key=lambda e:(e.t,e.t+e.duration,e.ticker)); groups=[];cur=[];end=-1
    for ev in xs:
        stop=ev.t+ev.duration
        if cur and ev.t>end:
            groups.append(cur);cur=[];end=-1
        cur.append(ev);end=max(end,stop)
    if cur:groups.append(cur)
    return groups

def cluster_count(events:list[Event])->int:return len(event_clusters(events))

def bootstrap_axes(ev:Evidence,seed:int,resamples=2000):
    if ev.n==0:return (-1e9,1e9,1e9)
    groups=event_clusters(ev.events)
    if not groups:return (-1e9,1e9,1e9)
    stats=[]
    for g in groups:
        stats.append((np.mean([e.net_return for e in g]),np.mean([-e.mae for e in g]),np.mean([e.duration for e in g])))
    a=np.asarray(stats,float);rng=np.random.default_rng(seed);k=len(a);ix=rng.integers(0,k,size=(resamples,k));z=a[ix].mean(1)
    return float(np.quantile(z[:,0],.10)),float(np.quantile(z[:,1],.90)),float(np.quantile(z[:,2],.90))

def dominates(a,b):
    return a[0]>=b[0] and a[1]<=b[1] and a[2]<=b[2] and (a[0]>b[0] or a[1]<b[1] or a[2]<b[2])

def descriptor(ev:Evidence):
    if not ev.events:return np.zeros(12)
    E=ev.events; r=np.array([e.net_return for e in E]); dur=np.array([e.duration for e in E]); mfe=np.array([e.mfe for e in E]); mae=np.maximum(1e-9,-np.array([e.mae for e in E]));
    tick=len(set(e.ticker for e in E)); short=np.mean([e.side<0 for e in E]); adds=np.mean([e.actions.count('add') for e in E]); reds=np.mean([e.actions.count('reduce') for e in E]);
    return np.array([math.log1p(len(E)),tick,short,np.median(dur),np.median(mfe/mae),np.mean(r),np.std(r),np.quantile(r,.1),np.quantile(r,.9),adds,reds,ev.clusters],float)

def promotion(ev10:Evidence,ev20:Evidence,axes,perturb_positive_fraction:float,explicit_narrow_scope=False):
    if ev10.n<50 or ev10.clusters<25:return False
    if axes[0]<=0 or ev20.mean<=0 or perturb_positive_fraction<.75:return False
    pnl={}
    for e in ev10.events:pnl[e.ticker]=pnl.get(e.ticker,0)+max(0,e.net_return)
    total=sum(pnl.values())
    if total>0 and max(pnl.values())/total>.5 and not explicit_narrow_scope:return False
    return True

def save_checkpoint(path:Path,state)->str:
    b=pickle.dumps(state,protocol=5); path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b);return hashlib.sha256(b).hexdigest()
def load_checkpoint(path:Path):return pickle.loads(path.read_bytes())

def genome_from_dict(d:dict)->Genome:
    mods=[]
    for x in d['modules']:
        apps=tuple(Predicate(**p) for p in x['applicability'])
        y=dict(x);y['applicability']=apps;y['signal_features']=tuple(y['signal_features']);y['signal_weights']=tuple(y['signal_weights']);mods.append(Module(**y))
    return Genome(tuple(mods),d['abstain_threshold'])
