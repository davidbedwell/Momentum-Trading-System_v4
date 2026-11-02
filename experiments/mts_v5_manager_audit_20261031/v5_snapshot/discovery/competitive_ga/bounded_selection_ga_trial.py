"""Bounded deterministic evolutionary FUNCTIONAL trial, not market validation."""
import json,random
from datetime import date,timedelta
from .evolved_selection_policy import SelectionGenes
from .functional_niche_manager import Candidate,NicheObservation,run_slice
from .native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

SEED=37

def fixture(regime='mixed'):
    days=[]
    start=date(2026,1,2)
    for i in range(32):
        d=(start+timedelta(days=i)).isoformat()
        # Distinct synthetic paths, including a sharp reversal.
        paths={'AAA':100+1.2*i-(18 if i>=17 else 0),
               'BBB':100+.4*i+(9 if i>=12 else 0)-(12 if i>=24 else 0),
               'CCC':100-.25*i+(14 if i>=19 else 0)}
        if regime=='trend':
            paths={'AAA':100+1.3*i,'BBB':100+.8*i,'CCC':100+.4*i}
        elif regime=='reversal':
            paths={'AAA':100+1.4*min(i,15)-1.8*max(0,i-15),
                   'BBB':100-.9*min(i,12)+1.6*max(0,i-12),
                   'CCC':100+(.9 if i%2 else -.9)*i/3}
        elif regime!='mixed':raise ValueError('unknown synthetic regime')
        days.append((d,{t:Bar(v,v) for t,v in paths.items()}))
    return days

def evaluate(genes,regime='mixed'):
    days=fixture(regime); idx={d:i for i,(d,_) in enumerate(days)}
    candidates=[Candidate('specialist','GA6','A',.02),Candidate('transfer','GA7',None,.02)]
    def classify(t,d):return NicheObservation(d,'2026-01-01','synthetic',(('A',.2),))
    def native(c,t,d,held):
        age=idx[d]-held['entry_session'] if held else 0
        action='EXIT' if held and age>=(2 if c.family=='GA6' else 5) else 'HOLD' if held else 'ENTER'
        return NativeProposal(d,t,c.family,c.chromosome_id,action,0 if action=='EXIT' else .1,
            .01,'entry_equity_fraction' if c.family=='GA6' else 'net_return_fraction',
            'fixture','fixture','2026-01-01')
    result=run_slice(days,candidates,classify=classify,eligible=lambda *a:True,native=native,
        conditional_ev=lambda c,*a:.025 if c.family=='GA6' else .07,
        selection_genes=genes,native_shadow=True,max_sessions=40)
    nav=[row[1] for row in result['nav']]
    peak=nav[0];dd=0.
    for v in nav:
        peak=max(peak,v);dd=max(dd,1-v/peak)
    net=nav[-1]/nav[0]-1
    # Portfolio return and drawdown, never per-chromosome fitness.
    fitness=net-2*dd
    return {'fitness':fitness,'net_return':net,'max_drawdown':dd,'ending_nav':nav[-1],
            'fills':len(result['ledger']),'shadow_outcomes':len(result['native_shadow_outcomes'])}

def run(seed=SEED,population=12,generations=3):
    rng=random.Random(seed)
    def random_genes():return SelectionGenes(rng.uniform(0,.15),rng.uniform(.2,3),rng.uniform(0,2),rng.uniform(0,.04))
    pop=[SelectionGenes(.15,1,0,0),SelectionGenes(0,1,0,0)]
    pop.extend(random_genes() for _ in range(population-len(pop)))
    history=[];best=None
    for generation in range(generations):
        scored=sorted([(evaluate(g),g) for g in pop],key=lambda pair:pair[0]['fitness'],reverse=True)
        if best is None or scored[0][0]['fitness']>best[0]['fitness']:best=scored[0]
        history.append({'generation':generation,'best_fitness':scored[0][0]['fitness'],
                        'best_return':scored[0][0]['net_return'],'best_mdd':scored[0][0]['max_drawdown']})
        parents=[g for _,g in scored[:max(2,population//3)]]
        pop=parents[:]
        while len(pop)<population:
            p=rng.choice(parents)
            pop.append(SelectionGenes(max(0,p.fit_bonus+rng.gauss(0,.025)),
                max(0,p.ev_weight+rng.gauss(0,.4)),max(0,p.uncertainty_weight+rng.gauss(0,.3)),
                max(0,p.min_edge+rng.gauss(0,.008))))
    return {'scope':'SYNTHETIC_FUNCTIONAL_ONLY','seed':seed,'population':population,
            'generations':generations,'history':history,'best_genes':best[1].__dict__,
            'best_metrics':best[0],'baseline_fit_first':evaluate(SelectionGenes(.15,1,0,0)),
            'baseline_ev_first':evaluate(SelectionGenes(0,1,0,0))}

if __name__=='__main__':print(json.dumps(run(),indent=2))
