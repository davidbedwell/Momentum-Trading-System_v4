# MTS GA Redesign Review Packet for GPT-6 Astra
Date: 2026-10-05

## Role
You are the independent senior quantitative-research architect reviewing an MTS genetic-algorithm experiment after an implementation-governance failure.

Your job is NOT to tune the failed runner. Your job is to:
1. audit the delta between the user-approved research architecture and the runner that was actually executed;
2. distinguish research-design defects from implementation defects and from merely disappointing empirical results;
3. design the instructions that should be given to the next GA implementation so it faithfully searches the intended hypothesis space;
4. preserve scientific validity and all still-virgin evidence.

Do not assume the reported OmniFunds performance is independently validated. Treat it as a comparison case and a source of architectural questions, not as proof that similar performance must exist in MTS.

---

# 1. USER-APPROVED / FROZEN MTS GA SPECIFICATION

The frozen experiment objective was:

> Pareto-optimize long-run CAGR versus maximum drawdown while explicitly measuring crash preservation, recovery burden, and behavioral tolerability.

Evidence sequence:
- DEV117 repeated 80-discovery / 37-blind-transport folds.
- DV25 = fresh development-validation gate.
- A25 = frozen blind proof only after DV25 passes.
- Preserve A75 and B100 untouched.
- Forward outcomes/trajectories are permitted as discovery labels on each 80-stock training partition only.
- No outcome from the 37-stock transport partition may enter evolution for that fold.
- Live/replay decisions at time T use T and earlier only.
- DV25 must remain sealed during this redesign.

R1 role:
- R1 is causal market-state information, not a mandatory action or rigid ordered gate.
- Dimensions:
  1. extreme prior destruction;
  2. initial price stabilization/impulse;
  3. delayed nonlinear breadth conversion, including breadth level, velocity, and acceleration;
  4. breadth persistence / broad cross-sectional persistence;
  5. continued reduction in failed rebounds;
  6. short-trend repair;
  7. stress normalization plus recovery retention.
- Large price bounce alone is insufficient.
- Timing and ordering may vary materially across recovery episodes.
- The GA should receive the dimensions separately and may discover interactions.

Market-state role:
- A/B/C/DEFENSIVE/R1 are causal context only.
- GA may choose long, short, SAFE, reduced exposure, sector rotation, or combinations.
- Market state must not prescribe action.

APPROVED SOFT ARCHITECTURE:
> market context -> sector context -> stock state/behavior -> applicable strategy -> opportunity ranking -> capital allocation

These are soft information levels, not rigid gates.

Forbidden:
- ticker identity as predictive input;
- minimum holding period;
- maximum holding period;
- fixed holding period;
- elapsed-position-age exit;
- session cooldown;
- future-return horizon as a live input;
- slot ceiling;
- one-stock-per-sector rule;
- fixed sector cap;
- leverage;
- options.

Decision semantics:
- ENTER
- CONTINUE
- REPLACE
- EXIT_TO_SAFE
- SHORT

Allocation methods approved:
- equal;
- relative opportunity strength;
- uncertainty-adjusted opportunity strength;
- downside-adjusted opportunity strength.

SAFE:
- actual historical 3-month Treasury rate;
- causal latest-published observation only;
- forward-fill after publication;
- never future-backfill;
- SAFE competes for capital, not merely as a fallback after a hard gate.

Transaction economics:
- zero commission baseline for Webull-style equities;
- realistic spread/slippage;
- regulatory and short-borrow costs where applicable;
- finalists must be evaluated at 0, 5, 10, and 20 bps one-way sensitivities as appropriate.

Fitness:
Primary Pareto:
- maximize CAGR;
- minimize maximum drawdown.

Required diagnostics/guards:
- CVaR5;
- worst day;
- worst 5/10/20-session loss;
- drawdown velocity;
- time underwater;
- time to recovery;
- turnover;
- SAFE fraction;
- concentration;
- effective independent evidence;
- fold stability;
- era stability.

