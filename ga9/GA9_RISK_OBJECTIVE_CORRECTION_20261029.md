# GA9 controlling correction — user clarification 2026-10-29

8% portfolio MDD is an external OmniFunds comparison point, NOT the user's GA9 hard risk limit. Remove 8% as a mandatory discovery/selection/fitness feasibility gate in GA9 after updating dependent tests. Preserve observed MDD as a continuous Pareto objective, and report 8% as an aspirational comparison threshold. Do not claim OmniFunds results independently verified.

Primary objective: maximize out-of-sample net CAGR excess versus frozen, preselected ETF benchmark (SPY broad US, QQQ Nasdaq focus). Optimize return and risk jointly: report Pareto frontier of CAGR/excess CAGR/MDD/Calmar and capital exposure, and avoid rewarding staying in cash during bull markets merely for low MDD. Allow discovery candidates >8% MDD; do not silently deploy them. Compare same dates and costs, with PIT selection and no forward leakage.

Engineering priority before long evolution: eliminate alphabetical 16-stock sample, establish full-universe PIT momentum baseline, distinguish stock selection from allocation/exit failures, audit average exposure ~2%, and inspect candidates with nonpositive momentum screen scores. Keep GA8 and its checkpoints untouched. Run bounded functionality proofs and document evidence before long jobs.

This file is a specification update, NOT evidence that runtime code has been changed or a run started.
