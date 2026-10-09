# Horizon-Grouped Pareto Ranking — Approved Freeze 2026-10-08

Status: USER APPROVED, FROZEN. Explicit amendment to GEN1_PARETO_PARENT_RANKING_FREEZE_20261008.md. No silent changes.

## Architecture
- Group chromosomes by holding-horizon windows BEFORE Pareto ranking. Rank independently WITHIN each window using successive nondominated fronts; preserve all EV-positive eligible chromosome-window memberships regardless of Pareto rank.
- Provisional horizon windows approved for implementation: 1–3, 4–7, 8–15, 16–30, 31–45, 46–63 trading sessions, and 64–126 once Phase B supplies validated results. Do not fabricate missing horizon measurements.
- Eligibility remains EV_net > 0 at at least one actually evaluated horizon in the relevant window; distinguish preliminary eligibility from certified viability.
- Chromosomes can belong to multiple windows when separately EV-positive there. Report both unique chromosome counts and chromosome-window memberships.
- Each populated, viable window must be represented in eventual breeding-parent pools; preserve multiple diverse parents per window where available. Do not enforce the former ~128 parent planning target as a quota. Do not promote weak/nonviable chromosomes merely to fill a window.
- Rank dimensions: net EV, statistical reliability and horizon consistency; track genetic/behavioral diversity separately and preserve it in eventual selection. MAE (mean, tail, exceedance distributions when available) and EV/MAE are visible diagnostic fields with ZERO effect on eligibility, dominance, ranking or breeding.
- Produce comprehensive per-candidate diagnostics including EV, MAE, sample/effective sample counts, horizon behavior, matched passive diagnostics, and eventual trade-level/portfolio performance when available.
- The numerical dominance objectives used in any immediate ranking are explicitly PROVISIONAL and diagnostic; exact objective definitions, multiplicity handling, diversity preservation algorithm, tie rules and certified parent-selection criteria require independent specification and freeze before breeding.
- Preserve all raw results and prior ranking artifacts; protected DEV37, DEV50 and BLIND17 untouched. Do not begin Generation 2 before remaining scientific gates.