Behavioral DD bands:
10%, 15%, 20%, 25%, 30%, 35%, 40%.

Evaluation:
- four independent approximately 5-year reset eras:
  - 2006-09-15 to 2011-09-14
  - 2011-09-15 to 2016-09-14
  - 2016-09-15 to 2021-09-14
  - 2021-09-15 to 2026-09-14
- each era resets at $100,000;
- one continuous 2006-09-15 to 2026-09-14 run beginning with $100,000, with no reset.

Required decline reporting:
- MTS CAGR while broad market declining;
- MTS return during each major decline;
- actual SPY return over same interval;
- Treasury return over same interval;
- max MTS DD;
- worst day;
- long contribution;
- short contribution;
- SAFE contribution;
- time to recover prior equity high.

Evidence accounting:
- raw N;
- effective N;
- stocks;
- sectors;
- independent market episodes;
- cross-era recurrence;
- cross-stock transport;
- uncertainty.

GA design:
- staged evolutionary search;
- initial chromosome approximately 8-12 ACTIVE CONCEPTS, not a permanent limitation on architectural expressiveness;
- approximately 250 population x 200 generations as an initial compute plan, not a scientific reason to narrow the hypothesis space;
- mutation/crossover;
- duplicate cache;
- elitism;
- invalid-candidate early elimination;
- stagnation detection;
- deterministic seeds;
- complexity used only as a tie-breaker when solutions are economically indistinguishable within uncertainty.

The intended strategy universe was broad and included, without using these as rigid cages:
- momentum;
- breakout;
- trend;
- mean reversion;
- volatility;
- volume/liquidity;
- relative strength;
- earnings;
- market/regime structure;
- reversal;
- pullback;
- volatility breakout;
- composite breadth;
- sector-relative behavior;
- other relationships discovered from the allowed causal feature set.

Core horizon-free capital-allocation principle:
> Of everything I could own today, where should the next dollar of capital be allocated?

Every causal session:
- incumbents are evaluated for incremental continuing value;
- new candidates are evaluated;
- alternatives compete for finite capital;
- SAFE competes;
- replacement occurs only if the challenger has enough incremental value to overcome friction and uncertainty;
- no fixed minimum/maximum hold;
- no elapsed-holding-time score;
- no fixed exit horizon;
- duration must emerge.

No arbitrary diversification:
- no stock-count ceiling;
- no one-stock-per-sector restriction;
- no fixed max sector count;
- sector information informs opportunity/risk but does not mechanically forbid concentration;
- concentration should be measured and economically evaluated, not prohibited by arbitrary rule.

---

# 2. WHAT WAS ACTUALLY IMPLEMENTED INSTEAD

The executed runner was:
`run_horizon_free_ga_final_study_20261005.py`
SHA-256:
`0d34eea2cd8cb51fdd62cf2079fcb43d8f896464fadf462b4044208a976cfa03`
313 lines.

The implementation reduced the approved architecture substantially.

## Actual genome
The runner encoded:
- 8-12 selected feature IDs;
- one continuous weight per selected feature;
- long qualification threshold;
- Boolean short permission;
- short qualification threshold;
- replacement margin;
- SAFE margin;
- allocation choice from ONLY:
  - strength
  - uncertainty
  - downside

Notably:
- approved `equal` allocation was omitted from the genome;
- there was no explicit market -> sector -> stock -> strategy hierarchical chromosome;
- there were no sector-context genes;
- there were no strategy-family chromosomes/modules;
- there was no explicit family applicability logic;
- the problem was largely converted into a sparse weighted scoring/ranking model.

## Actual score/action mechanics
The runner:
- combined selected features linearly with weights;
- converted the score to a cross-sectional rank;
- generated long strength from rank above `qual`;
- generated short strength from inverse rank below `short_qual` when shorting was enabled;
- applied `replace_margin`;
- transformed weights using one of the three allocation methods above;
- gross-normalized exposure to <= 1 (no leverage).

This is materially narrower than the approved discovery architecture.

