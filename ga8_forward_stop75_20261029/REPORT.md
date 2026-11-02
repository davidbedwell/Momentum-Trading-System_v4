# Frozen GA8 forward comparison

Portfolio `3d8db5c6e547bd8c`; 2024-01-02 through 2024-12-31 (252 sessions), initial NAV $100,000 each. Calendar 2024 is the next untrained phase-1 window. No refit or evolution.

| Account | Net return / CAGR | MDD | Calmar | Final NAV | Fills / closed trades | Costs | Mean / peak / terminal exposure |
|---|---:|---:|---:|---:|---:|---:|---:|
| GA8 | 0.52% | 11.90% | 0.044 | $100,520.14 | 1703 / 809 | $5,581.16 | 29.85% / 79.89% / 8.01% |
| SPY | 26.01% | 8.36% | 3.113 | $126,010.31 | 1 / 0 | $59.97 | 99.12% / 100.00% / 98.81% |
| equal_weight_DEV79 | 20.70% | 7.20% | 2.873 | $120,697.27 | 79 / 0 | $59.97 | 98.41% / 99.51% / 98.16% |

GA8 underperformed SPY by 25.49 percentage points ($25,490.18) and equal weight by 20.18 points ($20,177.14). GA8 MDD exceeded them by 3.54 and 4.69 points respectively. The frozen training result did not transfer. GA8 fails its existing forward feasibility criterion (Calmar).

GA8 had 810 entries, 809 closed trades and one terminal position; fills include adds/reductions. SPY and equal weight retain their holdings without terminal liquidation.

QQQ: Unavailable: absent from DEV79; no real QQQ parquet found under /opt/mts. No synthetic substitute.

## Execution and limitations

- Fresh cash account; first decision Jan 2 close, earliest entry Jan 3 open for all.
- 5 bps adverse slippage plus 1 bp commission each fill; fractional shares.
- Dividends in NAV as nonspendable receivables; no reinvestment; terminal holdings marked, no liquidation.
- CAGR uses 252/sessions. GA8 T+2 settlement; no cash interest.
- No refit, evolution, parameter selection, or 2026 holdout replay.
- Retrospectively selected DEV79 sample; historical full-market PIT membership/delisted coverage unproven. Applies to strategy and equal-weight diagnostic.
- Equal weight assigns 79 fixed sleeves; GEV cash until regular-way listing Apr 2 2024. No filtering on forward performance.
- Prefix check validates data causality, not historical universe selection. This is chronological out-of-training replay, not a prospectively sealed experiment.
- Vendor split-normalized prices and dividend ex-date receivables; dividend payment dates unavailable.

Small January replay and identical prefix using the full 2024 panel passed. Frozen training metrics reproduced exactly before forward replay. Snapshot hashes were unchanged. One worker; BLAS threads capped at one. GA9 code was imported read-only for existing benchmark functions; its pilot was not run or altered.

Reproduce from repository root:
```bash
/opt/mts/.venv/bin/python ga8_forward_stop75_20261029/run_forward.py
```

Full daily NAV, fills, events and audit: `GA8.json`; passive daily paths/fills: `SPY.json`, `equal_weight_DEV79.json`. Source and code hashes, audits and conventions: `metadata.json`.
