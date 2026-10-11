#!/usr/bin/env python3
"""Conservative evidence ledger: absence of proof cannot be certified as pass."""
import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.preflight_horizon_evolution_20261010 import BASE,REQUIRED_HORIZONS
checks={
 'causal_pit_verified':(False,'Real-data array horizon coverage is verified; independent point-in-time feature provenance and no-leakage proof are not.'),
 'dev80_only_verified':(True,'DEV80-only source paths and non-heldout tests were inspected; does not certify upstream construction.'),
 'confidence_calibrated':(False,'No empirical family-wise false-positive/coverage calibration under adaptive evolutionary selection.'),
 'multiple_testing_adjusted':(False,'Bonferroni utility is not wired into adaptive GA curation and trial-count accounting.'),
 'risk_policy_verified':(False,'Synthetic cash/R1 portfolio tests are not real-price historical crash and catastrophic-risk certification.'),
 'restart_recovery_verified':(False,'Journal and serial-controller smoke tests do not demonstrate kill/restart of live evaluator with deterministic replay.'),
 'economic_review_verified':(False,'Treasury annualized-yield proxy and synthetic costs do not establish full historical execution/slippage and portfolio economics.'),
 'launch_dry_run_passed':(False,'Authorization-denial smoke passed, but full isolated launch-and-restart dry run not executed.')
}
report={'status':'BLOCKED','scope':'THIRTEEN_WINDOW_2_TO_65','evaluated_horizons':list(REQUIRED_HORIZONS),'checks':{k:{'verified':v,'evidence_gap':why} for k,(v,why) in checks.items()},'scientific_certification_granted':False,'protected_heldouts_accessed':False,'ga_launched':False}
BASE.mkdir(parents=True,exist_ok=True)
(BASE/'thirteen_window_scientific_audit_20261011.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'verified':[k for k,(v,_) in checks.items() if v],'blocked':[k for k,(v,_) in checks.items() if not v]},indent=2))
