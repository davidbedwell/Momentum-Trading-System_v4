"""Independent grouped-logic signal adapter; no production evaluator modification.
Structural predicates gate entry only. Existing exits, sizing and risk remain unchanged.
"""
from ga6.upgrade_reuse_20261021.family_logic import validate,evaluate as evaluate_tree
from fast_decision import evaluate as legacy_decision

def decision(genome,features,position,price,entry_tree=None):
 action,weight=legacy_decision(genome,features,position,price)
 if entry_tree is None or position.shares or action!='ENTER':return action,weight
 validate(entry_tree)
 verdict=evaluate_tree(entry_tree,features)
 if verdict is not True:return 'NO_ENTRY',0.
 return action,weight