## Actual features
Stock predictor-v2 features included:
- ret5
- ret20
- sma20
- range20
- rsi14
- relvol
- dd252
- rvpct

Market/R1 inputs included:
- mret5
- mret20
- mdd
- breadth200
- breadth20
- mrv
- breadth_vel5
- breadth_vel10
- breadth_accel
- breadth_persist
- prior_destruction
- price_impulse
- failed_rebound_reduction
- short_trend_repair
- vix
- vvix
- funding
- credit
- stress_norm
- recovery_retention

Cross-sectional stock features were daily-ranked.
Market features used causal rolling/expanding percentile transforms.
OFR funding/credit were shifted and forward-filled causally.

However, there was NO explicit sector-information layer despite the frozen architecture requiring sector context.

## Costs
The runner hard-coded:
`cost_bps=5`

It did NOT execute the required 0/5/10/20-bps finalist sensitivity analysis as part of the reported study.

## Comparator defect / reporting mismatch
The runner contains:
`spy=np.nanmean(ret,axis=1)  # reporting comparator only; not a GA input`

Thus the variable called `spy` was NOT actual SPY. It was an equal-weight mean return of the DEV117 stock matrix. This violates the frozen decline-reporting requirement for actual SPY comparison.

## SAFE behavior
Although SAFE existed mechanically, the evolved finalists used it essentially never:
safe_fraction ~0.0001988 in the displayed finalists.

Thus the experiment mostly evolved continuously invested long/short solutions rather than meaningful capital competition with Treasury/SAFE.

## Validation
The runner did correctly use four predetermined 80-training / 37-blind folds and did not expose DV25.
Each fold ran 200 generations.
Unique evaluations:
- fold 0: 32,654
- fold 1: 32,237
- fold 2: 31,482
- fold 3: 32,273

The Pareto objective was CAGR vs. MDD.

---

# 3. PRIOR MTS FINDINGS / PRIOR GA PERFORMANCE RELEVANT TO THE REVIEW

Important previously recovered evidence includes:
- four-drawdown loss attribution;
- alpha/crash coupling;
- portfolio simultaneity/common-factor analysis;
- factor-aware allocation tests;
- 50/17 crash-management experiments;
- multi-market crash classifier;
- dual crash detector;
- MA geometry;
- slow-crash descriptor;
- early sentinel;
- Path B / Group C;
- re-entry experiments;
- true-recovery emergence;
- GFC false-rally studies;
- 2009-vs-2020 recovery morphology;
- six-recovery R1 morphology;
- Defensive GA Phase 1 and Phase 1B;
- Open-State Response GA that had reached 54,045 unique genomes by generation 137 before the historical recovery incident.

Previously opened 50-stock GA results included approximately:
- GROWTH: ~26.05% CAGR, ~-36.63% maximum drawdown;
- INTERMEDIATE_KNEE: ~25.02% CAGR, ~-42.98% maximum drawdown.

Those results are not clean virgin proof and must not be treated as such. They are historical development evidence only.

## R1 findings
R1-F1: Extreme prior destruction establishes recovery context.
R1-F2: Initial price stabilization/impulse is early evidence but insufficient.
R1-F3: Breadth conversion has level, velocity/acceleration, and timing information.
R1-F4: Breadth must persist rather than merely spike.
R1-F5: Failed rebounds must continue disappearing.
R1-F6: Short-trend repair confirms structural recovery.
R1-F7: Stress normalization and recovery retention complete the morphology but may lag.

GFC adversarial evidence:
- March 2009 true recovery day5->day10:
  - return change +0.10855
  - breadth20 +0.671875
  - breadth200 +0.07045
  - positive20 +0.15
  - failed rebound change -0.25
  - gap20 +0.07067
  - gap50 +0.09185
  - slope20 +0.02910
  - slope50 +0.01443
- November 2008 false rally day5->day10:
  - return change -0.02364
  - breadth20 +0.10870
  - breadth200 +0.00420
  - positive20 +0.05
  - failed rebound change +0.10
  - gap20 -0.01050
  - gap50 +0.00088
  - slope20 +0.00142
  - slope50 +0.00290

