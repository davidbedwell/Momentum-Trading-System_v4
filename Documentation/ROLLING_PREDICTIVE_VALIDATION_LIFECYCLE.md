# Rolling Predictive Validation Lifecycle

## Purpose

MTS v4 separates a frozen predictive hypothesis from the repeated blind trials used to evaluate it.

A hypothesis such as `AMD-H001` is one scientific object. Repeated tests do not create `H002`, `H003`, and so on. They accumulate as trial identities such as `AMD-H001-T01` through `AMD-H001-T20` under the unchanged frozen hypothesis.

## Scientific lifecycle

1. **Explore** the subject using evidence that is explicitly available for EXPLORATION.
2. When the AI Research Director judges a predictive proposition ready, **freeze one hypothesis definition**: statement, success definition, minimum trial count, and supporting result lineage.
3. Historical same-subject blind validation may use only evidence that was **mechanically sequestered before hypothesis creation** and was not exposed to the Research Director or Analysis during discovery.
4. **Lock each blind prediction before its outcome is exposed.**
5. Reveal the outcome and record it against the existing trial.
6. Repeat until the hypothesis reaches its predeclared validation decision boundary.
7. Once a blind tranche has been revealed, mark it **EXPOSED**. It remains durable audit evidence but can never again count as blind evidence for that frozen hypothesis version.
8. **Resume unrestricted exploration** on later eligible subject data. Validation pauses the exploration frontier; it does not retire the subject.
9. A materially revised proposition receives a new hypothesis ID and a new validation record.
10. Only when no eligible unexposed same-subject observations remain should the program wait for genuinely future subject observations or an eligible external unseen subject.

## Identity rule

- Hypothesis identity: `AMD-H001`
- Validation trial identities: `AMD-H001-T01`, `AMD-H001-T02`, ...
- Trial repetition does not imply hypothesis revision.

## Exposure rule

The validation frontier has three mechanical states:

- `SEALED`: reserved evidence that has not been exposed to scientific reasoning.
- `LOCKED_FOR_VALIDATION`: assigned to a frozen hypothesis and its predeclared blind trials; outcomes remain protected until prediction lock.
- `EXPOSED`: outcomes have been revealed. The data may contribute to later exploration but permanently lose blind status for that hypothesis version.

Deterministic code enforces identity, non-overlap, exposure state, and temporal/provenance integrity. It does not choose the hypothesis, scientific window, threshold, horizon, predictor, method, interpretation, or whether a scientific relationship is worth pursuing.

## Research Package provenance

A predictive hypothesis may need a different durable scientific home than the Research Package in which a historical implementation defect placed it. Provenance repair is permitted only when it is mechanically exact and preserves the frozen hypothesis byte-for-byte at the scientific-definition level. The repair must retain an audit transition on both source and target Research Packages and must never alter the statement, success definition, source result IDs, validation history, counts, or status.

## AMD-H001

The recovered AMD campaign exposed an RP semantic-drift defect: `AMD-H001` was persisted under the historically dark-pool-originating `RP-AMD-002` even though the hypothesis is a price-location proposition. The approved repair is to relocate the frozen hypothesis to a dedicated price-location validation RP descended from the broad price-location discovery lineage, while preserving the original RP and its originating question. This is a provenance correction only; it does not change the scientific claim or its evidence.
