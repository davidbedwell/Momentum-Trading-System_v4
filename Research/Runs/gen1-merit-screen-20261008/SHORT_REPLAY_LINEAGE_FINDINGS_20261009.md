# Gen1 SHORT Replay — Lineage Investigation, 2026-10-09

Status: SOURCE INPUT HASHES VERIFIED; SIGNAL REPLAY NOT REPRODUCED.

- DEV80 predictor SHA-256 1ca5c217c2932e6f957f0d17c94251a6d765615f36e00448891c6572bb50735d matches Phase A manifest.
- DEV80 execution array SHA-256 2bbfda7909e3e78ba032b93deca1afd8132620ea617af4e84f2f0c9ab270ad22 matches Phase A manifest.
- Thus input-file substitution is not supported as explanation for sample discrepancies.
- A replay using VectorSignalCompiler plus evaluate_curve does NOT reproduce archived Gen1 sample counts. Genome 1 SHORT horizon 1: 66721 vs 68641; genome 6 LONG horizon 1: 101005 vs 100797.
- The replay compiler/evaluator modules have existing unrelated working-tree modifications. Do not overwrite or commit those changes as part of this investigation.
- Need identify exact original Gen1 candidate screening runner (not currently identified among tracked scripts), its mask combination, eligibility and quantile semantics, and match archived n, effective_n, EV, SE, and LCB for multiple LONG/SHORT samples before environment stratification.
- No scientific environment conclusions, Gen2 launch, or protected-bank access authorized.
