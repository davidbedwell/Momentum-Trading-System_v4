"""Exploratory native-library evolution; never production/PIT certification.

Evolution breeds native chromosome descendants and jointly recombines chromosome
allocation alleles and manager risk/uncertainty alleles. Source definitions remain
unchanged; every descendant gets its own identity and shadow learning history.
"""
import argparse
import json
import math
import time
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import pandas as pd
from .native_ga7_integration_gate import diagnostic, library

OUT=Path('/opt/mts/ga7-deploy/experiments/exploratory_ga7_500')

class Policy:
    def __init__(self, records, evolved=True, seed=7007):
        self.evolved=evolved
        self.keys=sorted((f,c) for f,c,_,_ in records)
        # Explicit hypothesis, not authenticated equivalence or changed genomes.
        self.mapping={f'NICHE-{i:04d}':f'PIT-NICHE-{i:04d}' for i in range(1,14)}
        self.stats=defaultdict(lambda:np.zeros(3))
        self.context=defaultdict(lambda:np.zeros(3))
        self.queue=[];self.session=-1;self.events=[];self.learned_choices=0
        self.rng=np.random.default_rng(seed)
        self.weights=np.ones(len(self.keys));self.penalty=.5;self.cap=1.
        self.counts=Counter();self.max_maturity=-1;self.birth_cutoffs={};self.last_date=None

    def bind(self,genomes,candidates,register):
        self.genomes=genomes;self.candidates=candidates;self.register=register
        self.initial_count=len(self.keys);self.lineage=[]

    def breed(self,session):
        import copy
        from dataclasses import replace
        from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
        for family in ('GA6','GA7'):
            parents=sorted([k for k in self.keys if k[0]==family],
                key=lambda k:((self.estimate(k) or (-1.,0.))[0],k),reverse=True)
            for parent in parents[:2]:
                original=self.genomes[parent];child=copy.deepcopy(original)
                niche=next(c.niche for c in self.candidates if (c.family,c.chromosome_id)==parent)
                # Same-niche crossover preserves specialized niche semantics.
                mate=next((k for k in parents if k!=parent and next(c.niche for c in self.candidates if (c.family,c.chromosome_id)==k)==niche),parent)
                other=self.genomes[mate]
                if family=='GA6':
                    obj=StructuralCandidate.restore(original)
                    changes={f:float(np.clip((original['genome'][f]+other['genome'][f])/2+self.rng.normal(0,.08),-1,1)) for f in ('hold_threshold','exit_threshold','scale_in_threshold','scale_out_threshold')}
                    child=StructuralCandidate(replace(obj.genome,**changes),obj.entry_tree).checkpoint()
                else:
                    for f in ('threshold_a','threshold_b'):
                        child[f]=float(np.clip((original[f]+other[f])/2+self.rng.normal(0,.08),-1,1))
                    child['entry_pct']=float(np.clip((original['entry_pct']+other['entry_pct'])/2+self.rng.normal(0,.005),.005,.1))
                key=self.register(family,child,niche)
                if key not in self.keys:
                    self.keys.append(key);self.weights=np.r_[self.weights,1.]
                    self.birth_cutoffs[key]=self.last_date
                    self.lineage.append({'born_session':session,'family':family,'id':key[1],'parents':[parent[1],mate[1]],'definition':child,'niche':niche})

    def on_session(self, session, date, matured):
        self.session=session
        # Outcomes executed today cannot enter today's learner.
        for o in self.queue:
            assert o.maturity_session<session
            key=(o.family,o.chromosome_id)
            for stats in (self.stats[key],self.context[(key,o.context[0])]):
                stats += (1,o.net_r,o.net_r**2)
            self.max_maturity=max(self.max_maturity,o.maturity_session)
            self.counts[o.family]+=1
        self.queue=list(matured)
        if self.evolved and session in (252,504,756,1008):
            self.evolve(session,date)
        self.last_date=date
        if session%252==0:
            print(json.dumps({'session':session,'date':date,'matured':sum(self.counts.values()),'evolved':self.evolved}),flush=True)

    def estimate(self,key):
        n,s,q=self.stats[key]
        if n<5:return None
        mean=s/n;se=math.sqrt(max(0,q/n-mean*mean)/n)
        return mean,se

    def evolve(self,session,date):
        # Fitness uses only strict-past matured after-cost native shadow returns.
        # Proxy utility is disclosed: this is not candidate funded replay fitness.
        means=np.array([self.estimate(k) or (0.,0.) for k in self.keys])
        population=[(self.weights.copy(),self.penalty,self.cap)]
        population += [(self.rng.uniform(.1,2,len(self.keys)),float(self.rng.choice([0,.5,1,2])),float(self.rng.choice([.25,.5,.75,1]))) for _ in range(31)]
        def fitness(g):
            w,p,c=g; edge=means[:,0]-p*means[:,1]
            active=w*(edge>0)
            return float(c*np.dot(active,edge)/max(active.sum(),1e-12)-.00005*c*c)
        for _ in range(6):
            elite=sorted(population,key=fitness,reverse=True)[:8]
            population=elite.copy()
            while len(population)<32:
                a,b=[elite[i] for i in self.rng.integers(0,8,2)]
                w=np.where(self.rng.random(len(self.keys))<.5,a[0],b[0])
                w=np.clip(w+self.rng.normal(0,.2,len(w)),.05,3)
                population.append((w,max(0,a[1]+float(self.rng.normal(0,.2))),float(np.clip(b[2]+self.rng.normal(0,.1),.1,1))))
        best=max(population,key=fitness);self.weights,self.penalty,self.cap=best
        event={'session':session,'date':date,'training_maturity_max':self.max_maturity,'strict_past_samples':sum(self.counts.values()),'fitness':fitness(best),'penalty':self.penalty,'size_multiplier':self.cap,'chromosome_allocation':self.weights.tolist(),'population':32,'generations':6,'fitness_kind':'matured_shadow_proxy_NOT_candidate_funded_replay'}
        if hasattr(self,'register'):
            self.breed(session)
            event['descendants']=[r for r in self.lineage if r['born_session']==session]
        self.events.append(event)
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/f'checkpoint_{id(self)}_{session}.json').write_text(json.dumps(event,indent=2))

    def select(self,items,ticker,date,session,remaining):
        if not self.evolved:
            from .synthetic_entry_competition import choose
            return choose([(key,p.target_weight) for key,(_,p) in items],ticker,session)
        ranked=[]
        for token,(c,p) in items:
            key=(c.family,c.chromosome_id);estimate=self.estimate(key)
            if estimate is None:
                # Explicit cold start rotation, no invented edge.
                continue
            mean,se=estimate
            value=(mean-self.penalty*se)*self.weights[self.keys.index(key)]
            if value>0:ranked.append((value,token,p))
        if ranked:
            _,token,p=max(ranked,key=lambda x:(x[0],x[1]));self.learned_choices+=1
            # selector returns identity; size applied by native wrapper separately.
            return token,p.target_weight
        if session<40:
            from .synthetic_entry_competition import choose
            return choose([(key,p.target_weight) for key,(_,p) in items],ticker,session)
        return None

    def finish(self,result,days,elapsed,scenario):
        nav=np.array([row[1] for row in result['nav']]); benchmark=np.array([np.mean([b.close/days[0][1][t].close for t,b in bars.items()]) for _,bars in days])
        market=pd.read_parquet(Path('/opt/mts/synthetic-market-lab/runs/five_iteration_inputs')/f'universe_{scenario}'/'market_index.parquet').sort_values('Date')['Close'].to_numpy()[:len(days)]
        if len(market)!=len(days):raise ValueError('benchmark calendar mismatch')
        market=market/market[0]
        def metrics(a,base):
            path=np.r_[base,a];ratio=path/base
            return {'return_pct':float((a[-1]/base-1)*100),'cagr_pct':float(((a[-1]/base)**(252/len(a))-1)*100),'mdd_pct':float((1-path/np.maximum.accumulate(path)).max()*100)}
        annual=[]
        for y in range(5):
            lo=y*252;hi=min(lo+252,len(nav))
            if hi<=lo:break
            matured=[o.net_r for o in result['native_shadow_outcomes'] if lo<=o.maturity_session<hi]
            annual.append({'matured_shadow_trades':len(matured),'matured_shadow_net_ev':float(np.mean(matured)) if matured else None,'year':y+1,'synthetic_market_index':metrics(market[lo:hi],market[lo-1] if lo else 1),'portfolio':metrics(nav[lo:hi],nav[lo-1] if lo else 100000),'equal_weight_500_buy_hold':metrics(benchmark[lo:hi],benchmark[lo-1] if lo else 1)})
        summary={'status':'EXPLORATORY_NOT_PRODUCTION_CERTIFIED','scenario':scenario,'arm':'evolved' if self.evolved else 'frozen','sessions':len(days),'stocks':500,'initial_native_chromosomes':getattr(self,'initial_count',len(self.keys)),'native_chromosomes_including_descendants':len(self.keys),'wall_seconds':elapsed,'synthetic_market_index':metrics(market,1),'portfolio':metrics(nav,100000),'equal_weight_500_buy_hold':metrics(benchmark,1),'final_nav':float(nav[-1]),'annual':annual,'fills':len(result['ledger']),'matured_shadows':dict(Counter(o.family for o in result['native_shadow_outcomes'])),'matured_shadow_net_ev':float(np.mean([o.net_r for o in result['native_shadow_outcomes']])) if result['native_shadow_outcomes'] else None,'native_actions':getattr(self,'native_actions',{}),'learned_choices':self.learned_choices,'annual_joint_evolution':self.events,'limitations':['Suffix mapping is an exploratory hypothesis, not authenticated niche identity.','Source feature/model PIT and native value parity remain unverified.','Joint evolution breeds native trading genes and manager sizing/uncertainty; source genomes stay unchanged and descendants have separate identities.','Evolution uses matured shadow proxy fitness, not funded candidate replay.','Benchmarks are the generator synthetic market index and equal-weight 500-stock buy-and-hold; neither is real SPY. Cash earns zero; no SGOV yield is simulated.','Synthetic order calendar is rebased; final year is forward evaluation after last checkpoint, not certification.']}
        # Realized owner identities and still-held owners prove funded family coverage.
        summary['mean_cash_exposure_pct']=float(np.mean([r[2]/r[1] for r in result['nav']])*100)
        summary['funded_realized_pnl_by_family']={f:sum(x['pnl'] for x in result['realized'] if x['owner'][0]==f) for f in ('GA6','GA7')}
        summary['funded_families']=sorted({x['owner'][0] for x in result['realized']}|{x[0] for x in result['owners'].values()})
        OUT.mkdir(parents=True,exist_ok=True);stem=f'scenario_{scenario}_{summary["arm"]}'
        (OUT/f'{stem}.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
        (OUT/f'{stem}_learning.json').write_text(json.dumps({'asof_session':self.session,'maturity_max':self.max_maturity,'strict_past_samples':sum(self.counts.values()),'chromosomes':[{'family':k[0],'id':k[1],'samples':int(v[0]),'sum_net_r':float(v[1]),'sum_squared_net_r':float(v[2]),'born_training_cutoff':self.birth_cutoffs.get(k,'2026-10-28')} for k,v in self.stats.items()]},indent=2))
        (OUT/f'{stem}_nav.json').write_text(json.dumps(result['nav']))
        (OUT/f'{stem}_fills.json').write_text(json.dumps(result['ledger']))
        print(json.dumps({k:v for k,v in summary.items() if k not in ('annual_joint_evolution','limitations')},indent=2),flush=True)
        return summary

def main():
    p=argparse.ArgumentParser();p.add_argument('--force',action='store_true');p.add_argument('--scenario',type=int,default=1);p.add_argument('--sessions',type=int,default=1260);p.add_argument('--arm',choices=['frozen','evolved'],default='evolved');a=p.parse_args()
    import fcntl
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/f'scenario_{a.scenario}_{a.arm}.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        target=OUT/f'scenario_{a.scenario}_{a.arm}.json'
        if not a.force and a.sessions==1260 and target.exists():
            previous=json.loads(target.read_text())
            expected=70 if a.arm=='evolved' else 54
            if (previous.get('sessions')==1260 and previous.get('native_chromosomes_including_descendants')==expected
                and previous.get('native_actions') and (OUT/f'scenario_{a.scenario}_{a.arm}_learning.json').exists()):
                print(json.dumps({'reused_completed_arm':a.arm,'scenario':a.scenario}),flush=True)
                return
        records=library();policy=Policy(records,a.arm=='evolved',7007+a.scenario)
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'exploratory_mapping.json').write_text(json.dumps({'status':'EXPLORATORY_HYPOTHESIS_NOT_IDENTITY_CERTIFICATION','mapping':policy.mapping,'method':'ordinal suffix hypothesis; no authenticated bridge; native definitions unchanged','library':[{'family':f,'id':c,'source_niche':n,'definition':d} for f,c,n,d in records]},indent=2))
        diagnostic(records,a.scenario,0,a.sessions,exploratory=policy)

if __name__=='__main__':main()
