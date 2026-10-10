# A/B/C earlier-cash-entry research — benchmark-preserving plan

Status: RESEARCH PROPOSAL ONLY; no detector or R-1 policy changes authorized or deployed.

## Baseline
Preserve the original October 5 A/B/C OR state detector and R-1 exactly. Baseline replay: 12 entries, 12 exits, 1,532 Defensive sessions, 5,282 sessions. Original 2008 entry 2008-10-10, 2020 entry 2020-03-09, 2022 entry 2022-01-07. Existing state tape SHA-256 e827b8beed7d3a0a0512990b5c77eb94618fb52f8739695f16509008f1f920fe. Do not use DEV37, DEV50, BLIND17 or Verification A/B for design.

## Mechanism-specific hypotheses (not preapproved changes)
- A, rapid shock: strict 4-of-4 stress concurrence for five sessions is inherently slow and requires funding and VVIX confirmation. Test causally staged price/volatility early warning followed by confirmation, with explicit false-positive accounting.
- B, slow deterioration: the 40-session negative-day fraction plus OFR funding change may be insensitive early in credit-led bear markets and OFR has a two-business-day lag. Test independent trend/breadth early-warning triggers without look-ahead or removal of lag.
- C, grinding decline: four simultaneous extreme-percentile conditions and three-session confirmation can miss prolonged deterioration. Test persistent breadth/failed-rebound deterioration with explicitly specified nuisance-episode and drawdown penalties.
- R-1: keep frozen for the entry study, but report premature recovery and separate exit audit. Do not quietly improve entries by changing exits.

## Evaluation contract
Use SPY unadjusted closes for transparent index-proxy drawdowns; additionally assess adjusted prices for total-return cash-vs-hold comparisons. PIT market breadth, VIX, VVIX and correctly lagged OFR are separate inputs. Declare full crash episodes and matched noncrash controls *before* candidate tuning. Evaluate episode-level coverage, time-in-cash, avoided downside, missed upside, false alarms, and realistic next-session executions; include 2008, 2020, 2022, 2010, 2011, 2015-16, 2018, and other discovered episodes. Separate discovery and independent market-episode validation; shared ticker histories do not make episodes independent. Evaluate 2008 and 2022 failures, not merely pooled daily fitness. Use costs and historical T-bill cash return where available. Preserve original baseline and reproducible data lineage. No deployment or scientific certification without prospective thresholds and independent evidence.

## Current blocker
The historical A/B/C state tape was recovered from /home/ubuntu/Momentum-Trading-System_v4/Research/State; raw VIX, VVIX and OFR are present in that separate checkout, but the current checkout does not contain the derived feature tape. Reconstruct and checksum it without editing the protected frozen baseline.
