# MTS v4 — Integrated Regime Architecture Pre-Test Freeze — 2026-10-04

## Status

**FROZEN RESEARCH SEQUENCE AND GOVERNANCE BEFORE INTEGRATED 50→17 TEST.**

This document freezes the architecture, dependency order, evidence boundaries, and validation ladder for the next major MTS experiment. It does **not** freeze unfinished A/B/C rules, the final R-1 rule, the final defensive trading policy, or the final choice among previously discovered NORMAL-MTS chromosomes. Those objects must be frozen separately before the integrated replay begins.

## Scientific objective

Test whether a causally defined, market-regime-aware MTS can improve the return/drawdown tradeoff by combining:

1. previously discovered and previously heldout-tested NORMAL-MTS GA chromosomes,
2. independent market-wide deterioration logic that can move the system from NORMAL to DEFENSIVE,
3. a distinct opportunistic DEFENSIVE trading policy discovered only inside already-consumed development evidence,
4. an independent graded recovery process,
5. an R-1 declaration that returns the system to NORMAL operation.

The integrated test asks whether the **whole state machine** improves wealth growth and/or drawdown without destroying ordinary MTS alpha.

## Architectural invariant

```
NORMAL
  |
  | independent market-wide deterioration evidence
  | A OR B OR C
  v
DEFENSIVE
  |
  | frozen defensive opportunistic policy may trade
  | while market state remains DEFENSIVE
  v
RECOVERY EVIDENCE ACCUMULATES
  |
  | market-wide recovery evidence sets permitted exposure ceiling
  | individual MTS signals allocate only within that ceiling
  v
R-1
  |
  | independent recovery declaration
  v
NORMAL
```

A/B/C and R-series logic are market-wide scientific objects. Stock-level portfolio outcomes may evaluate the consequences of those state declarations, but may not redefine them.

## Independent deterioration paths

A/B/C are parallel pathways, not votes that must all agree.

### Path A — fast/systemic deterioration

Purpose: detect rapid systemic shock morphology using the surviving multi-market / dual-detector research.

Candidate evidence families include rapid drawdown/shock velocity, realized volatility, VIX/VVIX, breadth collapse, and funding/credit stress.

**Required before integrated testing:** recover the exact original causal rule or, if no complete original rule survived, reconstruct it explicitly and label it reconstructed. No portfolio-performance tuning may be used to choose or alter Path A.

### Path B — slow-bear deterioration

Purpose: identify slower destructive deterioration that may precede traditional MA confirmation.

The surviving frozen Path-B research uses breadth/internal damage, failed rebounds, negative-day persistence, and lagged funding/credit deterioration, with rolling historical causal percentiles and leave-one-positive-out style validation.

**Required before integrated testing:** determine the final Path-B declaration rule from surviving original reports/protocols and freeze its causal implementation without portfolio-performance tuning.

### Path C — grinding/internal deterioration

The surviving frozen Group-C candidate is:

- features: `negfrac20 + failed30 + negfrac40 + fundingchg30`
- each feature >= causal rolling historical 90th percentile
- 4 of 4 confluence
- 3-session confirmation
- OFR Funding shifted for 2-business-day publication lag

Observed discovery behavior:
- 2022 reference peak: 2022-01-03
- declaration: 2022-01-25
- 15 trading sessions after peak
- zero false declaration episodes in evaluable non-positive history
- 2008 declaration was late, confirming this is not a universal crash rule

Path C is a grinding/persistent deterioration signature, not a general crash detector.

## Transition into DEFENSIVE

Any sufficiently validated/frozen A, B, or C path may move MTS from NORMAL to DEFENSIVE.

A deterioration declaration does **not** mean:
- a crash is certain,
- the market must remain in cash until a future bull market is obvious,
- the triggering path can determine when recovery has occurred.

On entering DEFENSIVE, normal MTS entries are suspended and normal-regime positions are handled according to the separately frozen defensive-transition policy.

## DEFENSIVE trading policy

DEFENSIVE is not synonymous with permanent cash.

The separate Defensive GA research may discover short-duration opportunistic long policies used only while the independent market state remains DEFENSIVE.

Conceptually:

```
cash
 -> short-term long opportunity
 -> defensive-origin position
 -> deterioration/reversal resumes
 -> liquidate
 -> cash
```

DEFENSIVE entries, exits, stops, holding periods, sizing, and re-entry logic may differ materially from NORMAL MTS.

The current Defensive GA work is still development work. Before integrated testing:
- the final defensive policy or small frozen candidate set must be selected using only consumed development evidence,
- no preserved-50 outcome may influence selection,
- no R-1 or NORMAL transition may be inferred from the profitability of a defensive trade,
- all strategy parameters must be frozen before the preserved 50 is replayed.

