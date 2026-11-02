# GA9 historical opportunity discovery — engineering charter (2026-10-30)
Implement a standalone, staged research pipeline, not portfolio trading or certification. Preserve existing GA9/GA8 code and results; changes in isolated new files only unless essential and tested.

Research protocol:
- Historical NYSE/NASDAQ common-stock universe 2005–2011, point-in-time listing membership, IPOs, delistings, split/dividend-adjusted OHLCV, corporate actions. Never assume today's tickers were the historical universe. No ETFs/warrants/preferred shares; record exclusions and coverage.
- Discovery 2005–2009: label known exceptional winners using both calendar-year adjusted returns and within-year low-to-high advances, with start/peak dates, liquidity, market cap when available. Define exact thresholds/config; no hard trade-risk filters. Include failures/nonwinners as controls.
- Compare three research arms: chart/volume/market-only, fundamentals-only, combined. On the *same eligible stock-date intersection*, report incremental value; also report separate broad chart-only universe and missing-fundamentals coverage. Never treat missing fundamentals as zero.
- Financial records must be point-in-time as reported and only usable after public filing/availability timestamp (conservative lag if date precision absent). Record source, release date, revision policy, coverage. No future financial statements.
- Each development year: fit using known years only; before incorporating next year's labels, freeze predictions and compare to actual rankings, recall@K, precision@K, lead time, remaining upside, and naive baselines. Known-winner study can inform hypotheses, but never claim development years are pristine.
- 2010 and 2011 are locked unseen evaluation years. Freeze code, feature definitions, tuning, candidate models, metrics, and hashes BEFORE accessing their labels. Do not inspect or compute 2010/2011 winners during implementation or debugging. If labels have already been exposed elsewhere, disclose that and call these historical holdouts, not pristine.
- No exact winner-list memorization, no future leakage from adjusted historical membership, retroactive restatements, survivorship, sector classifications, or market cap. Explicit point-in-time as-of tests.

Execution sequence (functionality first):
1. Audit available historical datasets and provider credentials by *presence only*, never print secrets. Report coverage, gaps, feasibility, cost implications. Do not buy data or silently substitute incomplete sources.
2. Implement data adapter interfaces, schema, universe reconstruction, winner labeling, PIT feature construction, arm comparison, chronological folds, holdout locking, provenance, and unit tests with tiny synthetic fixtures. Use deterministic outputs and clear CLI.
3. Run small 2005 demonstration ONLY if defensible data exists; otherwise stop at working fixture and a precise data acquisition recommendation. No long GA runs, no 2010/2011 label access, no unrelated GA edits.
4. Report artifacts, tests, git status, blockers, ETA for next stage. Stop/audit/reengineer on nonfunctional behavior; no blind generations.

Do not claim causation from correlation. The user wants Codex engineering to begin now, not an extended certification project.