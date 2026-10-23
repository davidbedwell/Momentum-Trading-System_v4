import sys,json,random,hashlib,sqlite3
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from ga5_chromosome_contract import Genome
from niche_portfolio_breeder_v1 import breed_niche_portfolio
from pareto_breeding import breed_pareto
from optimizer_v3 import fitness
from canonical_engine import ResultCache
p=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019')
state=json.loads((p/'checkpoint_unified.json').read_text())
members=[Genome(**x) for x in state['members']]
cache=ResultCache(p/'evaluations.sqlite')
scored=[]
for g in members:
 k=cache.key(g,state['data'],'DEV79_FULL','unified:'+state['policy']+':'+state['code'])
 result=cache.get(k)
 if result is not None:scored.append((fitness(result),g,result))
cache.close()
print('cached',len(scored),'of',len(members),flush=True)
if len(scored)<26:raise SystemExit('Insufficient matched evaluated population; no comparison')
r1=random.Random(1700);r2=random.Random(1700)
old,os=breed_pareto(scored,r1,500)
new,ns=breed_niche_portfolio(scored,r2,500)
def summarize(children,parents):
 ids={g.identity() for g in parents}
 return dict(niche_counts={n:sum(g.niche==n for g in children) for n in sorted({g.niche for g in children})},unique=len({g.identity() for g in children}),novel=sum(g.identity() not in ids for g in children),retained=sum(g.identity() in ids for g in children))
report=dict(generation=state['generation'],population=500,matched_evaluations=len(scored),original=summarize(old,members),corrected=summarize(new,members),common_offspring=len({g.identity() for g in old}&{g.identity() for g in new}),comparison='BREEDING_ONLY_NO_NEW_OFFSPRING_PORTFOLIO_EVALUATION')
out=p/'all13_niche_screen'/'all13_fitness_firstwave'/'matched_checkpoint_breeder_comparison.json'
out.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