## Recovery and R-1

Recovery is independent of A/B/C.

A/B/C answer: **has sufficiently severe deterioration occurred to leave NORMAL?**

R-series research answers: **has enough independent evidence accumulated to justify restoring exposure and ultimately returning to NORMAL?**

The surviving six-recovery morphology includes:
- 2009
- 2011
- 2015/16
- 2018
- 2020
- 2022

Current recurring morphology is approximately:

```
damage
 -> price stabilization/impulse
 -> breadth expansion
 -> failed-rebound improvement
 -> short-trend repair
 -> broader persistence
 -> stress normalization
```

The order and timing vary by episode. No fixed ordering is imposed. Breadth may lead in some recoveries and lag initial price impulse in others. Stress normalization may occur later still.

**Required before integrated testing:** convert the descriptive R-1 morphology into a causal, frozen declaration/falsification rule using the six true recoveries and adversarial false-rally episodes. Future trough knowledge is prohibited.

## Graded recovery exposure

R-1 is not required to be a single all-or-nothing re-entry event.

The architecture permits graded recovery evidence:

```
market recovery evidence
 -> permitted portfolio exposure ceiling

individual MTS stock signals
 -> allocation within that ceiling
```

Exact exposure percentages are **not frozen by this document**. They may be searched only after the recovery classifier itself is scientifically frozen.

A strong stock-level opportunity cannot itself declare market recovery.

## NORMAL-MTS chromosomes

Previously discovered NORMAL-MTS GA chromosomes are separate from the Defensive GA work.

The surviving Phase-2 frozen four are:
- GROWTH
- PROTECTION_GROWTH
- TAIL_BALANCE
- INTERMEDIATE_KNEE

They were frozen before their one-time 50-stock/four-era holdout replay.

Later NORMAL-MTS GA work also survives and may contain superior candidates. Before integrated testing, the NORMAL candidate set used by the integrated architecture must be frozen from already-consumed evidence and prior legitimate heldout evidence only.

No defensive-state result may be used to retune a NORMAL chromosome unless a new research protocol explicitly authorizes that question before outcome access.

## Required causal market-state tape

Before any preserved-50 integrated portfolio replay, generate a causal daily market-state tape of the form:

```
date
NORMAL_or_DEFENSIVE
A_evidence
B_evidence
C_evidence
recovery_dimension_evidence
recovery_category
permitted_exposure_ceiling
R1_status
```

The tape must be generated from the full eligible market panel and causal external data only.

It must not use:
- the preserved 50-stock portfolio returns,
- TEST17 returns,
- future market troughs,
- future bull-market labels,
- untouched Discovery outcomes,
- Verification A/B outcomes.

Once created and audited, the tape is frozen before portfolio replay.

## Prerequisites before preserved-50 replay

The preserved 50 must remain untouched for this integrated experiment until all of the following are complete:

1. **Path A recovered/frozen.**
2. **Path B final declaration rule recovered/frozen.**
3. **Path C implementation audited against its surviving freeze.**
4. **R-1 causal declaration/falsification rule frozen.**
5. **Graded recovery evidence representation frozen.**
6. **Defensive opportunistic policy or small candidate set frozen from consumed development evidence.**
7. **NORMAL-MTS chromosome set frozen.**
8. **Integrated transition mechanics frozen**, including treatment of live positions at NORMAL→DEFENSIVE and DEFENSIVE→NORMAL transitions.
9. **Transaction-cost and portfolio accounting assumptions frozen.**
10. **Full causal market-state tape generated and independently audited.**

No preserved-50 result may be viewed before these ten conditions are satisfied.

## Integrated test ladder

### Stage 0 — consumed development only

Use the consumed 67-stock laboratory to finish:
- defensive-policy discovery,
- implementation debugging,
- portfolio-accounting debugging,
- transition-mechanics debugging.

The 67 may not redefine market-wide A/B/C or R-1 scientific rules through portfolio-performance optimization.

### Stage 1 — preserved 50

The previously opened 50-stock bank is **preserved, not pristine**.

It may be used as the first integrated architecture replay only after the architecture is fully frozen.

Its role is:
- falsification,
- transport assessment,
- regime-by-regime consequence testing,
- comparison with prior NORMAL-only MTS.

It is **not** to be described as fresh blind validation.

No architecture parameter may be changed because of Stage-1 results and then retested on the same 50 as though still held out.

### Stage 2 — TEST17

TEST17 is already consumed and therefore is also diagnostic/falsification evidence, not fresh blind validation.

Run the same pre-frozen integrated architecture unchanged.

