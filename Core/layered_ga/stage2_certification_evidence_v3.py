"""Independent evidence checks; no certificate by declaration or self-attestation."""
from collections import defaultdict
from math import isfinite
from Core.layered_ga.stage2_multiobjective_v3 import dominates, nondominated_sort

def audit_evolutionary_ledger(ledger):
    """Recompute dominance independently from actual per-generation candidate curves.

    Requires reproduction lineage, full candidate evaluations and an untouched
    selection-validation ledger. A synthetic declaration cannot substitute.
    """
    failures=[]
    if not isinstance(ledger,dict):return ['evolutionary ledger absent']
    generations=ledger.get('generations',[])
    if len(generations)<2:failures.append('at least two evaluated generations required')
    for i,gen in enumerate(generations):
        items=gen.get('evaluated_observations',[])
        if not items:failures.append(f'generation {i}: no observations');continue
        from Core.layered_ga.stage2_multiobjective_v3 import Observation
        try:
            obs=[Observation(**p) for p in items]
            if not all(isfinite(p.ev_net) and isfinite(p.lcb95) and isfinite(p.mae_mean) for p in obs):
                failures.append(f'generation {i}: nonfinite objective')
            fronts=nondominated_sort(obs)
            reported=set(gen.get('first_front',[]))
            actual={(p.candidate_id,p.horizon) for p in fronts[0]}
            if reported!={tuple(x) for x in actual}:failures.append(f'generation {i}: incorrect nondominated front')
            if not gen.get('selection_lineage'):failures.append(f'generation {i}: reproduction lineage absent')
        except (TypeError,ValueError,KeyError) as exc:
            failures.append(f'generation {i}: invalid ledger {exc}')
    if not ledger.get('heldout_selection_adjusted_validation'):
        failures.append('independent selection-adjusted validation absent')
    return failures

def audit_catastrophic_policy(policy):
    """Reject missing, post-hoc or unfrozen risk constraints; do not invent 2R."""
    if not isinstance(policy,dict):return ['catastrophic policy absent']
    failures=[]
    for k in ('policy_hash','frozen_at','search_started_at','metrics','thresholds','provenance'):
        if not policy.get(k):failures.append('catastrophic policy missing '+k)
    if policy.get('frozen_at') and policy.get('search_started_at'):
        if policy['frozen_at']>=policy['search_started_at']:
            failures.append('catastrophic policy was not frozen before search')
    if policy.get('hard_2r_cap') is True:failures.append('unapproved hard 2R cap')
    if not policy.get('independent_recalculation'):
        failures.append('catastrophic risk independently recalculated evidence absent')
    return failures
