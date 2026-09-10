# ADR — Predictive Hypothesis Blind Validation Lifecycle

Date: 2026-09-10
Status: Approved and implemented

## Decision

MTS v4 distinguishes exploratory predictive discovery from blind predictive verification.

During EXPLORATION, the AI Research Director may use look-ahead information when scientifically appropriate to discover candidate predictive relationships. A relationship that RD judges potentially predictive is preserved as a frozen predictive hypothesis with status `TENTATIVE` pending verification without look-ahead knowledge.

The AI Research Director authors the predictive proposition, the objective success definition for an individual trial, and a scientifically appropriate positive minimum number of blind validation trials before blind testing begins. Deterministic code does not invent those scientific values.

Human governance fixes the cumulative verification threshold at:

`success_rate >= 0.60`

A predictive hypothesis remains `TENTATIVE` until its predeclared minimum required number of valid blind trials has been completed. Once that minimum is reached:

- cumulative success rate >= 0.60 => `VERIFIED`
- cumulative success rate < 0.60 => `NOT_VERIFIED`

Verification does not require 100% accuracy.

## Frozen-hypothesis rule

A predictive hypothesis is frozen when created for verification. Its statement, success definition, and predeclared minimum trial count may not be revised after blind validation begins.

If later evidence motivates a materially different proposition, RD creates a new hypothesis identity with a fresh validation record. Prior trials are not transferred to the revised hypothesis.

## Blind-trial rule

A trial may count toward predictive verification only when it belongs to the `VALIDATION` research phase and its durable Analysis future-information lineage reports no future information.

Exploratory results, including results that use look-ahead, may motivate or support creation of a tentative hypothesis but do not count as blind verification trials.

The AI Research Director judges whether an individual blind trial satisfies the frozen success definition. Deterministic persistence records that judgment, validates the trial's objective phase and future-information lineage, calculates cumulative successes/failures/success rate, and applies the human-approved 0.60 status rule.

## Nexus representation

The Research Package carries the live cumulative predictive-hypothesis record and trial ledger.

If RD judges a tentative predictive relationship significant enough for Nexus promotion, the promoted finding should identify the predictive hypothesis and mark its predictive status as `TENTATIVE`. A later blind-validation outcome may be promoted as a new significant finding with `VERIFIED` or `NOT_VERIFIED` status. The original tentative finding is not rewritten.

This preserves the difference between discovery and verification while retaining immutable scientific history.

## Authority boundary

RD remains the scientific authority. RD chooses what relationship is worth hypothesizing, what the hypothesis says, how success is scientifically defined, the minimum blind trial count, trial design, interpretation, and whether findings are significant enough for Nexus promotion.

Deterministic code enforces only approved bookkeeping and objective validation boundaries: stable identities, frozen hypothesis definitions, VALIDATION-phase trial eligibility, future-information lineage, trial uniqueness, arithmetic counts/rates, and the approved `>= 0.60` verification threshold.
