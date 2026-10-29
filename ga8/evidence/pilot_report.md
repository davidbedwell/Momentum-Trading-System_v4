# GA8 engineering and bounded research report

Real-data funded replay and bounded evolutionary search completed. No validated edge claim.

| Replay | CAGR | MDD | Calmar | Closed trades | Exposure | Costs |
|---|---:|---:|---:|---:|---:|---:|
| 2022 smoke | -11.40% | 17.38% | -0.656 | 309 | 45.83% | $2601.23 |
| 2023 walk-forward | 6.38% | 5.72% | 1.115 | 371 | 43.75% | $2954.22 |
| 2024 walk-forward | 3.06% | 3.65% | 0.837 | 170 | 31.78% | $1589.16 |
| 2025 walk-forward | 4.11% | 11.74% | 0.350 | 271 | 49.83% | $2066.52 |
| 2026 final holdout | 37.18% | 5.64% | 6.598 | 244 | 46.58% | $2048.87 |

No survivor is promoted unless all chronological tests satisfy MDD <20% and Calmar >1.5. The best infeasible frontiers remain in each search ledger.

Each fold resets to $100,000, purges positions at its boundary, and uses only backward warmup. The model was frozen before each 2026 evaluation. There were two accounting versions: preliminary ex-date spendable dividends, then corrected nonspendable receivables. The corrected run reused the same seed, search bounds and training chronology. No strategy parameters were tuned from preliminary holdout outcomes. Thus 2026 is not strictly untouched; see holdout_access.json. 2025 results did not tune the model. Earlier MTS studies have seen these years, so this is GA8 isolation, not global blindness.

Next-open stops trigger at close; gaps can exceed the -2% loss policy. Conservative T+2 settlement, 5bp slippage and 1bp fee each side. 10% entry cap (9.9% buffer), 2% portfolio stop-risk cap, no leverage; cash yields zero. Per-symbol weights can drift over 10% intraday and trigger next-open exit. Position sizing limits implied stop risk below the 1–2% per-trade ceiling; it does not force that much risk.

Sector, earnings, named crash A/B/B1/C and R-1, SGOV and SPY are disabled for missing verified causal inputs. Price correlation provides diversification. Corporate actions rely on vendor split normalization with dividends credited as nonspendable receivables to overnight holders; no independent vendor authenticity certification. Static DEV79 membership has survivorship/PIT limitations. No GA4 archive strategies were used.

Search is a small engineering pilot, not exhaustive discovery. Grammar supports nested AND/OR trees, independent hold/exit families and conditional scaling; all seven enabled families are initialized. No long exploration is authorized by this result. See lineage, marginal ablations, funded fills and equity in JSON.

Measured first search: 80 native evaluations in 11.81s (6.77/s). Total elapsed 70.13s.

## Delivery evidence

Eight tests passed. Offspring ae3fc5d94ebe2392 and its actual parent bee3e2e24e546545 produced different funded fills; changing only the manager also changed fills. All pilot P&L ledgers reconciled within $0.00001. The shadow bank contains 23 independently replayed candidate accounts.

Smoke actions: {'ENTRY': 318, 'ADD': 134, 'REDUCE': 97, 'EXIT': 230, 'REPLACE': 79}. Holds 1138; abstaining sessions 55; capital competition events 202; correlation rejections 133.

Frozen portfolio genes:

- trend single momentum; niche 2; hold momentum; exit trend; target 6%.
- relative_strength or momentum; niche 2; hold volatility; exit recursive; target 6%.
- volatility and recursive; niche 1; hold momentum; exit trend; target 6%.

Entry cap and total-risk sizing were exercised; total-risk hard rejection count was zero because the cash reserve bound first. Close weights can drift above the entry cap; the largest observed smoke close weight was 10.28%. This is a next-open risk-control model, not continuous intraday cap enforcement.

Stages A inventory, B implementation, C funded smoke, D bounded breeding and marginal ablations, E chronological folds, and F packaging were executed. This delivers an engineering pilot; it does not certify live execution parity or establish a survivor. See guardrails.json for trade-frequency, tail, concentration and fold-stability diagnostics.
