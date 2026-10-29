# MTS Crash-State Genome Protocol
Date: 2026-10-03
Status: FROZEN BEFORE SEARCH

## Research question
Can contemporaneously observable market/portfolio state identify when systemic downside risk has become large enough that MTS should reduce equity exposure, and identify stabilization soon enough to re-enter, such that compounded CAGR after costs increases?

## Scope and isolation
This is a dedicated crash-state genome, separate from setup-selection/ranking genomes.
Development evidence is limited to the already-consumed 67-stock Discovery laboratory and causal market information available through each date.
Heldout50, remaining Discovery, Verification A, and Verification B remain sealed.
No event names, future crash dates, future drawdown labels, or hindsight news variables may be genome inputs.

## Episodes
Analyze the complete 2006-09-15 through 2026-09-14 development history, not only the four known maximum drawdowns.
Known drawdowns are cases, not templates.
Include ordinary corrections, false alarms, rallies, recoveries, and calm periods so false exits and delayed re-entry are penalized.

## Mechanical-only governance
The crash-state controller is market-structure-only for this research phase.
Exclude news, event descriptions, headlines, sentiment interpretation, macro narratives, discretionary labels, and AI/LLM judgment from all trading inputs and decisions.
Historical event names may be used only after results for human explanation; they may not define episodes, features, thresholds, exits, re-entry, selection, or fitness.
Every deployable decision must be reproducible from timestamped causal numeric/boolean inputs available at that decision time.
All transformations, thresholds, confirmation periods, hysteresis, exposure actions, and re-entry conditions must be explicit and deterministic.
The Analysis Engine performs calculations on specified variables/hypotheses; it does not reason about market meaning or formulate hypotheses.
GA searches the frozen mechanical parameter/rule space. Research interpretation remains outside the live decision path.
No subjective override may rescue or suppress a genome decision.

## Genome state inputs
Market trend/returns: 1/3/5/10/20/60 sessions; distance/slope of causal MA20/50/200 where available.
Volatility: realized 5/20/60, ratios, acceleration, shock magnitude.
Breadth: fraction positive/negative, deterioration/improvement and acceleration using causally available universe/portfolio measures.
Correlation/dispersion: cross-position return correlation/convergence, dispersion and same-direction fraction.
MTS state: live exposure, safe fraction, position count, concentration/HHI, new-position fraction, signal count/intensity/opportunity density.
Required interaction families include volatility x breadth, volatility x correlation, breadth x correlation, exposure x correlation, signal intensity x volatility, signal intensity x breadth, concentration x correlation, and recovery interactions.

## Genome actions
Equity exposure may be 100/75/50/25/0 percent; residual earns frozen 3% safe return.
No leverage above 100%.
A genome may contain separate warning, crash-confirmation, stabilization, and re-entry logic.
Allow confirmation and hysteresis, but penalize excessive delay and switching.
No fixed historical-date filters.

## Exhaustive crash-mechanism research before evolutionary search
First construct a comprehensive development-era catalog of cataclysmic, severe, near-crash, correction, false-alarm, stabilization, and recovery episodes.
Analyze each episode across pre-crash transition, crash propagation, trough/stabilization, and post-crash recovery phases at multiple causal horizons.
Systematically test state variables, thresholds, rates of change, persistence, interactions, sequencing, and recovery signatures. Preserve negative findings and false positives.
The objective is mechanism-space exhaustion: identify which observable state changes consistently distinguish dangerous systemic transitions from ordinary weakness, and which observable recovery states distinguish durable stabilization from temporary rebounds.

## Evolutionary search
Only after the mechanism audit, use GA to search combinations of supported and plausible state mechanisms.
There is no fixed genome-count target. Search as many genomes and generations as necessary while new mechanisms, non-dominated combinations, or materially improved out-of-sample wealth behavior continue to appear.
Stop based on scientific/search saturation and frontier stability, not an arbitrary count.
Use broad mutation/crossover across thresholds, interactions, sequencing, confirmation, hysteresis, exposure levels, and re-entry rules.
Preserve Pareto diversity and mechanism diversity; do not optimize a single crash statistic.

## Primary objective
Primary advancement criterion: improve pooled compounded CAGR / synthetic terminal wealth after costs across four independently reset eras versus the unchanged base portfolio.
Four eras reset to $100,000:
E1 2006-09-15--2011-09-14
E2 2011-09-15--2016-09-14
E3 2016-09-15--2021-09-14
E4 2021-09-15--2026-09-14

## Secondary diagnostics
Max drawdown, CVaR5, worst day, time underwater, drawdown frequency/depth distribution, recovery duration, upside/downside capture, safe fraction, turnover, switches/year, false exits, missed rebound, time-to-exit after crash onset, and time-to-reentry after stabilization.

## Generalization gate
Use leave-one-era-out development: derive/select on three eras, freeze the genome/rule, and apply unchanged to the fourth; rotate through all four.
A candidate is not accepted because it solves 2008 or 2020 alone.
Individual held-out eras may have modest CAGR degradation, but pooled CAGR improvement must not be explained by one memorized crash and behavior must remain economically coherent across rotations and cost sensitivities.

## Costs
Evaluate 0/5/10/15/20 bps with 10 bps primary.
Switching costs and foregone equity opportunity must be included.

## Scientific controls
Compare against unchanged MTS, always-invested equity exposure, simple market-trend controls, simple volatility controls, and simple fixed exposure reductions.
A complex genome must beat useful simple controls on the primary wealth objective or demonstrate robust incremental information.

## Interpretation
The desired mechanism is not permanent defensiveness. It is a card-counting-style state controller: remain exposed when MTS edge is sufficiently compensated, retreat when observable systemic state changes the odds, and re-enter when that state stabilizes.
Drawdown reduction alone is not advancement if compounded CAGR after costs falls.

## Freeze rule
Do not open heldout50 or any untouched bank to design, tune, select, or repair crash genomes. Untouched validation occurs only after a candidate architecture is frozen.
