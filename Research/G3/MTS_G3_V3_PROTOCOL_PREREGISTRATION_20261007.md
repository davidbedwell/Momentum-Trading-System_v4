# MTS G3 V3 PROTOCOL — PROSPECTIVE FREEZE CANDIDATE — 2026-10-07

## Authority
MTS machine-readable stage decisions alone authorize advancement. Assistant/operator commentary cannot override a gate. Missing, incomplete, malformed, or ambiguous artifacts fail closed.

## Evidence motivating V3
V1 inferential gate failed 0/3. V2 repaired structural search and failed 1/3 while all three Real-minus-null medians became positive. Frozen V2 diagnostics then showed Phase A 8/8 stock-level final medians > +0.3%; Phase C heterogeneous planted 3/8 recovery passed; Phase B estimated ~96 replicates for 80% power in the weakest N-A case. These diagnostics are design evidence, not inferential evidence.

## Fixed development panel
AAPL, MSFT, XOM, JPM, JNJ, CAT, WMT, NVDA. No stock may be removed because of diagnostic performance. Same 2500 aligned dates and same causal feature family as V2. No DEV50, DEV37, BLIND17, Verification A/B, or other protected outcomes.

## Genome
A V3 specialist contains:
1. applicability Rule(feature, standardized threshold, direction)
2. gate Rule(feature, standardized threshold, direction)
3. signal Rule(feature, standardized threshold, direction)
4. side {-1,+1}
5. lifecycle genes: take_profit, stop_loss, max_horizon, add_at, reduce_at
Ticker identity, sector label, company identity, and diagnostic winner identity are forbidden genome inputs.
Applicability/gate/signal use only the existing causal feature universe. Structural-screen thresholds remain {-1,0,+1}. Lifecycle mutation ranges remain V2 unless explicitly encoded here.

## Discovery architecture
Discovery is LOCAL by origin stock. Each of all 8 stocks is an origin independently; origin ticker is provenance only and never a genome feature.
Chronological temporal validation is mandatory. Candidate structure/lifecycle is frozen before evaluation on later time data. No validation result may mutate, rank-repair, or retune the candidate.
All 8 origins remain represented in the pipeline; validation may reject an organism but cannot remove an origin from the experiment.

## Applicability semantics
Applicability is evaluated from observable features. Entry = applicability AND gate AND signal. During cross-stock transport, the same frozen predicate determines where the organism activates. No ticker lookup is allowed.

## Fitness and minimum evidence
Discovery fitness uses event-level net return, downside/tail quality, and capital duration under existing cost semantics; portfolio CAGR/MDD and allocation metrics remain forbidden.
A candidate requires >=25 firing events in the scoring sample. Fitness is computed only on events where applicability fires.
No portfolio construction occurs in V3.

## Search
Deterministic structural screen precedes 6 generations x population 48 lifecycle evolution. Search work is identical in Real and every null arm. No Real-selected structures or feasibility/rank/archive state transfer to nulls.

## Null families
N-B remains guarded within-stock circular shift of Y, preserving Y serial structure.
N-C remains guarded within-stock circular shift of the complete multivariate X row vector, preserving cross-feature structure.
N-A V2 moving-block bootstrap is prospectively replaced by a Politis-Romano stationary bootstrap of Y with expected block length 50. It preserves local serial dependence stochastically while breaking X/Y temporal alignment. Exact implementation is frozen in code and tested before inference.
All null transformations occur before the complete discovery/temporal-validation pipeline; each null reruns the entire adaptive search independently.

## Replicates and inference
25 paired Real/null replicates remain the base inferential count for N-B and N-C.
The stationary-bootstrap N-A replacement uses 25 paired replicates initially because it is a new lower-variance implementation; no replicate count may be increased after observing V3 results.
Endpoint: final machine-defined promoted-candidate score produced by the frozen V3 pipeline, identical across Real/null arms.
Per-null test: one-sided paired Wilcoxon Real > Null.
Family alpha .05; Bonferroni per-null alpha .016666666666666666.
PASS requires >=2 of 3 null families significant. 3/3 = strong pass. <=1/3 = fail.
A near miss is a fail. Alpha cannot move.

## Pre-inference planted validation
Before any V3 Real/null inference, MTS must run a heterogeneous planted validation with signal present in 3/8 synthetic stocks and absent in 5/8. The V3 pipeline must recover a valid feature-defined specialist with active-stock mean event return >= +2.5%, while not using ticker identity. Failure stops and prohibits V3 inference.

## Transport
Transport is not authorized merely by passing the V3 null gate. After a >=2/3 gate pass, frozen candidates proceed to a separately frozen transport protocol using permitted held-out material. Candidate genome/lifecycle/applicability cannot change during transport.
A V3 gate failure invokes the frozen stopping rules; no protected transport data are opened.

## Cumulative stopping budget
V1 and V2 are consumed inferential gates. V3 is gate 3. At most one further inferential redesign (V4) is allowed, and only if the previously frozen stopping rule authorizes it based on a specific mechanistic failure. V4 failure retires this feature/genome/fitness research line.

## Automation invariants
- MTS result artifacts authorize every transition.
- Assistant/operator cannot manually promote.
- Missing/incomplete/invalid result => STOP_FAIL_CLOSED.
- No protected data before the appropriate MTS authorization.
- No large discovery before planted validation and V3 inferential gate authorization.
- Every transition is written to the controller ledger.