The 17 may answer whether the Stage-1 behavior transports to a second already-consumed security set.

### Advancement gate after 50 + 17

Proceed to fresh untouched Discovery only if the architecture demonstrates a scientifically credible positive result across the preserved 50 and TEST17.

The advancement decision must consider at minimum:
- terminal wealth / CAGR,
- maximum drawdown,
- CVaR / tail behavior,
- worst episode,
- normal-market alpha retention,
- defensive-market capital preservation,
- contribution of defensive opportunistic trades,
- contribution of graded recovery,
- turnover and trading costs,
- sensitivity to individual eras and securities.

No single aggregate metric may override catastrophic or highly concentrated failure.

Exact numerical advancement thresholds must be frozen before Stage 1 if they are to be hard gates.

### Stage 3 — genuinely untouched 50 from remaining Discovery

If Stages 1 and 2 justify advancement:

1. select 50 genuinely untouched Discovery securities,
2. use a pre-frozen performance-independent selection rule,
3. permanently record the identities before outcome access,
4. run the already-frozen integrated architecture once,
5. record all outcomes permanently,
6. treat those 50 as consumed thereafter.

This is the first genuinely unseen security-level validation of the integrated regime-aware architecture.

### Stage 4 — Verification A/B

Verification A and B remain protected during the above sequence.

No Verification access is authorized by this freeze.

Any later Verification test requires a separate protocol and a strategy frozen before Verification access.

## Comparison arms for the integrated experiment

At minimum, the integrated replay should report:

1. **Canonical NORMAL-only MTS baseline**
2. **Frozen NORMAL GA chromosome(s) without regime overlay**
3. **A/B/C defensive transition + cash-only DEFENSIVE + R-1 recovery**
4. **A/B/C + frozen defensive opportunistic policy + R-1**
5. **A/B/C + frozen defensive policy + graded recovery exposure + R-1**

This decomposition is required so improvements can be attributed to:
- deterioration avoidance,
- defensive opportunistic trading,
- recovery timing,
- graded exposure,
- NORMAL chromosome selection.

A final combined result without these decomposition arms is insufficient.

## Primary scientific questions

The integrated test must answer:

1. Does market-wide deterioration control materially reduce destructive drawdown?
2. How much normal-market alpha is sacrificed?
3. Does a defensive opportunistic policy earn meaningful net return while remaining consistent with capital preservation?
4. Does graded recovery capture rebound upside earlier than waiting for full R-1?
5. Does the final integrated architecture improve the return/drawdown frontier rather than simply exchange one form of risk for another?
6. Are gains broad across eras and securities, or dominated by one crash/recovery episode?
7. Does the architecture remain useful after realistic costs and turnover?

## Governance prohibitions

Before the fresh untouched-50 reveal, do not:

- tune A/B/C from stock-level portfolio CAGR,
- tune R-1 from portfolio CAGR,
- let a defensive trade's success declare market recovery,
- use known historical troughs as causal features,
- use preserved-50 or TEST17 outcomes to optimize and then relabel them held out,
- use untouched Discovery names for debugging,
- access Verification A/B,
- silently replace missing originals with reconstructions,
- describe a reconstructed rule as an original frozen rule,
- optimize the full integrated architecture directly on the preserved 50.

## Reconstruction labeling

Each integrated component must carry provenance:

- **ORIGINAL_RECOVERED**
- **ORIGINAL_RECOVERED_AND_REIMPLEMENTED**
- **RECONSTRUCTED_FROM_SURVIVING_SPEC**
- **NEW_RESEARCH_POST_RECOVERY**

The final integrated report must identify the provenance of every state transition and trading-policy component.

## Immediate execution order

The required order from this checkpoint is:

1. recover/finalize Path A,
2. recover/finalize Path B and audit Path C,
3. complete causal R-1 falsification across six true recoveries plus adversarial false rallies,
4. freeze graded recovery evidence representation,
5. complete/freeze Defensive GA opportunistic policy,
6. select/freeze NORMAL-MTS chromosome set,
7. freeze transition mechanics and accounting,
8. generate and audit causal full-market state tape,
9. freeze integrated test protocol and numerical advancement gates,
10. run preserved 50,
11. run TEST17 unchanged,
12. if justified, preselect and reveal a genuinely untouched 50-stock Discovery validation set.

## Frozen conclusion

**The integrated 50→17 experiment is the next major MTS experiment, but it must not begin until the market-state, recovery, defensive-policy, NORMAL-policy, transition, and accounting prerequisites above are frozen.**

The preserved 50 and TEST17 are falsification/transport stages. A subsequently selected 50-stock set from untouched Discovery is the first fresh security-level validation stage. Verification A/B remain protected.
