# GA8 exhaustive phase-1 forward test

All **5,851 / 5,851** distinct training qualifiers tested independently on 2024. No top-N cap, forward fitting, or selection.

Training: 2022-01-01 ≤ date < 2024-01-01. Gates: CAGR > 1.5*abs(MDD), abs(MDD)<0.20, closed_trades>=30 when available. Enumerated 68,451 distinct phase-1 behaviors across the evaluated catalog, current and archived generation journals, and frozen stop checkpoint/status. No conflicting qualifying training metrics.

Each replay starts with $100,000 fresh cash, uses 252 identical sessions (2024-01-02 through 2024-12-31), and fixed GA8 execution. Trade count means closed trades. Forward success applies the same gates; benchmark outperformance means higher final NAV.

Forward successes: **2,712 / 5,851 (46.35%)**.

| Benchmark | CAGR | MDD | Calmar | Final NAV | Qualifiers beating it |
|---|---:|---:|---:|---:|---:|
| SPY | 26.01% | 8.36% | 3.113 | $126,010.31 | 0 / 5,851 |
| equal_weight_DEV79 | 20.70% | 7.20% | 2.873 | $120,697.27 | 6 / 5,851 |

QQQ was absent from DEV79; no QQQ parquet found under /opt/mts. No substitute was generated.

## Distributions

| Period / metric | Min | 5th | 25th | Median | 75th | 95th | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| training / cagr | 1.86% | 5.87% | 8.44% | 10.34% | 12.32% | 16.09% | 26.84% |
| training / max_drawdown | 0.64% | 2.92% | 4.37% | 5.27% | 6.39% | 8.54% | 12.59% |
| training / calmar | 1.50 | 1.53 | 1.66 | 1.86 | 2.18 | 2.81 | 7.84 |
| training / final_nav | 103,736.40 | 112,002.31 | 117,487.63 | 121,597.01 | 125,994.26 | 134,520.94 | 160,440.97 |
| training / closed_trades | 45.00 | 209.50 | 353.00 | 437.00 | 525.00 | 730.00 | 1,508.00 |
| forward / cagr | -11.82% | -1.22% | 2.63% | 5.20% | 8.86% | 13.45% | 23.18% |
| forward / max_drawdown | 0.47% | 2.00% | 2.81% | 4.12% | 5.76% | 8.20% | 14.90% |
| forward / calmar | -0.98 | -0.22 | 0.49 | 1.32 | 2.73 | 5.05 | 9.60 |
| forward / final_nav | 88,177.65 | 98,781.02 | 102,633.46 | 105,195.90 | 108,855.19 | 113,453.16 | 123,184.02 |
| forward / closed_trades | 17.00 | 83.00 | 139.00 | 207.00 | 259.00 | 428.00 | 877.00 |

## Winners by forward NAV

Descriptive ranking after every qualifier was tested; these are not selections for further tuning.

| ID | Train CAGR | Train MDD | Forward CAGR | Forward MDD | Forward Calmar | Forward NAV | Closed trades |
|---|---:|---:|---:|---:|---:|---:|---:|
| a63694c2458c4b41 | 11.96% | 6.02% | 23.18% | 2.79% | 8.321 | $123,184.02 | 280 |
| e4ce29e8c1dbd5ea | 8.49% | 5.37% | 22.01% | 2.59% | 8.509 | $122,005.61 | 287 |
| d631bfe8dce598c4 | 12.86% | 8.54% | 21.78% | 4.08% | 5.341 | $121,783.91 | 347 |
| d8657e3857259685 | 8.37% | 5.20% | 21.45% | 2.50% | 8.569 | $121,452.54 | 312 |
| 02fdc6046f89e534 | 13.48% | 8.32% | 21.29% | 3.93% | 5.414 | $121,285.74 | 286 |
| ca8ae54ed8a0c78c | 11.48% | 7.62% | 21.08% | 2.38% | 8.843 | $121,079.34 | 238 |
| 943c7beaedd6cd8b | 14.85% | 6.36% | 20.68% | 3.01% | 6.861 | $120,683.64 | 247 |
| b7d7f01da8a15a30 | 18.55% | 12.34% | 20.53% | 4.45% | 4.617 | $120,527.63 | 315 |
| f0a51c4b65e4cacc | 16.28% | 10.29% | 20.45% | 2.88% | 7.110 | $120,452.69 | 267 |
| 8d1d6bec167b7805 | 16.62% | 10.68% | 20.15% | 4.26% | 4.733 | $120,152.41 | 311 |

## Losers by forward NAV

Descriptive ranking after every qualifier was tested; these are not selections for further tuning.

| ID | Train CAGR | Train MDD | Forward CAGR | Forward MDD | Forward Calmar | Forward NAV | Closed trades |
|---|---:|---:|---:|---:|---:|---:|---:|
| d03d53ea6e6548da | 17.24% | 10.81% | -11.82% | 14.90% | -0.794 | $88,177.65 | 788 |
| 2356dd3eb10c85a3 | 20.60% | 11.39% | -10.25% | 12.54% | -0.817 | $89,750.78 | 810 |
| b26973977458d098 | 20.87% | 10.99% | -10.18% | 12.54% | -0.812 | $89,816.78 | 811 |
| 6a3e531544991f3a | 8.39% | 4.50% | -9.13% | 9.32% | -0.980 | $90,866.15 | 694 |
| fb59d23055112d29 | 9.11% | 5.94% | -9.05% | 11.87% | -0.763 | $90,950.45 | 450 |
| 1787e264ca231cee | 15.31% | 5.84% | -8.05% | 11.86% | -0.679 | $91,949.59 | 257 |
| 041fe8589b895a31 | 11.64% | 6.71% | -7.73% | 10.86% | -0.712 | $92,271.66 | 235 |
| 907e650c7e143ff5 | 21.52% | 12.59% | -7.71% | 12.49% | -0.617 | $92,290.27 | 877 |
| 6f269e7dd9ba2e31 | 7.09% | 3.34% | -7.65% | 8.15% | -0.939 | $92,350.22 | 204 |
| 095ef58335ba0370 | 9.84% | 6.35% | -7.52% | 10.05% | -0.748 | $92,481.52 | 687 |

## Artifacts and verification

- `per_chromosome.csv`: every qualifier with training/forward CAGR, MDD, Calmar, NAV, closed trades, success and benchmark flags.
- `qualifiers.json`: frozen genomes, managers, original IDs, training metrics and provenance counts.
- `training_observations.jsonl` and `catalog_snapshot.sqlite`: retained evaluation metadata and original catalog.
- `manifest.json` and `data_metadata.json`: source hashes, cohort rules, execution conventions and data limitations.
- `results.jsonl`, `checkpoint.json`: durable per-chromosome results; rerun `/opt/mts/.venv/bin/python ga8_forward_all_20261029/run_all.py` from repository root to resume.
- `verification.json`: independent SQL gate count, complete unique coverage, unchanged source hashes, three training parity checks, and exact previous-winner/benchmark parity.

Production GA8 and GA9 were not modified. Other existing forward tasks were left untouched. Python sources were copied locally before replay so concurrent edits could not alter this run.

Limitations: retrospectively selected DEV79 universe with unproven full historical PIT and delisted coverage; chronological out-of-training evaluation rather than a prospectively sealed experiment. Equal weight uses 79 fixed cash sleeves with GEV cash until regular-way listing. Costs are 5bp slippage plus 1bp commission per fill; dividend receivables are nonspendable; terminal holdings are marked without liquidation.
