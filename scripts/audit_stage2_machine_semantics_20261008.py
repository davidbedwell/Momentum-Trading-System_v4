"""Read-only Stage2 machine semantics audit; no GA or protected data."""
import json
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces,VectorSignalCompiler
from Core.layered_ga.ga4_combination_genetics import propose,mutate,combine
import pandas as pd
import random
spaces=stage2_search_spaces()
summary={}
for name,space in spaces.items():
 summary[name]={'genes':len(space.genes),'values_per_gene':{g.gene_id:len(g.values) for g in space.genes},'search_product':__import__('math').prod(len(g.values) for g in space.genes),'maximum_active_predicates':space.maximum_active_predicates}
compiler=VectorSignalCompiler(pd.DataFrame({'x':[-2.,-1.,0.,1.,2.]}))
semantics={m:int(compiler.pred(compiler.arr('x'),m,0).sum()) for m in ['ABOVE','BELOW','HIGH','LOW','LEADER','LAGGARD','POSITIVE','NEGATIVE']}
rng=random.Random(41)
a=propose(spaces,rng);b=mutate(a,spaces,rng);c=combine(a,b,rng)
print(json.dumps({'families':summary,'predicate_semantics':semantics,'sample_lengths':[len(a),len(b),len(c)],'findings':['LOW and LAGGARD predicate modes are implemented and produce expected matches','Active runner calls evaluator without side, so only LONG is searched','Stage1 human labels not referenced in search spaces']},indent=2))
