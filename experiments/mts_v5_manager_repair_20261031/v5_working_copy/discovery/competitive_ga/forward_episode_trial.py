"""Forward-only synthetic episodes; each episode resets positions and state."""
import json
from .multiregime_selection_trial import run as evolve
from .bounded_selection_ga_trial import evaluate
from .evolved_selection_policy import SelectionGenes

def run():
    fit=SelectionGenes(.15,1,0,0)
    ev=SelectionGenes(0,1,0,0)
    episodes=('mixed','trend','reversal')
    folds=[]
    for i in range(3):
        # Train on two worlds, evaluate third. Regime-heldout, not chronological.
        train=tuple(r for j,r in enumerate(episodes) if j!=i)
        result=evolve(seed=37+i,population=12,generations=5,training_regimes=train,heldout_regime=episodes[i])
        genes=SelectionGenes(**result['winner_genes'])
        test=episodes[i]
        scores={name:evaluate(g,test) for name,g in [('evolved',genes),('fit',fit),('ev',ev)]}
        folds.append({'test':test,'scores':scores,'trained_on':result['discovery_regimes']})
    return {'scope':'SYNTHETIC_REGIME_HOLDOUT','folds':folds}

if __name__=='__main__':print(json.dumps(run(),indent=2))
