# MTS v4 — Risk/Return Tenability Gate

**Frozen:** 2026-10-03

## Governing Question

Are the major MTS losses preceded by causal, observable information that distinguishes dangerous exposure from the exposure responsible for MTS's major wealth-producing periods?

## Required Drawdown Decomposition

Every major portfolio drawdown must be decomposed using information available at or before the relevant decision point, including:

- market state;
- cross-position correlation and concentration;
- simultaneous equity exposure / number of active positions;
- volatility level and volatility expansion;
- MTS signal intensity / opportunity density;
- strategy-family exposure;
- sector exposure where causally available;
- position age and time since entry;
- interactions among these variables.

No future information may be used to define a protective state.

## Required Counterfactual

For every candidate risk indicator or interaction, test both sides:

1. How much subsequent loss could have been avoided by reducing exposure when the indicator was observable?
2. How much subsequent wealth-producing return would have been removed by the same rule?

A rule does not qualify as risk management merely because it lowers maximum drawdown by holding more capital in the 3% safe asset.

## Tenability Standard

The architecture remains scientifically tenable only if causal information available before major losses provides useful separation between dangerous exposure and wealth-producing exposure, such that risk can be reduced without destroying a disproportionate share of the strategy's return.

Evidence must be evaluated across independent development eras and with realistic transaction-cost sensitivity. Pooled full-history improvement alone is insufficient.

## Failure Condition

If major losses are not meaningfully distinguishable ex ante from the states producing the major gains—or if materially reducing those losses necessarily removes a disproportionate share of wealth creation—then the risk/return structure is considered inverted for the MTS objective.

Under that result, the current architecture is **untenable**.

It must not be rescued by:
- mechanically lowering exposure until drawdown appears acceptable;
- optimizing directly around known historical drawdowns;
- using hindsight-defined crisis dates;
- accepting large CAGR destruction as successful risk control;
- weakening the tenability criterion after results are observed.

## Interpretation

This is a falsifiable go/no-go gate for the current MTS architecture, not a preference and not a post-hoc diagnostic.

Passing this gate does not establish deployability. Failure rejects the current architecture for the stated MTS objective.

Development evidence only. Remaining Discovery stocks and Verification A/B remain sealed unless separately authorized.
