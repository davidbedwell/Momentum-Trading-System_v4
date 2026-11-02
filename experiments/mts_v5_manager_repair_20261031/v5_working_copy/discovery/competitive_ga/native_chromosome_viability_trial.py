"""Bounded GA5/GA6 native chromosome grammar viability probe. Simplified funded accounting; NOT full manager parity."""
import json,random
from dataclasses import replace
from ga5_chromosome_contract import Genome,mutate,crossover
from ga5_redesign.fast_decision import evaluate
from ga5_chromosome_decisions import PositionState
from .bounded_selection_ga_trial import fixture

FEATURES=('momentum_5','momentum_20','volatility_20','relative_strength_20','breadth_20')
def new(r):
    f=lambda:r.choice(FEATURES)
    g=Genome('NICHE-0001',f(),r.uniform(-.12,.12),f(),r.uniform(-.3,.1),f(),r.uniform(-.3,.1),f(),r.uniform(-.12,.12),f(),.07,.1,f(),r.uniform(-.3,.1),r.uniform(.02,.12),r.uniform(.03,.16),r.randint(2,20),True,.1,r.uniform(.1,.8),r.uniform(-.8,-.1),.25)
    assert g.valid()
    return g

def score(g,regime):
    days=fixture(regime); prices={t:[row[t].close for _,row in days] for t in ('AAA','BBB','CCC')}
    cash=100000.;hold={};nav=[cash];fills=0
    for i,(d,_) in enumerate(days):
        # Execute yesterday's close decisions at today's open (fixture open == close).
        if i:
            for t,action,weight in orders:
                p=prices[t][i]
                if action=='EXIT' and t in hold:
                    q,entry,peak,session=hold.pop(t);cash+=q*p;fills+=1
                elif action=='ENTER' and t not in hold:
                    equity=cash+sum(q*prices[s][i] for s,(q,*_) in hold.items())
                    qty=min(cash,max(0,equity*min(.1,weight)))//p
                    if qty:cash-=qty*p;hold[t]=(qty,p,p,i);fills+=1
        for t,(q,entry,peak,session) in list(hold.items()):hold[t]=(q,entry,max(peak,prices[t][i]),session)
        nav.append(cash+sum(q*prices[t][i] for t,(q,*_) in hold.items()))
        orders=[]
        for t in prices:
            seq=prices[t][:i+1]
            m5=seq[-1]/seq[-6]-1 if len(seq)>5 else 0.
            m20=seq[-1]/seq[-21]-1 if len(seq)>20 else m5
            ret=[seq[k]/seq[k-1]-1 for k in range(max(1,len(seq)-20),len(seq))]
            vol=(sum((x-sum(ret)/len(ret))**2 for x in ret)/len(ret))**.5 if ret else 0.
            feat={'momentum_5':m5,'momentum_20':m20,'volatility_20':vol,'relative_strength_20':m20,'breadth_20':sum(prices[s][i]>prices[s][max(0,i-5)] for s in prices)/3-.5}
            state=PositionState(*(hold[t] if t in hold else (0,0.,0.,0)))
            if t in hold:state=PositionState(hold[t][0],hold[t][1],hold[t][2],i-hold[t][3])
            action,w=evaluate(g,feat,state,seq[-1])
            if action in ('ENTER','EXIT'):orders.append((t,action,w))
    peak=nav[0];dd=0.
    for x in nav:peak=max(peak,x);dd=max(dd,1-x/peak)
    ret=nav[-1]/nav[0]-1
    return {'return':ret,'mdd':dd,'fitness':ret-2*dd,'fills':fills}

def run(seed=41,population=24,generations=3):
    rng=random.Random(seed);pop=[new(rng) for _ in range(population)];history=[]
    for k in range(generations):
        ranked=sorted(((score(g,'mixed'),g) for g in pop),key=lambda x:x[0]['fitness'],reverse=True)
        history.append({'generation':k,'best':ranked[0][0],'median_fitness':sorted(x[0]['fitness'] for x in ranked)[len(ranked)//2],'unique_genomes':len(set(g.identity() for g in pop)),'best_id':ranked[0][1].identity()[:12]})
        if k+1<generations:
            parents=[g for _,g in ranked[:8]];next_pop=parents[:]
            while len(next_pop)<population:
                if rng.random()<.4:
                    try:g=crossover(*rng.sample(parents,2),rng)
                    except ValueError:g=mutate(rng.choice(parents),rng)
                else:g=mutate(rng.choice(parents),rng)
                for field in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature'):
                    if getattr(g,field) not in FEATURES:g=replace(g,**{field:rng.choice(FEATURES)})
                if g.valid():next_pop.append(g)
            pop=next_pop
    winner=ranked[0][1]
    return {'scope':'SYNTHETIC_NATIVE_GRAMMAR_VIABILITY_NOT_FULL_MANAGER','history':history,'winner_holdout_reversal':score(winner,'reversal'),'winner_holdout_trend':score(winner,'trend'),'winner_genome':winner.identity()}
if __name__=='__main__':print(json.dumps(run(),indent=2))
