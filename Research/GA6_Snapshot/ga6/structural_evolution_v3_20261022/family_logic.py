"""Independent, chronological-safe boolean family expression primitive.
Does not alter production Genome or evaluator. Leaves are feature-threshold predicates.
"""
from math import isfinite
from ga5_feature_families import FAMILIES
OPS={'AND','OR'}
def validate(node):
 if not isinstance(node,dict):raise ValueError('Node must be mapping')
 if 'family' in node:
  if set(node)!={'family','threshold','comparison'} or node['family'] not in FAMILIES or node['comparison'] not in ('>=','<=') or not isfinite(float(node['threshold'])):raise ValueError('Invalid leaf')
  return frozenset((node['family'],))
 if set(node)!={'op','children'} or node['op'] not in OPS or not isinstance(node['children'],list) or len(node['children'])<2:raise ValueError('Invalid logical node')
 families=frozenset()
 for child in node['children']:
  used=validate(child)
  if families & used:raise ValueError('Duplicate family within expression')
  families|=used
 return families
def evaluate(node,features):
 validate(node)
 def visit(n):
  if 'family' in n:
   v=features.get(n['family'])
   if v is None or not isfinite(float(v)):return None
   return float(v)>=float(n['threshold']) if n['comparison']=='>=' else float(v)<=float(n['threshold'])
  values=[visit(c) for c in n['children']]
  # Missing inputs invalidate the signal; do not silently convert missing to False.
  if any(v is None for v in values):return None
  return all(values) if n['op']=='AND' else any(values)
 return visit(node)
