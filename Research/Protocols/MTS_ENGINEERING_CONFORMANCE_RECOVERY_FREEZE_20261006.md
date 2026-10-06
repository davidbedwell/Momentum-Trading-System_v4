# MTS ENGINEERING CONFORMANCE & RECOVERY FREEZE — 2026-10-06

**Status:** USER APPROVED / CONTROLLING
**Owner:** David E. Bedwell
**Applies to:** Momentum Trading System v4 and all successor MTS engineering/research work unless explicitly superseded by David E. Bedwell.
**Reason:** Critical repeated engineering/scientific-governance failures, including two major incidents within approximately 24 hours, culminating in the nonconforming DEV117 GA experiment.

## 1. Controlling Principle

**Claims of conformance do not count; executable evidence does.**

ChatGPT may exercise engineering autonomy only when the implementation preserves the frozen scientific design exactly. If an approved scientific mechanism cannot be implemented faithfully, or if implementation requires a material approximation, substitution, simplification, threshold change, data-governance change, or scientific redesign, work MUST STOP BEFORE MATERIAL COMPUTE and the discrepancy MUST be presented to David E. Bedwell for approval.

No silent scientific substitution is permitted.

## 2. Required Engineering Sequence

All material MTS simulator/GA work must follow this order:

1. SPECIFICATION — identify the controlling frozen requirements.
2. IMPLEMENTATION — implement those requirements without scientific reinterpretation.
3. BEHAVIORAL CONFORMANCE — prove the implementation using deterministic executable tests with known expected answers.
4. ADVERSARIAL SELF-AUDIT — actively search for counterexamples, transitive dependencies, leakage, semantic mismatches, and false-positive tests.
5. TRACEABILITY — produce requirement -> implementation -> behavioral test -> PASS/FAIL evidence.
6. CERTIFICATION GATE — all mandatory tests must pass before material/paid GA compute.
7. COMPUTE — only after certification may expensive evolutionary/search experiments begin.

No tests -> no simulator certification.
No simulator certification -> no GA.
No conformance evidence -> no claim that the approved experiment was run.

## 3. Verification Standard

Behavioral tests MUST verify actual semantics, not merely:
- presence of strings;
- function names;
- variable names;
- constants;
- source-code patterns;
- successful compilation;
- process completion;
- plausible metrics.

Whenever practical, tests must use small hand-computable numerical fixtures.

Examples of mandatory evidence include:
- partial resize actually changes a 60% position toward a permitted 30% target;
- REPLACE actually transfers capital from an incumbent to a higher-value challenger under the frozen inequality;
- weak absolute opportunity leaves residual capital in SAFE;
- changing Blind37 data cannot alter Train80 features or decisions;
- changing future data cannot alter decisions at or before T.

## 4. Minimum Mandatory Conformance Coverage

Before a simulator is certified for expensive GA compute, executable tests must cover at minimum:

1. Train80 feature isolation.
2. Blind37 independent feature reconstruction.
3. Protected-data denial/isolation.
4. Point-in-time causality.
5. Absolute-opportunity behavior.
6. SAFE competition.
7. Weak-opportunity underinvestment.
8. ENTER semantics.
9. CONTINUE semantics.
10. Partial resizing.
11. Full EXIT_TO_SAFE.
12. Genuine incumbent-to-challenger REPLACE.
13. SHORT entry.
14. SHORT covering.
15. Friction hurdles.
16. Uncertainty hurdles.
17. Immediate re-entry eligibility.
18. Gross exposure <= 1.
19. Exactly the four approved allocation modes.
20. Execution timing.
21. Transaction-cost accounting.
22. Borrow-cost accounting.
23. No position-age dependence.
24. No entry-price/date dependence.
25. No cooldown or fixed holding period.
26. Deterministic reproducibility.
27. Matched null calibration.
28. Planted-signal recovery.
29. Train/blind freeze barrier.
30. Exact provenance and permitted-universe scope of every input dataset.

## 5. Partition and Data Governance

