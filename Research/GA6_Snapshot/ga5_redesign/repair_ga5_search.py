"""Repair GA5 research grammar, historical feature access, portfolio capacity and niche seeds."""
from pathlib import Path
import json
p=Path('/opt/mts')
contract=p/'ga5_chromosome_contract.py'
s=contract.read_text()
s=s.replace('FEATURES=set(FAMILIES)|{"momentum_5","momentum_20","volatility_20","relative_strength_20","breadth_20"}', 'from ga5_redesign.ga4_registry import GA4_FEATURES\nFEATURES=set(FAMILIES)|{"momentum_5","momentum_20","volatility_20","relative_strength_20","breadth_20"}|set(GA4_FEATURES)')
s=s.replace('elif field=="max_hold_sessions":v=max(1,min(252,g.max_hold_sessions+rng.choice([-5,5])))','elif field=="max_hold_sessions":v=max(1,min(252,g.max_hold_sessions+rng.choice([-30,-10,-5,5,10,30])))')
s=s.replace('v=getattr(g,field)+rng.choice([-.01,.01])','v=getattr(g,field)+rng.choice([-.20,-.10,-.05,-.01,.01,.05,.10,.20])')
s=s.replace('if field=="max_weight":v=max(v,g.base_weight)','if field=="max_weight":v=max(v,g.base_weight)')
contract.write_text(s)
adapter=p/'ga5_feature_adapter.py';s=adapter.read_text()
s=s.replace('from ga5_feature_families import FAMILIES','from ga5_feature_families import FAMILIES\nfrom ga5_redesign.ga4_registry import GA4_FEATURES')
s=s.replace('if source not in FAMILIES:raise ValueError("Unknown feature: "+name)','if source not in FAMILIES and source not in GA4_FEATURES:raise ValueError("Unknown feature: "+name)')
adapter.write_text(s)
evaluator=p/'ga5_redesign/guarded_evaluator.py';s=evaluator.read_text()
s=s.replace('fee=.001,max_positions=5,annual_cash_yield=None','fee=.001,max_positions=None,annual_cash_yield=None')
s=s.replace('if not genome.valid():raise ValueError("Invalid genome")','if not genome.valid():raise ValueError("Invalid genome")\n if max_positions is None:max_positions=max(1,int(1.0/genome.base_weight)+1)\n if not 1<=max_positions<=79:raise ValueError("Invalid portfolio capacity")')
evaluator.write_text(s)
print('Patched chromosome grammar, mutation reach, adapter and dynamic portfolio capacity')
