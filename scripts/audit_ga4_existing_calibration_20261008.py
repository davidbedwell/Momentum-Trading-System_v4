#!/usr/bin/env python3
"""Read-only reconciliation of existing Stage 2 calibration evidence; fail closed."""
import hashlib,json
from collections import Counter
from pathlib import Path
from Core.layered_ga.stage2_calibration_gate_v3 import certify_calibration,REQUIRED_CASE_KEYS
ROOT=Path(__file__).resolve().parents[1]
CAL=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration'
SOURCES={
 'legacy_scalar':'evolutionary_results.json',
 'multiobjective_long':'nsga2_batch_evolutionary_evidence.json',
 'multiobjective_short':'ga4_short_evolutionary_evidence.json',
 'statistical':'ga4_statistical_evidence_measured.json',
 'plant_integrity':'plant_integrity_results.json',
}
def identity(x):return (str(x['family']),str(x['shape']),float(x['effect']))
def main():
 data={k:json.loads((CAL/v).read_text()) for k,v in SOURCES.items()}
 keys={}
 for name in ('legacy_scalar','multiobjective_long','multiobjective_short','statistical'):
  cases=data[name]['cases']; identities=[identity(x) for x in cases]
  keys[name]=set(identities)
  if len(identities)!=len(keys[name]):raise RuntimeError('duplicate case identities: '+name)
 reference=keys['statistical']
 intersections=set.intersection(*keys.values())
 if any(v!=reference for v in keys.values()):raise RuntimeError('case identity mismatch')
 merged=[]
 for c in data['statistical']['cases']:
  merged.append({k:c[k] for k in REQUIRED_CASE_KEYS if k in c})
 gate=certify_calibration(merged,frozen_parameters_verified=False)
 nulls=[c for c in merged if c['effect']==0]
 strong=[c for c in merged if c['effect']==.02]
 summary={
  'decision':'FAIL' if gate['decision']!='PASS' else 'PASS',
  'certified':False,
  'scope':'existing evidence reconciliation only; no new market data accessed',
  'source_files':{k:{'path':v,'sha256':hashlib.sha256((CAL/v).read_bytes()).hexdigest()} for k,v in SOURCES.items()},
  'matched_case_count':len(intersections),
  'matched_families':sorted({k[0] for k in intersections}),
  'multiobjective_method':'NSGA-II evidence recorded; independent verification pending',
  'legacy_scalar_not_certification_evidence':True,
  'plant_integrity_pass':data['plant_integrity'].get('passed') is True,
  'null_rejected_count':sum(c.get('null_target_specific_recovery') is False for c in nulls),
  'null_total':len(nulls),
  'strong_effect_positive_lcb_count':sum(c.get('target_region_positive_lcb95') is True for c in strong),
  'strong_effect_overlap_count':sum(c.get('target_region_overlap') is True for c in strong),
  'strong_effect_total':len(strong),
  'unverified_fields':{k:sum(c.get(k) is not True for c in merged) for k in ('independent_effective_n_verified','causal_costs_verified','long_short_evaluated_separately')},
  'gate':gate,
  'next_action':'Independently verify effective N, executable causal costs, selection-adjusted transport, and strong-effect recovery; do not reuse scalar legacy score as NSGA-II proof',
 }
 out=CAL/'ga4_existing_evidence_reconciliation_20261008.json'
 out.write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k not in ('source_files','gate')},indent=2))
 print('GATE_FAILURE_COUNT',len(gate['failed_criteria']))
if __name__=='__main__':main()
