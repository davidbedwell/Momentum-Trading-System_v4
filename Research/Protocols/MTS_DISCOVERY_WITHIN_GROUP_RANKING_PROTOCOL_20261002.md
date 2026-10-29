# MTS v4 — Discovery Within-Group EV/p10 Ranking Protocol — 2026-10-02

## Objective
Test whether EV/p10 can improve wealth without worsening portfolio tail risk when capital is redistributed only among simultaneous signals that share the same ticker or signal family.

## Rationale
Portfolio-wide ranking can change cross-ticker exposure and therefore daily correlation risk. Within-ticker redistribution preserves each ticker's same-day total scheduled capital exactly while allowing EV/p10 to favor stronger genomes. Within-family redistribution is a structurally distinct control.

## Evidence boundary
Discovery Development only for candidate generation. Discovery Holdout stays closed. No additional Verification A or Verification B access.

## Fixed predictor
Causal historical EV/p10, minimum N=100, genome -> family -> global backoff. No predictor retuning.

## Candidate families
1. Within-ticker, same-entry-day top-50% fixed-budget redistribution; caps 1.10x, 1.25x, 1.50x.
2. Within-family, same-entry-day top-50% fixed-budget redistribution; caps 1.10x, 1.25x, 1.50x.

For every ticker/family/day group, total scheduled multiplier must remain equal to group size. Groups with one eligible signal remain 1.0x.

## Gate
Unchanged strict gate: positive mean contribution; >=60% positive ticker/year/family breadth; ticker-cluster CI lower bound >0; <=15% ticker/genome positive-contribution concentration; terminal wealth > ordinary equal sizing; max drawdown and CVaR5 may not both worsen. Report exposure and exact risk metrics.

## Stability
Require at least two caps in a family to pass before nomination. Prefer the simpler/lower cap in a passing plateau unless a higher cap shows materially broader evidence.

## Integrity
No Holdout or Verification access; no tail-risk tolerance relaxation.
