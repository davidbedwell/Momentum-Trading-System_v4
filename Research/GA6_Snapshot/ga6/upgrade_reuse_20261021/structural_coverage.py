"""Deterministic, read-only GA6 family-structure coverage inventory.
This is a structural catalog, NOT an executable GA6 signal grammar.
"""
import itertools,json,hashlib,pathlib,collections
FAMILIES=('trend','momentum','volatility','volume','recursive','sector','breadth','relative_strength')
OUT=pathlib.Path(__file__).resolve().parent
catalog=[]
for k in range(1,len(FAMILIES)+1):
 for subset in itertools.combinations(FAMILIES,k):
  for logic in ('AND','OR'):
   record={'families':subset,'arity':k,'logic':logic,'status':'NOT_IMPLEMENTED_IN_GA6_EVALUATOR'}
   record['id']=hashlib.sha256(json.dumps([subset,logic]).encode()).hexdigest()[:20]
   catalog.append(record)
# Grouped syntax is intentionally not counted without a canonical grammar.
assert len({r['id'] for r in catalog})==510
(OUT/'structural_catalog.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in catalog))
report={'families':FAMILIES,'unordered_nonempty_subsets':255,'flat_AND_OR_structures':len(catalog),'grouped_structures':'NOT_ENUMERATED: canonical expression grammar required','current_ga6_executable_structures':0,'reason':'Existing GA6 genome supports six independent feature roles, not combinatorial family logic','coverage_status':dict(collections.Counter(x['status'] for x in catalog)),'production_modified':False}
(OUT/'structural_coverage_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
