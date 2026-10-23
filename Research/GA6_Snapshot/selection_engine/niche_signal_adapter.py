"""Fail-closed chromosome/niche decision adapter; original GA6 decision remains authority.
Niche recognition is supplied by a separately validated point-in-time classifier.
No assumption that a chromosome's niche ID establishes market niche membership.
"""
from math import isfinite
from ga5_chromosome_decisions import PositionState
from ga5_feature_adapter import LEGACY
from ga6.structural_independent_v2_20261022.structural_decision import decision
from ga6.structural_independent_v2_20261022.family_logic import validate


def required_features(candidate):
 g=candidate.genome
 fields={g.entry_feature,g.hold_feature,g.exit_feature,g.regime_feature,g.sizing_feature,g.replace_feature}
 def walk(node):
  if 'family' in node:fields.add(node['family'])
  else:
   for child in node['children']:walk(child)
 validate(candidate.entry_tree);walk(candidate.entry_tree)
 return fields


def evaluate_all(*,asof,symbol,market_features,recognized_niches,niche_evidence_cutoff,candidates,position_by_chromosome=None,close_price):
 """Evaluate every candidate in applicable niches, preserving original GA6 signals.
 Returns raw chromosome decisions, not invented probability/EV scores.
 Caller must provide point-in-time niche recognition; no fallback to all niches.
 """
 if recognized_niches is None or niche_evidence_cutoff is None:raise ValueError('niche recognition required')
 if niche_evidence_cutoff>asof:raise ValueError('future niche evidence')
 if not isfinite(close_price) or close_price<=0:raise ValueError('invalid close')
 positions=position_by_chromosome or {}
 out=[];missing=0
 for i,c in enumerate(candidates):
  if c.genome.niche not in recognized_niches:continue
  f={};valid=True
  for name in required_features(c):
   v=market_features.get(LEGACY.get(name,name))
   if v is None or not isfinite(float(v)):valid=False;break
   f[name]=float(v)
  if not valid:missing+=1;continue
  p=positions.get(i,PositionState())
  action,weight=decision(c.genome,f,p,close_price,c.entry_tree)
  out.append(dict(chromosome=i,symbol=symbol,asof=asof,niche=c.genome.niche,action=action,raw_weight=weight,evidence_cutoff=asof,features=f,identity=c.identity()))
 return dict(decisions=out,missing_features=missing,eligible_chromosomes=sum(c.genome.niche in recognized_niches for c in candidates))
