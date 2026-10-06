#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,time
REPO=Path(__file__).resolve().parents[1]
TEST=REPO/"Tests/conforming_ga/test_g2_mutation_proof.py"
OUT=REPO/"Research/Conformance/MTS_G2_MUTATION_SEMANTIC_EVIDENCE_20261006.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
names=["test_every_claude_alternative_is_directly_reachable","test_class_sampling_is_independent_of_low_level_count_exact_contract","test_plateau_does_not_touch_conditional_operation_distributions","test_replace_replaces_a_typed_subtree_not_necessarily_whole_slot","test_unwrap_can_remove_nested_wrapper_without_collapsing_root","test_wrap_all_claude_wrapper_families_are_reachable_and_valid","test_wrap_can_target_nested_subtree_without_replacing_root"]
nodes=[f"{TEST.relative_to(REPO)}::{n}" for n in names]
p=subprocess.run([str(REPO/".venv/bin/python"),"-m","pytest","-q",*nodes],cwd=REPO,capture_output=True,text=True)
obj={"schema":"MTS_G2_MUTATION_SEMANTIC_EVIDENCE_V1","passed":p.returncode==0,"fixture_file":str(TEST.relative_to(REPO)),"fixture_sha256":sha(TEST),"controlled_fixtures":names,"result":p.stdout.strip(),"generated_at":time.time()}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
print(json.dumps(obj,indent=2));raise SystemExit(p.returncode)
