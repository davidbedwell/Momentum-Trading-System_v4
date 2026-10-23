"""Canonical two-block grouped structures, distinct from flat logic; no production writes."""
import itertools,json,hashlib,pathlib,collections
from ga5_feature_families import FAMILIES
OUT=pathlib.Path(__file__).resolve().parent
rows=[]
for k in range(3,9):
 for subset in itertools.combinations(FAMILIES,k):
  # Canonical unordered partition: first family must be in the first block.
  for size in range(1,k):
   for rest in itertools.combinations(subset[1:],size-1):
    left=(subset[0],)+rest;right=tuple(x for x in subset if x not in left)
    for root in ('AND','OR'):
     for lop in ('AND','OR') if len(left)>1 else ('LEAF',):
      for rop in ('AND','OR') if len(right)>1 else ('LEAF',):
       # Equal operators collapse to a flat expression; exclude.
       if lop in (root,'LEAF') and rop in (root,'LEAF'):continue
       key=(root,left,lop,right,rop)
       rows.append({'id':hashlib.sha256(repr(key).encode()).hexdigest()[:20], 'root':root,'left':left,'left_op':lop,'right':right,'right_op':rop,'arity':k,'status':'NOT_INTEGRATED_WITH_PORTFOLIO_EVALUATOR'})
assert len({r['id'] for r in rows})==len(rows)
(OUT/'grouped_two_block_catalog.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
report={'grouped_two_block_count':len(rows),'by_arity':dict(collections.Counter(r['arity'] for r in rows)),'scope':'canonical unordered two-block partitions only; excludes deeper nested trees and ordered signal pipelines','all_status':'NOT_INTEGRATED_WITH_PORTFOLIO_EVALUATOR'}
(OUT/'grouped_catalog_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
