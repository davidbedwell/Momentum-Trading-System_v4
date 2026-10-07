

# COLD RE-AUDIT — MTS G3 Production Specialist Discovery Protocol + Amendment A

**Auditor posture:** Scientific validity and executable specificity only. The user governance constraint (second consecutive plateau → freeze island, reallocate compute only; no replacement islands, no population/budget/objective/config changes) is respected as given. I am looking for defects that would invalidate freezing/implementing this protocol as written.

---

## BLOCKER ISSUES

**None identified.**

The protocol is internally consistent, scientifically conservative, and executable as specified. No single defect would invalidate the experiment if implemented faithfully.

---

## MAJOR ISSUES

### MAJOR-1: "Second consecutive plateau" has no operational definition

The protocol and amendment repeatedly reference freezing an island upon its "second consecutive plateau" but never define what constitutes a plateau. Without a deterministic, pre-frozen definition, this becomes a discretionary decision during a live run — which is exactly the kind of mid-run judgment the protocol otherwise eliminates.

**Required fix:** Before freeze, specify: (a) the metric monitored (e.g., archive promotions per generation, hypervolume of island Pareto front, best-rank improvement count), (b) the window length that constitutes one plateau period (e.g., N consecutive generations with zero change), (c) the threshold for "no improvement" (exact zero? epsilon?), and (d) confirmation that the second consecutive such window triggers the freeze. All parameters must be frozen before launch.

**Why MAJOR not BLOCKER:** The concept is clear and the governance rule is unambiguous in intent; only the triggering measurement is unspecified. A one-paragraph operational definition resolves it without any structural redesign.

---

### MAJOR-2: Migration from a frozen island is unspecified

When an island is frozen, the protocol says freed *compute* is reallocated. But the migration mechanism (every 20 generations, behaviorally novel genomes move between islands) does not address whether: (a) a frozen island can still *donate* migrants from its final population to active islands at migration checkpoints, or (b) active islands can attempt to *send* migrants to the frozen island (which would be meaningless since it performs no evaluation). Omitting this creates ambiguity about whether frozen-island genomes remain accessible to the migration graph.

**Required fix:** State explicitly: frozen islands neither send nor receive migrants (cleanest), OR frozen islands may donate from their terminal archive/population but never receive (also defensible). Either is fine; silence is not.

---

### MAJOR-3: Internal temporal confirmation (final 20%) lacks a failure consequence

The protocol requires "positive cluster-bootstrap reward LCB on the frozen final-20% internal temporal confirmation" for promotion. But it does not state what happens if a candidate that passed all discovery-interval criteria fails this temporal confirmation. Presumably it does not promote — but the protocol should say so explicitly, and clarify whether such a candidate can remain in the museum/novelty archive (where it presumably can, since those have no validity claim).

**Required fix:** Add: "A candidate that fails internal temporal confirmation is demoted from CANDIDATE to museum-eligible only and may not enter the promoted QD archive. No repair, re-evolution, or threshold adjustment is permitted."

---

### MAJOR-4: Null-run max-statistic threshold application is ambiguous when null promotes zero candidates

The protocol says: "if the null produces no promotable candidate, its maximum contender LCB is used." But "contender" is not a defined status tier. The protocol defines CANDIDATE (promoted) and archive membership, but the population of organisms that *attempted* promotion without succeeding is unbounded and noisy. Using the max LCB of all organisms that ever entered the archive pipeline could be extremely conservative or extremely noisy depending on implementation.

**Required fix:** Define "contender" precisely — e.g., "any organism that satisfied all promotion criteria except the reward-LCB positivity test" or "the top organism per CVT cell by reward-LCB that met the event-count and cluster-count floors." Then confirm: production REAL candidates must have reward-LCB strictly exceeding this null threshold.

---

## MINOR ISSUES

### MINOR-1: 60-session embargo direction is ambiguous
The "60-session embargo separates discovery and temporal-confirmation evaluation." It should clarify whether this is a 60-session gap *excluded from both intervals* or simply a minimum separation between the last discovery date and the first confirmation date. If excluded, the effective data used shrinks and the partition percentages (20/60/20) no longer sum to 100% of the panel's date range.

### MINOR-2: Checkpoint retention may be insufficient for audit
"Every 10th checkpoint plus last 3 consecutive" means that if a crash occurs at generation 87, the auditable trail has checkpoints at 10, 20, 30, 40, 50, 60, 70, 80, 85, 86, 87. This is adequate, but the protocol says "checkpoint every generation" — the retention policy should clarify that non-retained checkpoints are deleted only *after* the next retained checkpoint is verified, to prevent data loss on write failure.

### MINOR-3: Cross-island duplicate merge timing
Merging when descriptor distance ≤0.01 and Jaccard ≥0.95 is specified but the *timing* is not: is this checked at migration, at archive insertion, at end-of-run, or continuously? Continuous checking is expensive; end-of-run is cheapest but allows duplicates to consume archive slots during evolution.

### MINOR-4: "Positive point mean at 10 bps in at least 2/3 thirds" — denominator clarity
With three chronological thirds, 2/3 means two of three. This is clear, but the protocol should confirm this is evaluated per-candidate on discovery data only (not including the temporal-confirmation 20%), which appears to be the intent but could be read otherwise.

### MINOR-5: Pre-launch benchmark scope
The protocol requires "exact one-generation benchmark" for timing, and the amendment requires ≥80% CPU utilization. It does not specify whether this benchmark uses the real discovery data or synthetic data. If real data, it partially exposes the production pipeline to outcomes before authorization; if synthetic, utilization may differ. Recommend: benchmark on the descriptor-development 20% partition (already exposed, no new leakage).

### MINOR-6: Perturbation case count can be large and is not budgeted
One-at-a-time ±10% on all numeric parameters across 2–8 modules could produce 60–200+ perturbation cases per candidate. With up to 1,024 promoted candidates, this is 60K–200K+ additional evaluations. This is feasible but should be included in the compute-feasibility benchmark projection.

---

## SUMMARY

| Severity | Count | IDs |
|----------|-------|-----|
| BLOCKER | 0 | — |
| MAJOR | 4 | M1–M4 |
| MINOR | 6 | m1–m6 |

---

## FREEZE_READY: **NO**

Four MAJOR issues require resolution before the protocol can be frozen for implementation. All four are addressable with short, precise textual additions (no structural redesign needed). Once resolved:

- MAJOR-1: Add operational plateau definition (~1 paragraph)
- MAJOR-2: Add frozen-island migration rule (~2 sentences)
- MAJOR-3: Add temporal-confirmation failure consequence (~2 sentences)
- MAJOR-4: Define "contender" for null-threshold computation (~1 paragraph)

After these four additions, with no other changes, the protocol would be FREEZE_READY from a scientific-validity and executable-specificity standpoint.