There must never be an all-universe feature tensor followed by partition slicing when the scientific design requires partition-local feature construction.

For every fold:
- Train80 cross-sectional transforms use Train80 only.
- Train80 dynamic peers use Train80 only.
- Train80 online calibration uses Train80 only.
- Blind37 replay reconstructs cross-sectional transforms using Blind37 only.
- Blind37 dynamic peers use Blind37 only.
- Blind37 online calibration uses Blind37 only where the frozen design permits it.
- Protected cohorts must not be loaded, aggregated, ranked, used as peers, or otherwise influence features unless David explicitly authorizes that use.

Market-context sources must have explicit provenance and must not acquire protected/research-universe information through hidden aggregation.

## 6. Lifecycle and Allocation Governance

The approved lifecycle must be implemented literally as a unified economic source-to-destination capital movement system where required by the controlling scientific specification.

ENTER, CONTINUE/resize, REPLACE, EXIT_TO_SAFE, SHORT, and cover must have their defined economic meanings.

Absolute claims must preserve the approved SAFE competition semantics. Weak opportunity must be capable of leaving substantial capital in SAFE. Risky claims must not be silently normalized upward merely because some opportunity exists.

Any proposed change to these semantics is a scientific change and requires David's explicit approval before implementation or compute.

## 7. External Model Review

A paid external-model audit (Astra, Claude, or another model) is **NOT required** for MTS engineering certification.

David is not required to pay an additional AI-service fee to verify that ChatGPT followed the approved specification.

External review is optional and occurs only when David explicitly requests it.

Mandatory conformance certification must be achievable through deterministic behavioral testing, traceability, adversarial self-audit, and inexpensive/local engineering verification.

## 8. Existing Nonconforming Experiment

The 2026-10-05/06 redesigned DEV117 GA experiment and its runner/results are frozen as:

**FORENSIC / NONCONFORMING / INVALID FOR SCIENTIFIC CONCLUSION**

They must not be silently repaired in place, treated as evidence that the approved MTS architecture succeeded or failed, or used to justify scientific conclusions that depend on the intended architecture having actually been executed.

The defective artifacts must remain preserved for incident reconstruction.

## 9. Engineering Accountability

ChatGPT must not ask David to compensate for engineering uncertainty by:
- manually auditing code he delegated because he lacks engineering expertise;
- babysitting routine processes;
- paying for an external model by default;
- accepting undocumented approximations;
- accepting successful execution as evidence of correctness.

If a process fails for an ordinary engineering reason, ChatGPT should diagnose and repair it autonomously while preserving the frozen science.

If the problem requires changing the science, governance, protected-data policy, or material experimental design, ChatGPT must stop and ask David.

## 10. Handoff Report Requirement — MANDATORY

**EVERY future MTS handoff report must include this freeze as a controlling authority.**

Every MTS handoff must contain a clearly visible section titled:

### MANDATORY ENGINEERING CONFORMANCE GOVERNANCE

That section must state, at minimum:

- `MTS_ENGINEERING_CONFORMANCE_RECOVERY_FREEZE_20261006.md` is USER APPROVED / CONTROLLING.
- Claims of conformance do not count; executable evidence does.
- Scientific requirements may not be silently simplified, substituted, approximated, or redesigned.
- Required sequence: specification -> implementation -> behavioral conformance -> adversarial self-audit -> traceability -> certification -> compute.
- No simulator certification means no expensive GA.
- Protected/train/blind universe isolation must be proven behaviorally.
- Paid Astra/Claude/external review is optional only; it is not a required certification cost.
- If faithful implementation is impossible or materially ambiguous, STOP BEFORE COMPUTE and ask David.
- The 2026-10-05/06 DEV117 GA is FORENSIC/NONCONFORMING and cannot support scientific conclusions about the approved architecture.

A handoff that omits this governance block is itself incomplete/nonconforming.

## 11. Supersession

This freeze remains controlling until David E. Bedwell explicitly changes or supersedes it.

ChatGPT may not infer supersession from later implementation choices, code changes, experiments, convenience, cost, or elapsed time.
