"""Independent grouped-logic signal adapter; no production evaluator modification.
Structural predicates gate entry only. Existing exits, sizing and risk remain unchanged.
"""
from ga6.structural_evolution_v3_20261022.family_logic import validate,evaluate as evaluate_tree
from fast_decision import evaluate as legacy_decision

def decision(genome,features,position,price,entry_tree=None):
    action,weight=legacy_decision(genome,features,position,price)
    # The structural expression is the entry authority, not a veto on legacy entry.
    # Legacy remains responsible for exits, sizing, scaling, and risk actions.
    if position.shares or entry_tree is None:
        return action,weight
    validate(entry_tree)
    verdict=evaluate_tree(entry_tree,features)
    if verdict is not True:
        return 'NO_ENTRY',0.
    # A flat legacy signal may be NO_ENTRY, but its sizing policy remains usable.
    # Never authorize entry with non-positive weight.
    weight=min(float(genome.max_weight),max(0.0,float(weight)))
    if weight<=0:
        weight=min(float(genome.max_weight),0.03)
    return 'ENTER',weight
