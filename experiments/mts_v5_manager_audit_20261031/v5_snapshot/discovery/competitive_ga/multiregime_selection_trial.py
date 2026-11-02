"""Three synthetic worlds: discover on mixed/trend, evaluate reversal unseen."""
import json,random
from .bounded_selection_ga_trial import evaluate
from .evolved_selection_policy import SelectionGenes

def run(seed=37,population=12,generations=5,training_regimes=('mixed','trend'),heldout_regime='reversal'):
    rng=random.Random(seed)
    fit=SelectionGenes(.15,1,0,0)
    ev=SelectionGenes(0,1,0,0)
    def random_genes():return SelectionGenes(rng.uniform(0,.2),rng.uniform(.2,3),rng.uniform(0,2),rng.uniform(0,.04),rng.uniform(-3,3),rng.uniform(-3,3))
    def training(g):
        metrics=[evaluate(g,regime) for regime in training_regimes]
        return sum(m['fitness'] for m in metrics)/len(metrics)
    population_genes=[fit,ev]+[random_genes() for _ in range(population-2)]
    history=[]
    for gen in range(generations):
        ranked=sorted(((training(g),g) for g in population_genes),key=lambda x:x[0],reverse=True)
        history.append({'generation':gen,'best_training_fitness':ranked[0][0]})
        parents=[g for _,g in ranked[:max(2,population//3)]]
        population_genes=parents[:]
        while len(population_genes)<population:
            p=rng.choice(parents)
            population_genes.append(SelectionGenes(max(0,p.fit_bonus+rng.gauss(0,.03)),
                max(0,p.ev_weight+rng.gauss(0,.4)),max(0,p.uncertainty_weight+rng.gauss(0,.3)),
                max(0,p.min_edge+rng.gauss(0,.008)),
                p.momentum_fit_weight+rng.gauss(0,.8),
                p.volatility_fit_weight+rng.gauss(0,.8)))
    ranked=sorted(((training(g),g) for g in population_genes),key=lambda x:x[0],reverse=True)
    winner=ranked[0][1]
    return {'scope':'SYNTHETIC_FUNCTIONAL_NOT_OOS_MARKET_CERTIFICATION',
            'seed':seed,'population':population,'generations':generations,
            'discovery_regimes':list(training_regimes),'heldout_regime':heldout_regime,
            'history':history,'winner_genes':winner.__dict__,
            'discovery_fitness':ranked[0][0],
            'heldout':{'evolved':evaluate(winner,heldout_regime),
                       'niche_first':evaluate(fit,heldout_regime),
                       'ev_first':evaluate(ev,heldout_regime)}}

if __name__=='__main__':print(json.dumps(run(),indent=2))
