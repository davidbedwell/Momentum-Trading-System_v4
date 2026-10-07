# MTS G2 H.4 Hypervolume / Plateau Clarification Request

You are Claude Opus 5.5. You authored the controlling G2 redesign review in:
Research/Reviews/MTS_CLAUDE_GA_REDESIGN_REVIEW_20261005_221916.md

We need a narrow clarification of YOUR ORIGINAL H.4 intent. Do not redesign G2 unless you clearly label a separate prospective recommendation. The frozen wording is:

H.2: 9 islands x 250 individuals per fold; base 500 generations.
H.4 Plateau rules:
- First plateau (island training-hypervolume gain < 0.5% over 40 generations): inject 20% immigrants and up-weight structural mutation.
- Second consecutive plateau: freeze the island archive and reallocate its compute.

Problem encountered:
A four-fold H.7 null calibration reached generation 40. All 36 island-fold combinations were classified as first-plateau. Runtime per 10 generations deteriorated approximately 81 min (10->20), 120 min (20->30), 159 min (30->40) on the 64-vCPU machine. This initially suggested universal search stagnation and raised a decision whether to spend another 11-14 hours reaching the second plateau window.

Forensic audit then found an implementation defect in Core/conforming_ga/ga_g2.py. The old function claimed exact 2-D dominated hypervolume for maximize(CAGR, signed-MDD), but sorted frontier points ascending in CAGR and accumulated area only when MDD increased. Recorded hypervolume could DECREASE even though the archive was cumulative. Therefore the 36/36 plateau classification cannot be trusted as evidence of true plateau.

The old Pareto implementation was also naive O(n^2). By generation 40, cumulative archive sizes across folds were 2,784; 2,239; 4,654; 1,976 entries. One Fold-2 novelty archive contained 2,476 entries but only 80 corrected Pareto-frontier points. This is a plausible contributor to the generation-time deterioration.

Current engineering revision:
1. The gen-40 checkpoints were preserved before changes.
2. hypervolume() was replaced with an exact deterministic 2-D maximize/maximize dominated-area sweep.
3. pareto() was replaced with an exact deterministic O(n log n) 2-D frontier algorithm.
4. Regression tests now verify a known rectangle-union value, monotonic hypervolume as candidates are added to a cumulative archive, and optimized-Pareto equivalence to brute-force dominance on deterministic random unique metrics.
5. The affected G2 tests pass (15/15 in the broader affected suite).
6. No scientific parameter, population, generation budget, mutation probability, plateau threshold, partition, fitness objective, or H.4 rule has been changed.
7. The expensive H.7 null remains STOPPED.

Examples of corrected generation-40 HV using the existing ref=(-1,-1):
Fold 0: band_10 1.093547088; band_15 1.124115583; band_20 1.157932428; band_25 1.201863941; band_30 1.217592546; band_35 1.251473059; band_40 1.258507712; global 1.373077770; novelty 1.370539923.
Fold 2: global 1.403342028; novelty 1.372750427.

Critical ambiguity:
Your H.4 says "training-hypervolume gain < 0.5% over 40 generations", but the review does not explicitly define:
- the hypervolume reference point;
- whether "gain %" means (HV_t/HV_t-40)-1 on raw dominated area;
- whether reference-area baseline should be subtracted before percentage gain;
- whether HV should be normalized to a fixed objective box/range;
- whether each MDD-band island should calculate HV over its feasible frontier only, while global/novelty use their own complete frontier;
- whether cumulative archive HV or current-population HV was intended.

Because ref=(-1,-1) creates a large baseline dominated area around ~1.x, a 0.5% relative threshold may behave very differently from a percentage computed on excess/normalized hypervolume. We will NOT invent a definition.

Please answer these questions explicitly:

A. ORIGINAL INTENT ONLY
1. What exact mathematical definition of "island training-hypervolume" did H.4 intend?
2. What exact fixed reference point did you intend for objectives CAGR and signed MDD? If no exact point was specified/intended, say so.
3. What exact formula did you intend for "hypervolume gain < 0.5% over 40 generations"?
4. Was percentage gain intended on raw HV including the reference rectangle, excess HV after subtracting a baseline, or normalized HV?
5. Was H.4 intended to use the cumulative island archive or current population?
6. For MDD-band islands, should HV be computed only from receiver-feasible/archive-admitted points? What about global and novelty islands?
7. Should a cumulative archive's HV be mathematically non-decreasing? Confirm.
8. Is the corrected exact 2-D maximize/maximize sweep described above consistent with your intended metric, subject to whatever reference/normalization you specify?

B. VALIDITY OF THE EXISTING GEN-40 RUN
9. The generations 1-40 populations were evolved normally, but plateau intervention was first triggered at generation 40 using the defective HV history. No post-trigger generations have been run. Can the preserved gen-40 populations/archives be salvaged by recomputing the correct HV history from checkpoints/state and then applying the correct gen-40 plateau decision? Or must H.7 restart from generation 0?
10. If only checkpoints every 10 generations exist, is recomputing HV at 10/20/30/40 sufficient for the H.4 40-generation decision, or does H.4 require per-generation HV history? State the exact requirement.
11. Does the defective HV calculation affect evolution before generation 40 in any other way under your design, or only the plateau decision at the first eligible window?

C. ENGINEERING / COMPUTE
12. Is replacing naive O(n^2) Pareto extraction with an exactly equivalent deterministic O(n log n) algorithm scientifically neutral and permitted?
13. Should cumulative archives be Pareto-pruned/deduplicated as they grow, provided this provably preserves every non-dominated point and all other archive semantics? Or did you intend historical dominated members to remain for another purpose?
14. Given the observed archive sizes and runtime growth, identify any other algorithmic-complexity issue in the stated G2 design that should be optimized WITHOUT changing the scientific experiment.

D. DECISION
15. Give one of these explicit dispositions:
- RESUME_FROM_GEN40 after recomputation (state exact required steps);
- RESTART_H7_FROM_GEN0 (state why);
- BLOCKED_PENDING_A_SPECIFIC_UNRESOLVED_DESIGN_CHOICE (state exactly what choice).

Finally, include a short section titled "Prospective recommendations (NOT original H.4 intent)" only if you now recommend changing H.4. Keep those recommendations clearly separate so they cannot be mistaken for clarification of the frozen design.
