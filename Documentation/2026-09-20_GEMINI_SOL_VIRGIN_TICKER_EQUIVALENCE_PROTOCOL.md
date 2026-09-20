# MTS V4 Gemini–Sol Virgin-Ticker Equivalence Protocol

Date: 2026-09-20
Base commit: `3347c4a8c71487ed37a4311d9928a32fdb3e428d`
Status: FROZEN EXPERIMENT GOVERNANCE

## Purpose

Determine whether Gemini can serve as the MTS Research Director with a bounded Sol appeal while preserving the scientific output of the frozen successful direct-Sol workflow at materially lower model cost.

This experiment evaluates replacement economics and scientific equivalence. It does not authorize weakening MTS to accommodate Gemini.

## Non-negotiable test design

1. Deterministically select and freeze three genuinely virgin DISCOVERY tickers.
2. Give both arms identical evidence, Analysis methods, research question, and starting state.
3. Arm A — Direct Sol: direct Sol research using the frozen successful workflow.
4. Arm B — Hybrid: Gemini operates as Research Director. After Gemini completes its research cycle, Sol receives the full underlying evidence, every Analysis result generated in the hybrid arm, and Gemini's complete work product for a bounded scientific appeal. Sol is not restricted to Gemini's conclusions.
5. Neither arm may see the other arm's results before both arms for that ticker are complete and cryptographically frozen.
6. Final comparison is blinded and evaluates: materially missed research lines; false or unsupported promotions; substantive findings; direction; horizon; robustness; trading conclusion; and actual model cost.
7. Gemini+Sol qualifies only if all three tickers are materially equivalent to Direct Sol AND aggregate hybrid model cost is at least 35 percent lower than aggregate Direct-Sol model cost.
8. Automatic failure: any material Direct-Sol finding that the hybrid fails to recover fails qualification regardless of cost.

## Scientific invariants

- No MTS scientific standard, evidence requirement, promotion standard, research autonomy, Analysis capability, validation rule, or execution contract may be weakened or changed to improve Gemini performance.
- Both arms start from the exact same immutable per-ticker starting package. The package must be serialized canonically and SHA-256 hashed before either arm starts.
- Both arms have the same available evidence descriptors, Analysis methods, research mission/question, subject metadata, market context, earnings context, and other governed starting state.
- Evidence-source availability is symmetric. FINRA is not reserved to Sol. Unusual Whales is not required for this experiment and must not be silently reintroduced as an asymmetric dependency.
- Arm A uses the already successful frozen direct-Sol workflow; the experiment harness must wrap it rather than alter its scientific behavior.
- Arm B must permit Gemini the same research autonomy and Analysis capabilities available to Direct Sol.
- Sol appeal receives raw/full governed context: starting evidence, Analysis results produced in Arm B, Gemini decisions/work product, and the same available methods. The appeal must not be reduced to reviewing a Gemini summary.
- The Sol appeal is bounded so it cannot silently become a second unrestricted Direct-Sol run. Its purpose is to challenge, repair, reject, recover omissions visible from the full hybrid record, and adjudicate Gemini's work. Appeal bounds and actual Sol calls/tokens/cost must be recorded.
- Candidate/model outputs are evidence for adjudication, never self-validating truth.

## Virgin ticker eligibility

A ticker is eligible only when all of the following are machine-verifiable:

- partition is DISCOVERY;
- no prior Sol scientific exposure exists in governed exposure state;
- no prior Gemini scientific exposure exists for this experiment;
- no completed or partial prior research campaign/artifact makes the ticker non-virgin under existing MTS governance;
- required frozen starting data are available for both arms.

Selection must be deterministic from the eligible set. The selector must record: eligible-set hash, deterministic selection rule/seed material, selected ticker symbols/IDs, partition evidence, exposure checks, and a freeze-manifest hash. If virginity cannot be proven, fail closed and do not substitute a hand-picked ticker.

## Arm isolation

Create separate immutable roots for `DIRECT_SOL` and `GEMINI_SOL_HYBRID`. No decision, result, continuation summary, finding, promotion, cost telemetry, or artifact from one arm may enter the other arm's context before both are frozen. Shared input is allowed only through the pre-arm frozen starting package.

## Hybrid appeal boundary

The bounded Sol appeal must receive the complete hybrid scientific record. It may:

- challenge Gemini's reasoning;
- identify omitted research lines evident from the supplied evidence/results;
- reject unsupported findings/promotions;
- reinterpret Analysis results;
- request bounded corrective Analysis when necessary to adjudicate a suspected material omission;
- affirm, revise, replace, or close Gemini conclusions within the appeal scope.

The appeal may not simply discard Gemini and restart the unrestricted Direct-Sol workflow from scratch. The harness must record every appeal request and distinguish review/repair calls from newly requested corrective Analysis.

## Freeze artifacts

For each ticker, freeze and hash at minimum:

- starting package;
- Arm A complete decision/research/result stream;
- Arm B Gemini complete decision/research/result stream;
- Arm B Sol appeal stream;
- final Arm A scientific output;
- final Arm B scientific output;
- provider usage telemetry and actual model cost by model/call;
- arm completion manifest.

Comparison begins only after both arm completion manifests exist and their hashes are recorded.

## Blinded comparison

The comparison input must use neutral labels (for example `ARM_X` and `ARM_Y`) and must not disclose provider/model identity or cost until scientific comparison is frozen.

For each ticker the comparator must explicitly assess:

1. material research lines present in one arm and absent in the other;
2. false or unsupported promotions;
3. substantive findings and whether each material finding is recovered;
4. direction;
5. horizon;
6. robustness and important caveats;
7. trading conclusion/actionability;
8. material scientific disagreements.

Only after the scientific comparison is frozen may the harness reveal arm identity and calculate cost qualification.

## Qualification rule

Let `direct_cost` be aggregate actual model cost for Direct Sol across all three tickers. Let `hybrid_cost` be aggregate actual model cost for Gemini plus bounded Sol appeal across all three tickers.

Cost saving fraction = `(direct_cost - hybrid_cost) / direct_cost`.

Qualification requires ALL of:

- exactly three frozen eligible virgin DISCOVERY tickers completed in both arms;
- no isolation breach;
- no starting-package mismatch;
- no material Direct-Sol finding missed by the hybrid on any ticker;
- each ticker judged materially equivalent on the frozen scientific comparison dimensions;
- no disqualifying false/unsupported hybrid promotion;
- aggregate cost saving fraction >= 0.35.

Any material Direct-Sol finding missed by the hybrid is an automatic overall FAIL. No averaging across tickers may erase that failure.

## Fail-closed conditions

Abort or mark the experiment invalid rather than infer success when: virginity cannot be proven; starting hashes differ; an arm sees the other arm; usage/cost telemetry is missing; a required evidence/method capability differs between arms; the Direct-Sol workflow is modified for the experiment; the Gemini path is given reduced evidence or Analysis capability; the Sol appeal is denied the full hybrid record; or the comparator is unblinded before scientific judgment is frozen.

## Relationship to five-control ladder

The existing OpenRouter five-control ladder remains a prequalification/capability test. Passing it does not qualify Gemini to replace Direct Sol. This three-ticker virgin equivalence experiment is the replacement qualification gate.
