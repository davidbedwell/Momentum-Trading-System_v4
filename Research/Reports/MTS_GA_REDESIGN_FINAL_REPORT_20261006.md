# MTS GA Redesign — Final DEV117 Report

Status: DEV117_COMPLETE

Calibration: {"null_shift_sessions": 4227, "null_best_cagr_small_calibration": 0.1354134116383674, "null_equal_weight_cagr": 0.14858293533325195, "null_best_excess_vs_equal_weight": -0.013169523694884555, "planted_recovered_seeds": 4, "planted_required": 3, "pass": true}

## Frozen training sets
- Fold 0: 6825cb0dd4eb11fc54283e66dfae446a0eaef46ebaf0ebdd1757e460c1504747
- Fold 1: 07061a0df94e3630e6809f59a0f8ddfe49c95c3c4cf07845b213fc428069117d
- Fold 2: 49d5cc0ba4e7ce33372a44d48d03e7420abe68fbdd78b471b898be148bddd762
- Fold 3: 9cd9617dc94ce92dbbd68614b20fa4deb55c649662762101ba568ad3bae7ffe6

## Blind cross-stock transport
### Fold 0
- Train CAGR 12.061%, MDD -9.688%; blind CAGR 7.938%, MDD -26.854%; SAFE 53.678%
- Train CAGR 14.362%, MDD -13.817%; blind CAGR 8.905%, MDD -32.208%; SAFE 37.614%
- Train CAGR 16.736%, MDD -18.565%; blind CAGR 8.057%, MDD -46.466%; SAFE 44.417%
- Train CAGR 19.120%, MDD -24.258%; blind CAGR 17.599%, MDD -27.349%; SAFE 21.003%
- Train CAGR 21.143%, MDD -28.597%; blind CAGR 16.875%, MDD -34.863%; SAFE 11.411%
- Train CAGR 22.442%, MDD -34.953%; blind CAGR 9.054%, MDD -48.071%; SAFE 18.687%
- Train CAGR 24.610%, MDD -39.126%; blind CAGR 8.202%, MDD -44.986%; SAFE 14.539%
### Fold 1
- Train CAGR 24.925%, MDD -7.928%; blind CAGR 1.200%, MDD -24.813%; SAFE 99.130%
- Train CAGR 25.869%, MDD -39.992%; blind CAGR 15.988%, MDD -29.516%; SAFE 33.431%
### Fold 2
- Train CAGR 8.797%, MDD -9.988%; blind CAGR 7.323%, MDD -10.441%; SAFE 66.726%
- Train CAGR 12.986%, MDD -14.960%; blind CAGR 10.703%, MDD -15.224%; SAFE 45.366%
- Train CAGR 17.890%, MDD -19.953%; blind CAGR 13.672%, MDD -23.919%; SAFE 21.825%
- Train CAGR 19.580%, MDD -24.960%; blind CAGR 15.759%, MDD -30.034%; SAFE 12.924%
- Train CAGR 20.304%, MDD -29.864%; blind CAGR 14.604%, MDD -30.154%; SAFE 12.698%
- Train CAGR 20.437%, MDD -31.289%; blind CAGR 14.460%, MDD -31.424%; SAFE 11.333%
- Train CAGR 21.180%, MDD -39.942%; blind CAGR 14.432%, MDD -48.563%; SAFE 12.763%
### Fold 3
- Train CAGR 8.970%, MDD -9.646%; blind CAGR 1.682%, MDD -18.120%; SAFE 98.833%
- Train CAGR 10.943%, MDD -14.910%; blind CAGR 9.647%, MDD -27.953%; SAFE 56.886%
- Train CAGR 14.669%, MDD -19.693%; blind CAGR 9.643%, MDD -19.193%; SAFE 46.953%
- Train CAGR 24.781%, MDD -24.457%; blind CAGR 14.748%, MDD -47.478%; SAFE 16.975%
- Train CAGR 26.940%, MDD -29.452%; blind CAGR 15.781%, MDD -58.557%; SAFE 14.265%
- Train CAGR 27.311%, MDD -34.404%; blind CAGR 15.508%, MDD -59.399%; SAFE 13.829%
- Train CAGR 27.479%, MDD -35.707%; blind CAGR 15.526%, MDD -59.720%; SAFE 13.037%

## Governance
All four training finalist sets were frozen and SHA-256 hashed before any blind37 replay. DV25/A25/A75/B100 were not opened. Crash episodes are reported as independent market episodes, not multiplied across folds.
