# Frozen 2024 forward comparison

All 5,851 Phase-1 training qualifiers and all three verified Phase-0 survivors are included. The three survivors overlap Phase-1 behaviors: 5,851 unique replays, three dual memberships, zero supplemental heavy replays.

Window: 2024-01-01 through 2024-12-31 (252 sessions), fresh $100,000 each. Frozen genes, manager, entry and exit rules, costs and data match the main job. No evolution, production writes, or selection using 2024 results.

| Phase-0 survivor ID | CAGR | Max drawdown | Calmar | Final NAV | Comparison gate |
|---|---:|---:|---:|---:|---|
| `d520b78763e1805a` | 8.84% | 5.26% | 1.681 | $108,842.39 | Pass |
| `e4d65994319677d7` | 6.11% | 2.81% | 2.177 | $106,112.73 | Pass |
| `efe0ff726c852a0d` | 4.20% | 6.54% | 0.642 | $104,201.03 | Fail |

Comparison gate: CAGR > 1.5 × abs(MDD), abs(MDD) < 20%, at least 30 closed trades when available. This is an outcome label only; all candidates remain included.

Benchmarks:
- SPY: CAGR 26.01%, max drawdown 8.36%, final NAV $126,010.31.
- equal_weight_DEV79: CAGR 20.70%, max drawdown 7.20%, final NAV $120,697.27.

QQQ: Absent from DEV79 and previous forward metadata reports no real QQQ parquet under /opt/mts.

Evidence: `manifest.json` hashes the original 2023 forward JSONL, summary and saved checkpoint corroborating all three parents. `cohort.json` retains exact genomes, managers, discovery phase/generation, parents and 2023 evidence. `merged_results.jsonl` retains both memberships; `discovery_lineage.jsonl` preserves discovery metadata for every source identity. Main training observations and qualifier records remain in `../ga8_forward_all_20261029/`.

Limitations:
- Retrospective DEV79 universe; complete historical PIT/delisted coverage unproven.
- Chronological out-of-training replay, not prospectively sealed experiment.
- Equal-weight fixed 79 sleeves, GEV cash until regular listing.
