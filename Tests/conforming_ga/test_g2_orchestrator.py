from pathlib import Path
import importlib.util,json,pytest
P=Path(__file__).resolve().parents[2]/"scripts/run_mts_g2_workflow_20261006.py"
spec=importlib.util.spec_from_file_location("wf",P);wf=importlib.util.module_from_spec(spec);spec.loader.exec_module(wf)

def test_manifest_approved_structural_multiplier():
    m=wf.verify_manifest()
    assert m["production"]["plateau_structural_mutation_multiplier"]==2.0
    assert m["production"]["plateau_structural_mutation_duration_generations"]==40
    assert m["production"]["structural_mutation_class_ids"]==[4,5,6,11]
    assert m["production"]["context_applicability_classes_excluded_from_plateau_structural_multiplier"]==[7,8]
    assert m["production"]["plateau_nonstructural_mutation_probabilities"]=="unchanged unless explicitly required by frozen design"

def test_manifest_scopes_planted_64_and_production_250():
    m=json.loads(wf.MANIFEST.read_text())
    assert m["planted"]["population_per_island"]==64
    assert m["null"]["population_per_island"]==250
    assert m["production"]["population_per_island"]==250
    assert m["production"]["base_generations"]==500
    assert m["production"]["max_generations"]==800

def test_stage_order_is_governed():
    assert wf.STAGES==("NULL_CALIBRATION","ADVERSARIAL_CERTIFICATION","PRODUCTION_GA")

def test_structural_mutation_operator_set_is_exactly_frozen():
    m=json.loads(wf.MANIFEST.read_text())["production"]
    assert set(m["structural_mutation_class_ids"])=={4,5,6,11}
    assert 7 not in m["structural_mutation_class_ids"]
    assert 8 not in m["structural_mutation_class_ids"]
    assert m["plateau_structural_mutation_multiplier"]==2.0
    assert m["plateau_structural_mutation_duration_generations"]==40
