# MTS v4 Human-Approved Governance Amendment — 2026-09-14

This amendment is explicitly authorized by the human owner and supplements `ChatGPT.md` for the branch `mts-v4-cross-sectional-derived-market-store-20260914`.

Where the existing root authority says the Research Nexus must not durably retain reproducible market datasets, the following narrower rule now governs:

1. Raw or otherwise reacquirable source data such as OHLCV remains temporary research/update cache data and must not be durably warehoused in Nexus.
2. Reproducible **derived point-in-time market state** may be retained durably in a Nexus-owned derived market store when doing so avoids repeated expensive universe-wide reconstruction and supports cross-sectional research.
3. The derived market store must preserve feature/version definitions, point-in-time semantics, universe identity, provenance, high-water marks, and historical effective-date observations. Routine market progress appends new observations rather than silently rewriting old values.
4. Nexus scientific memory continues to preserve findings, hypotheses, negative results, lineage, and research state separately from bulk derived observations.
5. Existing single-subject research remains valid. MTS must also support universe/cohort research without sending bulk row data to the AI Research Director.
6. The detailed approved design is `Documentation/2026-09-14_MTS_V4_CROSS_SECTIONAL_DERIVED_MARKET_STORE_DESIGN.md`.
7. Qwen must not be released as an autonomous Research Director until the repaired deterministic backend passes acceptance controls and Sol has established the historical benchmark/approach corpus described in that design.

This amendment does not authorize hard-coded scientific conclusions, deterministic replacement of AI scientific authority, look-ahead leakage in blind/live prediction, or durable storage of raw reacquirable market data.
