"""Evaluate GA6-H context-free expressions using only supplied decision-time features.
A niche/context is metadata for reporting, not part of chromosome identity.
"""
from math import isfinite
from context_free_genome import validate_tree

def score_tree(tree, features):
    """features keyed (family, window, transform); absent features invalidate the signal.
    Returns (bool, margin) where margin measures signed distance to thresholds.
    """
    validate_tree(tree)
    def visit(node):
        if 'feature' in node:
            key=(node['feature'],node['window'],node['transform'])
            value=features.get(key)
            if value is None or not isfinite(float(value)):return None
            delta=float(value)-float(node['threshold'])
            margin=delta if node['direction']=='>=' else -delta
            return (margin>=0,margin)
        children=[visit(c) for c in node['children']]
        if any(c is None for c in children):return None
        if node['op']=='AND':return (all(c[0] for c in children),min(c[1] for c in children))
        return (any(c[0] for c in children),max(c[1] for c in children))
    return visit(tree)

def evaluate_contexts(genome, records):
    """records: (context_label, symbol, decision_features); no label in genome.
    Returns independent context-specific evidence; no forward outcome labels used.
    """
    genome.validate()
    output={}
    for context,symbol,features in records:
        result=score_tree(genome.tree,features)
        stats=output.setdefault(context,{'eligible':0,'passed':0,'missing':0,'symbols':[]})
        if result is None:stats['missing']+=1;continue
        stats['eligible']+=1
        if result[0] and result[1]>=genome.entry_threshold:
            stats['passed']+=1;stats['symbols'].append(symbol)
    return output
