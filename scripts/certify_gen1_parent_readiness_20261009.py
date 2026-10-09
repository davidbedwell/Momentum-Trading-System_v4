"""Fail-closed certification of Gen1 readiness against frozen governance."""
import json,pathlib,hashlib,datetime
root=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
out=root/'scientific_certification_20261009';out.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text()) if p.exists() else {}
parents=root/'horizon_grouped_pareto_20261009/provisional_168_priority.jsonl'
rows=[json.loads(x) for x in parents.read_text().splitlines()]
replay=read(root/'parent_168_causal_replay_20261009/result.json')
phase_b=read(root/'phaseB_dev80_126_20261009/manifest.json')
b_eval=read(root/'phaseB_parent_study_20261009/manifest.json')
c_eval=read(root/'phaseC_parent_study_20261009/manifest.json')
d_eval=read(root/'phaseD_diagnostic_20261009/manifest.json')
checks={
 '168_distinct_parent_identities':len(rows)==168 and len({r['index'] for r in rows})==168,
 'original_replay_1602_exact_checks':replay.get('status')=='PASS' and replay.get('checks')==1602 and replay.get('failed_candidates')==0,
 'extended_path_prefix_preserved':phase_b.get('horizons')==126 and all(phase_b.get('prefix_comparisons',{}).values()) and len(phase_b.get('prefix_comparisons',{}))==6,
 'phase_b_168_extended_horizons_complete':b_eval.get('candidate_count')==168,
 'phase_c_168_all_horizons_complete':c_eval.get('candidate_count')==168 and len(c_eval.get('horizons',[]))==126,
 'phase_d_descriptive_evidence_complete':d_eval.get('candidates')==168,
 'independent_episode_robustness_certified':False,
 'selection_multiplicity_adjusted_reliability_certified':False,
 'behavioral_near_duplicate_control_certified':False,
 'full_portfolio_lifecycle_and_mdd_certified':False,
 'matched_passive_and_cost_audit_certified':False,
 'frozen_minimum_sample_and_parent_eligibility_gate_certified':False,
}
result={'decision':'PASS' if all(checks.values()) else 'FAIL_CLOSED_NOT_AUTHORIZED','checks':checks,'completed_checks':sum(checks.values()),'total_checks':len(checks),'gen2_authorized':all(checks.values()),'scope':'DEV80 only','parents_sha256':hashlib.sha256(parents.read_bytes()).hexdigest(),'note':'Missing scientific evidence cannot be treated as PASS; no protected datasets touched.'}
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