Conclusion: the true recovery separated most strongly through continuing cross-sectional conversion, declining failed rebounds, and trend repair—not bounce magnitude alone.

---

# 4. CURRENT DEV117 RESULTS FROM THE REDUCED RUNNER

The combined report status is `DEV117_COMPLETE`.

Approximate displayed blind frontier:

| Blind MDD | Blind CAGR |
|---|---|
| -14.50% | +3.55% |
| -19.86% | +8.85% |
| -24.98% | +10.78% |
| -29.48% | +12.55% |
| -32.62% | +13.42% |
| -39.63% | +16.55% |

The ~20% MDD candidate:
- training CAGR ~4.95%, MDD ~-15.89%;
- blind CAGR ~8.85%, MDD ~-19.86%;
- blind era CAGRs:
  - E1 ~11.86%
  - E2 ~2.70%
  - E3 ~11.75%
  - E4 ~9.22%
- blind ending multiple ~5.43 over the continuous run.

The ~25% MDD candidate:
- blind CAGR ~10.78%;
- blind MDD ~-24.98%.

The ~30% MDD candidate:
- blind CAGR ~12.55%;
- blind MDD ~-29.48%.

The ~35% band candidate:
- blind CAGR ~13.42%;
- blind MDD ~-32.62%.

The ~40% band candidate:
- blind CAGR ~16.55%;
- blind MDD ~-39.63%.

The <=10% DD band produced no candidate.

## Current anomalies / concerns
1. Training turnover on several displayed candidates is essentially ~0.0001988, whereas blind turnover for the same genomes is roughly 0.03-0.07. Audit whether this is a legitimate population effect, a metric-definition artifact, or a bug.

2. SAFE fraction is essentially zero for these candidates (~0.0001988), suggesting SAFE did not meaningfully compete despite being part of the approved capital-allocation concept.

3. Selection diagnostics are NEGATIVE for several attractive lower-DD candidates. Example ~20% DD candidate blind:
   - mean selected-minus-unselected next return ~ -0.0002339 per session;
   - positive-session fraction ~0.4728.
The ~25%-35% candidates are also negative on this diagnostic.
Only the much higher-drawdown ~40% candidate turns the blind selection diagnostic positive (~+0.0001481).

4. The runner's actual-SPY decline comparison requirement was not implemented correctly.

5. The runner does not provide the rich sector/strategy-family architecture the user approved.

6. Because of these issues and poor economics relative to the project goal, DV25 has NOT been opened and must remain sealed.

Current MTS conclusion:
- The DEV117 run is scientifically informative as a test of the REDUCED runner.
- It is NOT a valid test of the full user-approved architecture.
- It has NOT earned advancement to DV25.
- The trading performance is economically unacceptable for the MTS objective.

---

# 5. OMNIFUNDS COMPARISON CASE

Treat all performance as company-reported unless independently verified.

From the user's OmniFunds materials and subsequent written answers:

## AI Market Leaders with Trend Protection
Reported:
- officially deployed August 26, 2026;
- as of September 29, 2026: approximately +86.2% YTD;
- approximately +70.8% of that was pre-release backtest from Jan 1 to Aug 26;
- approximately +9.0% from Aug 26 to Sep 29 after release;
- reported max drawdown over that post-release interval: ~3.9%;
- strategy was reportedly frozen at release and unchanged after August 26.

Architecture reported:
- not a live genetic algorithm selecting each day's trades;
- developed collaboratively using multiple LLMs plus the OmniFunds developer;
- proprietary AI-derived indicators;
- deterministic filtering, ranking, market-state, switching logic;
- a rules-based "Brake" / Trend Protection system that can move substantially toward cash as broader market conditions deteriorate;
- NASDAQ-100 universe;
- can allocate as much as 25% to a single security;
- can become highly concentrated in a leadership sector;
- once-daily execution / Market-on-Close orientation;
- an example historical vulnerability was about 95% semiconductor exposure followed by an approximately 14% one-day giveback before the system exited.

