# MTS v4 Capital Sizing — Verification A2 Result — 2026-10-02

## Frozen result
**VERIFICATION_A2_FAILED** under the prospectively frozen all-criteria gate.

A2 used exactly 20 prospectively assigned names from the pre-existing 80-name Verification-A remainder manifest. The other 60 remained sequestered as MACHINE-ACCESSED / RESEARCHER-BLINDED. Verification B was not accessed.

## Metrics
| Metric | Equal sizing | Frozen sizing | Exposure-matched equal |
|---|---:|---:|---:|
| Terminal wealth | 15.757743x | 16.052861x | 14.955228x |
| CAGR-equivalent | 14.0316% | 14.1324% | 13.7482% |
| Max drawdown | -53.0479% | -53.1937% | -53.0241% |
| Daily CVaR5 | -3.28144% | -3.29173% | -3.28211% |
| Avg gross exposure | 96.5688% | 96.8692% | 96.8692% |

Frozen sizing terminal wealth was +1.8728% relative to ordinary equal sizing and +7.3395% relative to the exposure-matched equal baseline. CAGR improved by +0.1008 percentage points versus ordinary equal sizing.

Max drawdown worsened by 0.1457 percentage points and daily CVaR5 worsened by 0.0103 percentage points versus ordinary equal sizing.

Ticker breadth was 2/20 positive (10%).

## Frozen criteria
- Wealth > ordinary equal sizing: PASS
- Wealth > exposure-matched equal sizing: PASS
- Max drawdown no worse: FAIL
- CVaR5 no worse: FAIL
- Positive sizing contribution on >50% of usable tickers: FAIL (2/20)

## Scientific interpretation
The frozen sizing rule retained a positive aggregate wealth effect in A2, including after matching average gross exposure, but did not generalize broadly across tickers and did not preserve the frozen downside-risk requirements. The aggregate wealth improvement therefore does not satisfy the precommitted validation standard.

No rescue threshold, retuning, or post-result policy modification is permitted inside A2. Any investigation of why aggregate wealth improved despite 2/20 positive ticker contributions is a new Discovery question and must not consume the sequestered 60 or Verification B.

## Integrity
- A2 target count: 20
- Verification trades: 672,697
- Score sources: genome 564,583; family 105,606; global 1,562; unavailable/neutral 946
- Search: false
- Retune: false
- Verification B accessed: false
