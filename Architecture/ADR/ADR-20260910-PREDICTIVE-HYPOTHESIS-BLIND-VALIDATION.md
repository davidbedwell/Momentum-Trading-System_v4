# ADR — Predictive Hypothesis Blind Validation Lifecycle

Date: 2026-09-10
Status: Approved; lifecycle bookkeeping and historical blind-data boundary implemented

## Decision

MTS v4 distinguishes exploratory predictive discovery from blind predictive verification because both are necessary to the system's governing purpose.

MTS exists to discover reproducible relationships between information observable at time T and subsequent market behavior at T+1 onward. It is not primarily a descriptive market-analysis system. During EXPLORATION, the AI Research Director is therefore positively directed to seek scientifically defensible prospective relationships rather than merely being permitted to notice them.

During EXPLORATION, the AI Research Director may use historical look-ahead where scientifically useful to investigate whether present-time conditions precede or discriminate subsequent direction, magnitude, timing, continuation or reversal, path quality, or interactions among evidence streams. Descriptive and contemporaneous findings may be valuable stepping stones when they help expose predictive structure.

This encouragement is not a requirement to manufacture positive results. RD should reject unsupported candidate relationships as readily as it advances promising ones. A falsifiable predictive hypothesis that later fails verification remains useful scientific knowledge.

A relationship that RD judges potentially predictive is preserved as a frozen predictive hypothesis with status `TENTATIVE` pending verification without look-ahead knowledge.

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

## Historical blind-data boundary

Historical repeated validation uses a separate mechanical prediction sandbox.

For every evidence source admitted to a historical blind trial, the caller must provide one explicit temporal window identifying the exact evidence ID, exact time field, and inclusive prediction cutoff. Deterministic code does not select those scientific trial boundaries.

Before Qwen performs the blind prediction stage:

- every supplied evidence payload is copied into a fresh temporary cache;
- all rows later than that source's declared cutoff are physically withheld;
- the RD-visible evidence descriptor reports the masked row count and cutoff rather than the original future coverage;
- original source provenance and content identity are withheld from the prediction view so arbitrary future-derived metadata cannot leak the hidden outcome;
- a fresh in-memory Nexus is used, containing no exploratory findings or prior Analysis-result memory;
- the blind RD transport is deliberately separate from the RP-aware production provider, so exploratory RP history is not automatically injected;
- the only scientific prior carried into the blind prediction context is the already-frozen hypothesis and its success definition.

The sandbox refuses to reveal post-cutoff outcome rows until a prediction statement has been explicitly locked. Once locked, that prediction cannot be changed. The future rows can then be revealed for outcome scoring within the caller-declared outcome window.

This is an objective withholding mechanism, not a scientific selection mechanism. Qwen remains responsible for trial design, what the frozen hypothesis predicts, what evidence is scientifically relevant, and interpretation of the blind outcome.

A historical trial must not be counted as genuinely blind merely because an Analysis method is labeled `VALIDATION`; the prediction stage must use the masked cache, masked descriptors, isolated Nexus, and blind RD context described above.

The strict validation boundary must never be generalized backward into EXPLORATION. Its purpose is to protect the credibility of predictive claims discovered during exploration, not to reduce Qwen's freedom or incentive to discover those claims.

## Historical unseen-subject rule versus live prediction

Retrospective historical blind verification adds a separate subject-level integrity rule: the ticker used as the historical verification subject must not have been analyzed by MTS before that verification campaign began. Findings and tentative predictive hypotheses may come from one or many previously analyzed tickers; historical verification should then be performed against a genuinely unseen ticker.

After those historical verification results are durably recorded, that ticker may enter unrestricted EXPLORATION and its results and subsequent findings may join the cumulative research corpus. New or materially revised hypotheses arising from that enlarged corpus should be historically verified on another ticker that was unseen at the start of its verification campaign.

This unseen-subject requirement applies only to retrospective historical verification. It does not prohibit genuine live prospective predictions on familiar tickers. If the prediction point is current and the future outcome has not yet occurred, MTS may predict, trade, and later score outcomes on a ticker it has analyzed extensively before. Scientific familiarity with AAPL, XOM, or any other ticker must not make that ticker untradeable.

Accordingly, deterministic unseen-subject eligibility checks belong only in the historical replay/holdout verification path. They must not be reused as a universal gate on prospective prediction or trading.

## Nexus representation

The Research Package carries the live cumulative predictive-hypothesis record and trial ledger.

If RD judges a tentative predictive relationship significant enough for Nexus promotion, the promoted finding should identify the predictive hypothesis and mark its predictive status as `TENTATIVE`. A later blind-validation outcome may be promoted as a new significant finding with `VERIFIED` or `NOT_VERIFIED` status. The original tentative finding is not rewritten.

This preserves the difference between discovery and verification while retaining immutable scientific history.

## Authority boundary

RD remains the scientific authority. RD chooses what relationship is worth hypothesizing, what the hypothesis says, how success is scientifically defined, the minimum blind trial count, trial design, the exact trial prediction, interpretation, and whether findings are significant enough for Nexus promotion.

Deterministic code enforces only approved bookkeeping and objective validation boundaries: stable identities, frozen hypothesis definitions, prediction-lock-before-outcome ordering, historical row withholding at explicitly supplied cutoffs, historical unseen-subject eligibility, isolated prediction-stage scientific memory, VALIDATION-phase/no-future-information requirements for the prediction lock, trial uniqueness, arithmetic counts/rates, and the approved `>= 0.60` verification threshold. The historical unseen-subject gate is not a live-trading restriction.
