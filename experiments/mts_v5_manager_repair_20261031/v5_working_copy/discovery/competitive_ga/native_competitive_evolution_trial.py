"""Bounded 24x3 synthetic shared-bank native chromosome experiment; not market certification."""
import json,random
from dataclasses import replace,asdict
from ga5_chromosome_contract import mutate,crossover
from ga5_redesign.fast_decision import evaluate
from ga5_chromosome_decisions import PositionState
from .native_chromosome_viability_trial import new,FEATURES
from .causal_niche_classifier import classify_closes
from .functional_niche_manager import Candidate,run_slice
from .native_signal_contract import NativeProposal
from .genome_identity import GenomeIdentityRegistry
from .bounded_selection_ga_trial import fixture
from .evolved_selection_policy import SelectionGenes

TICKERS=('AAA','BBB','CCC')
def portfolio(genomes,regime='mixed',genes=None):
    days=fixture(regime);idx={d:i for i,(d,_) in enumerate(days)}
    prices={t:[row[t].close for _,row in days] for t in TICKERS}
    candidates=[Candidate(str(k),'GA6','A' if k%2==0 else 'B',.02) for k in range(len(genomes))]
    mapped={(c.family,c.chromosome_id):asdict(g) for c,g in zip(candidates,genomes)}
    registry=GenomeIdentityRegistry()
    for (f,c),g in mapped.items():registry.register(f,c,g)
    def classify(t,d):
        i=idx[d];return classify_closes(prices[t][:i+1],i,d)
    def native(c,t,d,held):
        i=idx[d];g=genomes[int(c.chromosome_id)];seq=prices[t][:i+1]
        m5=seq[-1]/seq[-6]-1 if i>=5 else 0.
        m20=seq[-1]/seq[-21]-1 if i>=20 else m5
        rr=[seq[k]/seq[k-1]-1 for k in range(max(1,len(seq)-20),len(seq))]
        mean=sum(rr)/len(rr) if rr else 0.
        vol=(sum((x-mean)**2 for x in rr)/len(rr))**.5 if rr else 0.
        feat={'momentum_5':m5,'momentum_20':m20,'volatility_20':vol,'relative_strength_20':m20,
              'breadth_20':sum(prices[s][i]>prices[s][max(0,i-5)] for s in TICKERS)/3-.5}
        state=PositionState(int(held.get('shares',1)),held.get('entry',held.get('entry_price',seq[-1])),held.get('peak',seq[-1]),i-held['entry_session']) if held else PositionState()
        action,w=evaluate(g,feat,state,seq[-1])
        if action=='NO_ENTRY':return None
        if held and action=='ENTER':action,w='HOLD',held['weight']
        if action=='REPLACE_CANDIDATE':action,w='EXIT',0.
        if action=='SCALE_IN':action,w='ADD',min(.1,held['weight']+min(.03,w))
        elif action=='SCALE_OUT':action,w='REDUCE',held['weight']*(1-w)
        elif action=='HOLD':w=held['weight']
        return NativeProposal(d,t,'GA6',c.chromosome_id,action,min(.1,max(0.,w)),.01,'entry_equity_fraction','synthetic','synthetic','2025-12-31')
    result=run_slice(days,candidates,classify=classify,eligible=lambda *a:True,native=native,
                     conditional_ev=lambda c,*a:.02,native_genomes=mapped,genome_registry=registry,
                     require_genome_identity=True,max_sessions=160,native_shadow=True,selection_genes=genes)
    nav=[100000.]+[row[1] for row in result['nav']];peak=nav[0];dd=0.
    for v in nav:peak=max(peak,v);dd=max(dd,1-v/peak)
    growth=nav[-1]/nav[0]-1
    return {'return':growth,'mdd':dd,'fitness':growth-2*dd,'fills':len(result['ledger'])}

def run(seed=41,population=24,generations=3):
    rng=random.Random(seed);pop=[new(rng) for _ in range(population)];history=[]
    genes=SelectionGenes(.02,1.,.5,0.)
    def mutate_genes(g):
        return SelectionGenes(max(0,g.fit_bonus+rng.gauss(0,.015)),max(0,g.ev_weight+rng.gauss(0,.25)),max(0,g.uncertainty_weight+rng.gauss(0,.2)),max(0,g.min_edge+rng.gauss(0,.003)),g.momentum_fit_weight+rng.gauss(0,.15),g.volatility_fit_weight+rng.gauss(0,.15))
    for gen in range(generations):
        metric=portfolio(pop,genes=genes)
        history.append({'generation':gen,'portfolio':metric,'unique_genomes':len({g.identity() for g in pop})})
        if gen+1==generations:break
        # Compete complete 24-member libraries through funded portfolio replay.
        # Never remove/reindex a member: niche ownership is index-qualified.
        accepted=0;attempts=24
        for _ in range(attempts):
            slot=rng.randrange(population)
            parent=pop[slot]
            if rng.random()<.35:
                other=rng.choice(pop)
                try:child=crossover(parent,other,rng)
                except ValueError:child=mutate(parent,rng)
            else:child=mutate(parent,rng)
            for field in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature'):
                if getattr(child,field) not in FEATURES:child=replace(child,**{field:rng.choice(FEATURES)})
            if not child.valid() or child.identity() in {g.identity() for g in pop}:continue
            challenger=pop[:];challenger[slot]=child
            trial=portfolio(challenger,genes=genes)
            if trial['fitness']>metric['fitness']+1e-10:
                pop=challenger;metric=trial;accepted+=1
        for _ in range(8):
            candidate_genes=mutate_genes(genes)
            trial=portfolio(pop,genes=candidate_genes)
            if trial['fitness']>metric['fitness']+1e-10:
                genes=candidate_genes;metric=trial;accepted+=1
        history[-1]['manager_genes']=asdict(genes)
        history[-1]['accepted_portfolio_improvements']=accepted
        history[-1]['post_selection_portfolio']=metric
    return {'scope':'SYNTHETIC_SHARED_BANK_NATIVE_GRAMMAR','history':history,'manager_genes':asdict(genes),'holdout_reversal':portfolio(pop,'reversal',genes),'holdout_trend':portfolio(pop,'trend',genes)}
if __name__=='__main__':print(json.dumps(run(),indent=2))