## OmniFunds Model 2
This is the product described as actually using Genetic Algorithm technology to select trades.

Their GA description:
- indicator relationships are genes;
- combinations become rules/chromosomes;
- crossover and mutation search the large rule space;
- an example demonstration used:
  - five genes;
  - five-day exit;
  - top 50 NASDAQ securities by liquidity;
  - 2,000 training iterations;
  - an explicitly separated out-of-sample period.
- OmniFunds materials describe "Actual Return: 40% Since Release" for Model 2 in the presentation available to the user.
- a separate 2026 YTD image dated 2026-09-09 reported AI Model 2 +32% YTD and AI Market Leaders +83.8% YTD.

The user also reports an OmniFunds claim of roughly 10-11% per month. We do NOT currently have an independently verified source establishing a durable 10-11% monthly return. Do not silently elevate this to a verified fact; instead analyze what level of CAGR such a claim implies and what evidence would be required to make a fair comparison.

Important comparison distinction:
- Market Leaders and Model 2 are NOT the same architecture.
- Market Leaders is the stronger reported performer in the materials, but its production trading system is described as deterministic AI-derived rules, NOT a live GA.
- Model 2 is the directly GA-relevant comparison.

Trading-cost note from OmniFunds answers:
- commissions/fees said to be included in published statistics;
- curves use exchange-reported opening/closing prices;
- they are not actual-customer-fill composites adjusted for every source of bid/ask, fill, latency, partial fill, or market-impact shortfall.

---

# 6. THE QUESTION YOU MUST ANSWER

The user believes the current MTS output is unacceptable and wants the NEXT GA instructions designed correctly.

Do NOT merely say "increase population/generations" or tune thresholds.

Determine:

1. Did the executed runner materially alter the approved research question?
2. Which implementation reductions are most likely to suppress discoverable alpha or suppress crash-defense behavior?
3. Which differences are harmless engineering simplifications versus scientifically consequential changes?
4. Is the linear weighted-score / cross-sectional-rank chromosome fundamentally too weak for the approved architecture?
5. Should strategy-family modules, conditional logic, regime-conditioned strategy applicability, sector-relative behavior, temporal pattern/morphology, and portfolio ecosystem interactions be first-class genes/substructures?
6. How should a GA search high-dimensional conditional architectures without requiring a brute-force Cartesian search?
7. How should holdings be horizon-free while still allowing GA to learn persistence, replacement, exit-to-SAFE, and short behavior?
8. How should SAFE compete economically so the GA is not structurally biased toward near-100% risky exposure?
9. How should market, sector, stock, and strategy information be represented without making arbitrary hard gates?
10. How should crash-state/R1 information be made discoverable without dictating actions?
11. How should the objective reward genuinely desirable wealth growth rather than permit pathological high-turnover/high-drawdown or continuously invested solutions?
12. Should CAGR/MDD remain the primary Pareto objective, and what should be constraints/guards versus diagnostics?
13. How should transaction costs be incorporated during evolution versus finalist sensitivity analysis?
14. How should effective independent evidence be handled so thousands of correlated daily observations are not mistaken for thousands of independent confirmations?
15. How should the four 80/37 DEV117 folds be used for model selection without leaking blind results back into evolution?
16. What should be frozen before DV25?
17. What exact criteria should decide whether DV25 is worth burning?
18. What preflight tests should prove that the implementation matches the specification BEFORE any expensive run starts?

---

# 7. REQUIRED OUTPUT: DESIGN THE GA INSTRUCTIONS

Produce a complete implementable instruction set for the next MTS GA experiment.

Use these sections:

A. Root-cause assessment
- approved architecture vs executed runner;
- rank each discrepancy by expected scientific consequence: CRITICAL / HIGH / MEDIUM / LOW;
- identify any likely bugs requiring repair before redesign.

B. Research architecture
- define market layer;
- sector layer;
- stock layer;
- strategy/applicability layer;
- opportunity-ranking layer;
- portfolio/allocation layer;
- incumbent/challenger/SAFE competition;
- long/short behavior;
- no leverage.

