import sys,json,random
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from ga5_chromosome_contract import Genome
from niche_portfolio_breeder_v1 import breed_niche_portfolio
from pareto_breeding import breed_pareto
from optimizer_v3 import fitness
p=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019')
state=json.loads((p/'checkpoint_unified.json').read_text())
members=[Genome(**x) for x in state['members']]
from canonical_engine import ResultCache
cache=ResultCache(p/'evaluations.sqlite')
print('cache API', [x for x in dir(cache) if not x.startswith('_')])
print('checkpoint keys',list(state.keys()))
cache.close()
