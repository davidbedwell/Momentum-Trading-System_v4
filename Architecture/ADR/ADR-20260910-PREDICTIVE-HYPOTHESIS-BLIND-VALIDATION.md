# ADR — Predictive Hypothesis Blind Validation Lifecycle

Date: 2026-09-10
Status: Approved; lifecycle bookkeeping implemented

## Decision

MTS v4 distinguishes exploratory predictive discovery from blind predictive verification.

During EXPLORATION, the AI Research Director may use look-ahead information when scientifically appropriate to discover candidate predictive relationships. A relationship that RD judges potentially predictive is preserved as a frozen predictive hypothesis with status `TENTATIVE` pending verification without look-ahead knowledge.

The AI Research Director authors the predictive proposition, the objective success definition for an individual trial, and a scientifically appropriate positive minimum number of blind validation trials before blind testing begins. Deterministic code does not invent those scientific values.

Human governance fixes the cumulative verification threshold at:

`success_rate >= 0.60`

A predictive hypothesis remains `TENTATIVE` until its predeclared minimum required number of completed blind trials has been reached. Once that minimum is reached:

- cumulative success rate >= 0.60 => `VERIFIED`
- cumulative success rate < 0.60 => `NOT_VERIFIED`

Verification does not require 100% accuracy.

## Frozen-hypothesis rule

A predictive hypothesis is frozen when created for verification. Its statement, success definition, and predeclared minimum trial count may not be revised after blind validation begins.

If later evidence motivates a materially different proposition, RD creates a new hypothesis identity with a fresh validation record. Prior trials are not transferred to the revised hypothesis.

## Two-stage blind-trial rule

A valid blind trial has two distinct stages.

### 1. Prediction lock

Qwen first evaluates the market state without look-ahead knowledge and makes the prediction. The Analysis result used to inform that prediction must belong to the `VALIDATION` research phase and its durable future-information lineage must report no future information.

The prediction is then durably locked with a unique trial identity before any subsequent outcome is exposed. The lock preserves the exact prediction Qwen made for that trial.

### 2. Outcome evaluation

Only after the prediction is locked may subsequent/future information be exposed to evaluate what actually happened. Outcome Analysis may therefore contain future information; that does not contaminate the already-locked prediction.

Qwen judges whether the observed outcome satisfies the hypothesis's frozen success definition. Deterministic persistence records the success/failure judgment, counts only completed locked trials, calculates cumulative successes/failures/success rate, and applies the human-approved 0.60 status rule.

Exploratory results, including results that use look-ahead, may motivate or support creation of a tentative hypothesis but do not themselves count as blind predictions.

## Historical holdout requirement

The lifecycle bookkeeping above does not by itself create a historical blind-data boundary. For historical repeated validation, the execution layer must supply Qwen and Analysis only information available at the selected prediction point until the prediction has been locked. The hidden future may then be released solely for outcome evaluation.

A historical trial must not be counted as genuinely blind merely because its Analysis method is labeled `VALIDATION`; the evidence presented at prediction time must also be objectively withheld beyond the prediction point. That holdout/masking execution mechanism is a separate mechanical capability that must be present before historical blind trials can support production `VERIFIED` status.

## Nexus representation

The Research Package carries the live cumulative predictive-hypothesis record and trial ledger.

If RD judges a tentative predictive relationship significant enough for Nexus promotion, the promoted finding should identify the predictive hypothesis and mark its predictive status as `TENTATIVE`. A later blind-validation outcome may be promoted as a new significant finding with `VERIFIED` or `NOT_VERIFIED` status. The original tentative finding is not rewritten.

This preserves the difference between discovery and verification while retaining immutable scientific history.

## Authority boundary

RD remains the scientific authority. RD chooses what relationship is worth hypothesizing, what the hypothesis says, how success is scientifically defined, the minimum blind trial count, trial design, the exact trial prediction, interpretation, and whether findings are significant enough for Nexus promotion.

Deterministic code enforces only approved bookkeeping and objective validation boundaries: stable identities, frozen hypothesis definitions, prediction-lock-before-outcome ordering, VALIDATION-phase/no-future-information requirements for the prediction lock, trial uniqueness, arithmetic counts/rates, and the approved `>= 0.60` verification threshold.