C. Genetic representation
- exact chromosome structure;
- typed genes/subtrees/modules;
- how conditional relationships are represented;
- strategy families;
- market/sector/stock interactions;
- mutation operators;
- crossover operators;
- how complexity can grow/shrink;
- how invalid structures are rejected;
- how semantic duplicates are cached;
- do not use ticker identity.

D. Feature substrate
- what existing causal features are retained;
- what sector features are required;
- what additional causal features should be calculated;
- distinguish derived measurements from trading rules;
- no future leakage.

E. Horizon-free position lifecycle
- exact ENTER / CONTINUE / REPLACE / EXIT_TO_SAFE / SHORT semantics;
- no fixed holding horizon;
- no elapsed-time rule;
- how persistence can emerge from causal state;
- how challengers displace incumbents after friction and uncertainty.

F. Portfolio construction
- capital competition;
- concentration allowed when economically earned;
- diversification not hard-coded;
- SAFE as a true competing asset;
- sector concentration measured;
- gross exposure <=100%;
- no leverage.

G. Fitness / evolutionary pressure
- exact primary objectives;
- constraints versus soft penalties versus diagnostics;
- crash preservation;
- recovery burden;
- turnover;
- tail losses;
- time underwater;
- uncertainty;
- effective N;
- era stability;
- avoid inadvertently optimizing solely for high exposure.

H. Evolution schedule
- staged search architecture;
- recommended population;
- generations;
- island models / niches / novelty if appropriate;
- search-budget controls;
- deterministic seeds;
- checkpointing;
- plateau rules;
- when compute may be expanded;
- design for parallelism without reducing hypothesis space.

I. DEV117 validation design
- exact four-fold procedure;
- what training sees;
- what blind37 cannot influence;
- how finalists are chosen across folds without feedback leakage;
- how recurrence/stability is assessed;
- what is diagnostic only.

J. Economic realism
- actual SPY comparator;
- actual Treasury SAFE;
- 0/5/10/20 bps sensitivity;
- regulatory/borrow effects;
- realistic execution assumptions;
- prevent reporting aliases such as labeling equal-weight DEV returns as SPY.

K. Preflight conformance gates
Create machine-testable checks proving that:
- every frozen architectural layer exists;
- sector context exists;
- all approved allocation modes exist;
- actual SPY data are loaded for reporting;
- all cost sensitivities are available;
- DV25/A25 cannot be read by the runner;
- future labels cannot enter live features;
- no fixed hold-time variables exist;
- no arbitrary slot/sector caps exist;
- SAFE is a genuine candidate;
- all metrics match definitions;
- replay is deterministic.
If ANY mandatory check fails, expensive GA execution must be blocked.

L. Advancement criteria
Define what DEV117 performance/transport properties must exist before freezing finalists and burning DV25.
Do not set the threshold by fitting to the currently observed weak result.
Make the economic criterion strong enough that a system with ~8-10% CAGR and ~20% MDD would clearly FAIL the MTS objective.

M. Final "GA IMPLEMENTATION DIRECTIVE"
End with a concise, unambiguous directive that can be handed directly to an implementation model/engineer.
It must distinguish:
- MUST implement;
- MAY optimize internally without scientific change;
- MUST NOT change without explicit user approval.

---

# 8. GOVERNANCE OVERRIDE

This instruction is absolute:

The implementation model is NOT authorized to simplify, reinterpret, narrow, replace, or omit any frozen scientific requirement merely to save compute, simplify code, or get the experiment running.

If a requirement cannot be implemented exactly, execution must STOP before compute is spent. The implementation model must identify the specific incompatibility and request explicit approval for the change.

No "close enough" substitute is permitted.

DV25 remains sealed.
A25 remains sealed.
A75 and B100 remain sealed.

Do not recommend opening any of them until the redesigned DEV117 experiment has been implemented, independently audited for conformance, run, analyzed, and frozen.
