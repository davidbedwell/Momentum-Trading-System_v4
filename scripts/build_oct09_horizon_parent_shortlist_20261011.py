#!/usr/bin/env python3
"""Build an auditable Oct 9 parent shortlist; does not launch or alter GA."""
import collections,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'Research/Preparation/horizon_generational_20261010/parent_study'
def rows(name):return [json.loads(x) for x in (p/name).read_text().splitlines() if x.strip()]
rankings=rows('cross_generation_window_rankings.jsonl')
gen1={r['gen1_index']:r for r in rows('gen1_parent_definitions.jsonl')}
gen2={r['offspring_id']:r for r in rows('gen2_reconciled_ranked_candidates.jsonl')}
chosen={(r['generation'],r['id']) for r in rankings if r['provisional_rank']<=5}
# Retain generation-one representation beyond its two overall top-five leaders.
# These six had positive nominal LCB on >=3 horizons in a top-three Gen1 window.
extra_gen1={1006,586,4320,976,1568,2298}
chosen|={(1,x) for x in extra_gen1}|{(1,1660),(2,766)}
by_id=collections.defaultdict(list)
for r in rankings:
 if (r['generation'],r['id']) in chosen:by_id[(r['generation'],r['id'])].append(r)
output=[]
for gen,id_ in sorted(chosen):
 rr=by_id[(gen,id_)];assert rr,('missing window evidence',id_)
 assert all(x['generation']==gen for x in rr)
 definition=(gen1 if gen==1 else gen2).get(id_)
 assert definition is not None,('missing definition',id_)
 assert definition['chromosomes'] and definition['side']=='LONG'
 assert all(x['genome_hash']==rr[0]['genome_hash'] for x in rr)
 if 'genome_hash' in definition:assert definition['genome_hash']==rr[0]['genome_hash']
 top5=[x for x in rr if x['provisional_rank']<=5]
 output.append({'id':id_,'generation':gen,'genome_hash':rr[0]['genome_hash'],'side':'LONG','chromosomes':definition['chromosomes'],'parent_ids':definition.get('parents'),'top5_windows':[x['window'] for x in sorted(top5,key=lambda v:v['window'])],'top5_count':len(top5),'best_nominal_lcb95':max(x['median_lcb95'] for x in rr),'reason':'MANDATORY' if (gen,id_) in ((1,1660),(2,766)) else 'CROSS_GENERATION_TOP5' if top5 else 'GEN1_DIVERSITY','fitness_status':'REQUIRES_FRESH_DEV80_REEVALUATION'})
assert len(output)==len(chosen) and {(1,1660),(2,766)}.issubset(chosen)
result={'status':'PROPOSED_PARENT_SEEDS_NOT_LAUNCHED','source':'OCT09_GEN1_GEN2_DEV80_PROVISIONAL','selection':'union of top five per 13 windows plus six Gen1 breadth representatives','count':len(output),'gen1_count':sum(x['generation']==1 for x in output),'gen2_count':sum(x['generation']==2 for x in output),'no_legacy_fitness_import':True,'certification':'NOT_CERTIFIED','parents':output}
out=p/'oct09_parent_seed_shortlist_20261011.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'count':len(output),'gen1':result['gen1_count'],'gen2':result['gen2_count'],'ids':[x['id'] for x in output]}))
