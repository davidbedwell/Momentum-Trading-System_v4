"""Small predeclared scenario-order holdout; independent 64-session episodes.
This is NOT a continuous longitudinal portfolio or proof of OOS market transfer.
"""
import json
from .multiregime_gate_trial import trial

DISCOVERY=('up_down_recovery','steady_up','steady_down')
HOLDOUT=('choppy','delayed_reversal','down_recovery')
THRESHOLDS=(None,-.03,-.01,0.,.01,.03)

def objective(rows):
    # Equal-weight episodes, penalize maximum drawdown; no hidden threshold changes.
    return sum(x['return']-x['mdd'] for x in rows)/len(rows)

def run():
    cache={(scenario,t):trial(scenario,t) for scenario in DISCOVERY+HOLDOUT for t in THRESHOLDS}
    discovery={str(t):round(objective([cache[(s,t)] for s in DISCOVERY]),6) for t in THRESHOLDS}
    # Tie-break: first in predeclared order; freeze before any holdout scoring.
    chosen=max(THRESHOLDS,key=lambda t:discovery[str(t)])
    holdout={s:{'frozen':cache[(s,chosen)],'no_gate':cache[(s,None)]} for s in HOLDOUT}
    return {'scope':'SYNTHETIC_SEPARATE_EPISODE_HOLDOUT_NOT_MARKET_VALIDATION',
        'discovery_order':DISCOVERY,'holdout_order':HOLDOUT,
        'objective':'mean_episode_return_minus_episode_mdd',
        'discovery_scores':discovery,'frozen_threshold':chosen,
        'holdout':holdout,
        'holdout_frozen_objective':round(objective([cache[(s,chosen)] for s in HOLDOUT]),6),
        'holdout_no_gate_objective':round(objective([cache[(s,None)] for s in HOLDOUT]),6)}
if __name__=='__main__':print(json.dumps(run(),indent=2))
