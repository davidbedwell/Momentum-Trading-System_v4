# G2 Nebius Recovery Inventory — 2026-10-07

Status: FORENSIC PRESERVATION IN PROGRESS
Source host: computeinstance-e04y8wmqwr0gaf707f
Source repository path: /home/ubuntu/Momentum-Trading-System_v4
Source condition: working tree has no .git directory; recovered by direct file comparison.
Destination branch: forensic/g2-recovery-20261007
Base GitHub commit: edbb4bcda76adfa42bfe78be99d7d68d3a06527f

## Safety boundary
No GA was started during recovery. G2 is being used only as a source/recovery machine.
Generated __pycache__, Numba cache files, and large checkpoint binaries are excluded from normal source history.

## Critical recovered source
- Core/conforming_ga/ga_g2.py — corrected exact Pareto/hypervolume implementation and G2 controller state.
- Tests/conforming_ga/test_g2_hypervolume_regression.py — regression tests for known union area, cumulative monotonicity, brute-force Pareto equivalence, excess-HV plateau semantics, and equal-objective strict dominance.

## Defective imported gen40 checkpoints
The binary checkpoints remain outside normal Git source history. Their SHA-256 identities are:
- fold0: 15a8f4bca6dd13950ec10b091a9620b21f3b09f968579b704643c29eb30945b6
- fold1: ba76736304f71fbcbb3ee36b4462db0a88e5c755458660a829307df535805cba
- fold2: aac98fb8eb10131b3c02c51cbce653b9311a6a6b1bebbbb0143e84a6d4e60e7a
- fold3: 023d80c245d3a819d1ece55d99970060854a17cd996d8c121dceaa506b95d59f

These checkpoints were quarantined under:
Research/Forensic/H7_NULL_IMPORTED_DEFECTIVE_GEN40_20261007/

## Historical correctness warning
Historical G2 checkpoint hypervolume histories were generated under a defective prior hypervolume implementation. The corrected implementation demonstrates that stored historical HV values are not trustworthy as controller/plateau evidence. Do not resume the historical null run as a clean calibrated search procedure without a separately approved scientific disposition.

## Remaining recovery classes
The machine inventory also contains Oct. 6–7 workflow/controller scripts, approved manifests, governance protocols, engineering incident reports, H.4 review artifacts, and forensic evidence. These must be compared and preserved before G2 is considered fully recovered.
