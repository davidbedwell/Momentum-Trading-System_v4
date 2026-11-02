# SPY ordered-state-transition study

Executed 2026-10-31. **Null incremental result:** this bounded damage → breadth recovery → price confirmation hypothesis does not establish improved 21- or 63-session return or forward drawdown forecasts. These are exploratory historical conditional-outcome comparisons, not untouched OOS, forecast calibration, trading profitability or causal treatment effects. All CSV return/drawdown effects are decimal fractions: 0.01 is one percentage point.

Confirmed-state mean returns were 0.56% at 21 sessions and 2.25% at 63 sessions, versus 2.25% and 4.92% for weak breadth alone on common eligibility. Price confirmation reduced mean return relative to the breadth-wait stage by 0.50 and 3.95 percentage points. Both differences are uncertain. Breadth recovery had a higher 63-session mean than damage, but did not establish incremental value over weak breadth. Pre-outcome protocol criteria: breadth: does not pass; confirmed: does not pass.

Weak breadth (<40% DEV79 above 50DMA) has historically accompanied larger subsequent SPY returns. That is a rebound association, **not proof of positive correlation between breadth level and future returns**. The ordered hypothesis neither overturns that distinction nor validates an original R1 implementation.

## Chronology and definitions
[PROTOCOL.md](PROTOCOL.md) was written before this study computed outcomes. [SOURCES.md](SOURCES.md) identifies the prior studies and original frozen protocols read. Damage requires current trailing 252-session SPY drawdown <=−10% and weak breadth. Breadth must subsequently improve >=10 points from its damage-declaration value, with five-session mean >=40%. On a still later session, price must be above EMA20 on >=4/5 sessions, with positive five-session return, rising EMA20 and nonincreasing RV20 over five sessions. These are newly fixed hypothesis thresholds, not original R1 rules. They omit external stress and directly measured failed rebounds.

The machine permits only one transition per session. Damage and breadth wait deadlines are 63 and 21 sessions; confirmation remains active for 21 sessions; all episodes expire within 126 sessions. Exact deadline transitions are allowed. Missing required features abort and produce missing state. A terminated episode must observe the damage gate false while idle before rearming. No future trough, later minimum or eventual recovery outcome initializes, resets or gates a declaration. Earlier stages include failed episodes; they are never filtered to successful conversions. States are exclusive, so a prior-stage contrast compares different dates and may reflect changing regimes/time since damage. It does not identify an isolated effect of waiting.

Across the full feature history there were 19 damage declarations, 18 breadth transitions and 14 confirmations. Only 14 completed confirmation declarations make the confirmed stage fragile. Exported history checks confirm strictly increasing transition timestamps; transition and state ledgers preserve anchor breadth and dates. Episodes may span year boundaries; forward labels may not.

## State outcomes
Mean adjusted-close forward return, negative-return probability and maximum close peak-to-trough drawdown include all eligible occupancy dates, not just declarations. The MDD path includes t..t+h and interim peaks. More positive drawdown effect means less loss. Same-close execution is not assumed; intraday losses are unobserved. Counts are daily dates, runs and greedily spaced h-session windows, none certified independent.
| stage | horizon | metric | n | onsets | nonoverlap_n | mean | baseline_mean | effect | ci_low | ci_high | q | bonferroni |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| damage | 21.00000 | return | 372.00000 | 19.00000 | 27.00000 | 0.00613 | 0.00990 | -0.00377 | -0.02892 | 0.02138 | 0.97177 | 1.00000 |
| damage | 21.00000 | downside | 372.00000 | 19.00000 | 27.00000 | 0.40591 | 0.32401 | 0.08191 | -0.05642 | 0.22024 | 0.79796 | 1.00000 |
| damage | 21.00000 | drawdown | 372.00000 | 19.00000 | 27.00000 | -0.08230 | -0.04064 | -0.04166 | -0.07104 | -0.01229 | 0.29387 | 1.00000 |
| breadth | 21.00000 | return | 155.00000 | 18.00000 | 22.00000 | 0.01065 | 0.00990 | 0.00075 | -0.03892 | 0.04041 | 0.99013 | 1.00000 |
| breadth | 21.00000 | downside | 155.00000 | 18.00000 | 22.00000 | 0.39355 | 0.32401 | 0.06954 | -0.15850 | 0.29758 | 0.91894 | 1.00000 |
| breadth | 21.00000 | drawdown | 155.00000 | 18.00000 | 22.00000 | -0.06981 | -0.04064 | -0.02917 | -0.05789 | -0.00045 | 0.44106 | 1.00000 |
| confirmed | 21.00000 | return | 277.00000 | 14.00000 | 14.00000 | 0.00561 | 0.00990 | -0.00429 | -0.02515 | 0.01656 | 0.96652 | 1.00000 |
| confirmed | 21.00000 | downside | 277.00000 | 14.00000 | 14.00000 | 0.35018 | 0.32401 | 0.02617 | -0.13661 | 0.18895 | 0.97177 | 1.00000 |
| confirmed | 21.00000 | drawdown | 277.00000 | 14.00000 | 14.00000 | -0.04917 | -0.04064 | -0.00853 | -0.02339 | 0.00633 | 0.81881 | 1.00000 |
| damage | 63.00000 | return | 323.00000 | 18.00000 | 18.00000 | 0.03303 | 0.02914 | 0.00389 | -0.05867 | 0.06645 | 0.97177 | 1.00000 |
| damage | 63.00000 | downside | 323.00000 | 18.00000 | 18.00000 | 0.26316 | 0.26624 | -0.00308 | -0.19697 | 0.19080 | 0.99013 | 1.00000 |
| damage | 63.00000 | drawdown | 323.00000 | 18.00000 | 18.00000 | -0.11569 | -0.07396 | -0.04173 | -0.08401 | 0.00055 | 0.45665 | 1.00000 |
| breadth | 63.00000 | return | 141.00000 | 16.00000 | 14.00000 | 0.06204 | 0.02914 | 0.03290 | -0.00196 | 0.06777 | 0.47093 | 1.00000 |
| breadth | 63.00000 | downside | 141.00000 | 16.00000 | 14.00000 | 0.16312 | 0.26624 | -0.10312 | -0.21615 | 0.00990 | 0.47093 | 1.00000 |
| breadth | 63.00000 | drawdown | 141.00000 | 16.00000 | 14.00000 | -0.09835 | -0.07396 | -0.02438 | -0.06044 | 0.01167 | 0.68393 | 1.00000 |
| confirmed | 63.00000 | return | 231.00000 | 12.00000 | 11.00000 | 0.02251 | 0.02914 | -0.00663 | -0.07172 | 0.05846 | 0.97177 | 1.00000 |
| confirmed | 63.00000 | downside | 231.00000 | 12.00000 | 11.00000 | 0.23377 | 0.26624 | -0.03248 | -0.24572 | 0.18077 | 0.97177 | 1.00000 |
| confirmed | 63.00000 | drawdown | 231.00000 | 12.00000 | 11.00000 | -0.09508 | -0.07396 | -0.02112 | -0.07262 | 0.03038 | 0.84409 | 1.00000 |

## Incremental comparisons
Each stage is compared with its immediate prior stage, weak breadth alone, positive 63-session SPY momentum, unconditional SPY, matched damage and an unordered same-date conjunction. Damage uses unconditional as its prior. All rows, including nulls and undefined sparse estimates, are in results.csv.
| stage | comparator | horizon | metric | n | effect | ci_low | ci_high | q | bonferroni |
|---|---|---|---|---|---|---|---|---|---|
| breadth | damage | 21.00000 | return | 155.00000 | 0.00452 | -0.04436 | 0.05340 | 0.97177 | 1.00000 |
| breadth | damage | 21.00000 | downside | 155.00000 | -0.01237 | -0.29314 | 0.26841 | 0.97177 | 1.00000 |
| breadth | damage | 21.00000 | drawdown | 155.00000 | 0.01249 | -0.02973 | 0.05471 | 0.92718 | 1.00000 |
| breadth | weak | 21.00000 | return | 155.00000 | -0.01183 | -0.05502 | 0.03136 | 0.93913 | 1.00000 |
| breadth | weak | 21.00000 | downside | 155.00000 | 0.10831 | -0.13671 | 0.35333 | 0.83117 | 1.00000 |
| breadth | weak | 21.00000 | drawdown | 155.00000 | -0.01225 | -0.04396 | 0.01945 | 0.84409 | 1.00000 |
| confirmed | breadth | 21.00000 | return | 277.00000 | -0.00504 | -0.05100 | 0.04092 | 0.97177 | 1.00000 |
| confirmed | breadth | 21.00000 | downside | 277.00000 | -0.04337 | -0.32639 | 0.23965 | 0.97177 | 1.00000 |
| confirmed | breadth | 21.00000 | drawdown | 277.00000 | 0.02064 | -0.01298 | 0.05427 | 0.75540 | 1.00000 |
| confirmed | weak | 21.00000 | return | 277.00000 | -0.01687 | -0.03747 | 0.00374 | 0.52432 | 1.00000 |
| confirmed | weak | 21.00000 | downside | 277.00000 | 0.06494 | -0.10563 | 0.23552 | 0.84409 | 1.00000 |
| confirmed | weak | 21.00000 | drawdown | 277.00000 | 0.00839 | -0.00954 | 0.02631 | 0.83117 | 1.00000 |
| breadth | damage | 63.00000 | return | 141.00000 | 0.02902 | -0.04220 | 0.10023 | 0.84409 | 1.00000 |
| breadth | damage | 63.00000 | downside | 141.00000 | -0.10004 | -0.31053 | 0.11046 | 0.83117 | 1.00000 |
| breadth | damage | 63.00000 | drawdown | 141.00000 | 0.01735 | -0.03424 | 0.06894 | 0.89145 | 1.00000 |
| breadth | weak | 63.00000 | return | 141.00000 | 0.01280 | -0.02455 | 0.05016 | 0.89145 | 1.00000 |
| breadth | weak | 63.00000 | downside | 141.00000 | -0.06358 | -0.18696 | 0.05980 | 0.83117 | 1.00000 |
| breadth | weak | 63.00000 | drawdown | 141.00000 | -0.00737 | -0.04510 | 0.03036 | 0.96652 | 1.00000 |
| confirmed | breadth | 63.00000 | return | 231.00000 | -0.03953 | -0.11051 | 0.03145 | 0.83117 | 1.00000 |
| confirmed | breadth | 63.00000 | downside | 231.00000 | 0.07065 | -0.14156 | 0.28285 | 0.89145 | 1.00000 |
| confirmed | breadth | 63.00000 | drawdown | 231.00000 | 0.00327 | -0.05542 | 0.06196 | 0.97177 | 1.00000 |
| confirmed | weak | 63.00000 | return | 231.00000 | -0.02673 | -0.08185 | 0.02839 | 0.83117 | 1.00000 |
| confirmed | weak | 63.00000 | downside | 231.00000 | 0.00706 | -0.17313 | 0.18725 | 0.97177 | 1.00000 |
| confirmed | weak | 63.00000 | drawdown | 231.00000 | -0.00410 | -0.04790 | 0.03970 | 0.97177 | 1.00000 |

The confirmed-state mean MDD is −4.92% at 21 and −9.51% at 63 sessions, compared with unconditional −4.06% and −7.40%. Relative to breadth-wait dates, drawdown improves by 2.06 points at 21 sessions but only 0.33 at 63; both intervals include zero. No robust lower-path-risk forecast follows from confirmation. Downside probabilities likewise do not establish incremental benefit.

## Matching and support
Controls are contemporaneous DAMAGE-state dates in the same calendar year, current drawdown bin and annualized RV20 bin. Exact strata are fixed; controls receive weights matching target-date stratum shares, with replacement. This uses no future data or eventual conversion. Year conditioning is retrospective sample control, not an online forecast estimator. Matching controls only coarse observed severity, not confounding. Unmatched targets are excluded only from this contrast; target support and every control weight appear in match_support.csv. Damage occupancy against matched damage is an identical-arm diagnostic with zero effect and undefined p-value.
| stage | horizon | metric | n | unmatched_n | baseline_n | baseline_effective_n | nonoverlap_n | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|---|---|---|
| breadth | 21.00000 | return | 108.00000 | 47.00000 | 203.00000 | 96.19990 | 18.00000 | 0.01219 | -0.02123 | 0.04561 | 0.87035 |
| breadth | 21.00000 | downside | 108.00000 | 47.00000 | 203.00000 | 96.19990 | 18.00000 | -0.09401 | -0.37223 | 0.18422 | 0.89145 |
| breadth | 21.00000 | drawdown | 108.00000 | 47.00000 | 203.00000 | 96.19990 | 18.00000 | 0.00845 | -0.00953 | 0.02642 | 0.83117 |
| confirmed | 21.00000 | return | 116.00000 | 161.00000 | 196.00000 | 46.60281 | 12.00000 | 0.01135 | -0.04907 | 0.07178 | 0.96652 |
| confirmed | 21.00000 | downside | 116.00000 | 161.00000 | 196.00000 | 46.60281 | 12.00000 | -0.03061 | -0.36601 | 0.30479 | 0.97177 |
| confirmed | 21.00000 | drawdown | 116.00000 | 161.00000 | 196.00000 | 46.60281 | 12.00000 | 0.02816 | -0.03597 | 0.09229 | 0.83117 |
| breadth | 63.00000 | return | 98.00000 | 43.00000 | 197.00000 | 88.87102 | 14.00000 | 0.03368 | -0.00947 | 0.07684 | 0.57649 |
| breadth | 63.00000 | downside | 98.00000 | 43.00000 | 197.00000 | 88.87102 | 14.00000 | -0.05192 | -0.28314 | 0.17929 | 0.96652 |
| breadth | 63.00000 | drawdown | 98.00000 | 43.00000 | 197.00000 | 88.87102 | 14.00000 | 0.02836 | -0.00250 | 0.05921 | 0.47093 |
| confirmed | 63.00000 | return | 111.00000 | 120.00000 | 179.00000 | 43.05965 | 10.00000 | -0.02094 | -0.11995 | 0.07808 | 0.96652 |
| confirmed | 63.00000 | downside | 111.00000 | 120.00000 | 179.00000 | 43.05965 | 10.00000 | 0.06933 | -0.17340 | 0.31206 | 0.93286 |
| confirmed | 63.00000 | drawdown | 111.00000 | 120.00000 | 179.00000 | 43.05965 | 10.00000 | 0.00479 | -0.08693 | 0.09652 | 0.97177 |

Most confirmed dates cannot be matched: 161/277 at horizon 21 and 120/231 at horizon 63. Matched results apply only to supported dates and cannot be generalized to all confirmations. Their return effects and MDD effects remain uncertain.

## Transition-date analysis
Pulses use the actual declaration dates. Prior-stage pulses are all earlier-stage declarations, including episodes that never reach the next stage. No paired successful-episode selection is performed. Small numbers make asymptotic intervals particularly unreliable.
| stage | horizon | metric | n | onsets | nonoverlap_n | mean | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | 21.00000 | return | 18.00000 | 18.00000 | 18.00000 | 0.00225 | -0.00765 | -0.03948 | 0.02418 | 0.96372 |
| damage | 21.00000 | downside | 18.00000 | 18.00000 | 18.00000 | 0.55556 | 0.23155 | 0.00845 | 0.45465 | 0.44106 |
| damage | 21.00000 | drawdown | 18.00000 | 18.00000 | 18.00000 | -0.08256 | -0.04192 | -0.07551 | -0.00833 | 0.29387 |
| breadth | 21.00000 | return | 18.00000 | 18.00000 | 18.00000 | 0.00095 | -0.00895 | -0.03114 | 0.01325 | 0.84409 |
| breadth | 21.00000 | downside | 18.00000 | 18.00000 | 18.00000 | 0.55556 | 0.23155 | 0.01140 | 0.45169 | 0.44106 |
| breadth | 21.00000 | drawdown | 18.00000 | 18.00000 | 18.00000 | -0.05749 | -0.01685 | -0.03482 | 0.00112 | 0.47093 |
| confirmed | 21.00000 | return | 13.00000 | 13.00000 | 13.00000 | 0.01337 | 0.00346 | -0.01842 | 0.02535 | 0.97177 |
| confirmed | 21.00000 | downside | 13.00000 | 13.00000 | 13.00000 | 0.46154 | 0.13753 | -0.11962 | 0.39469 | 0.83117 |
| confirmed | 21.00000 | drawdown | 13.00000 | 13.00000 | 13.00000 | -0.04124 | -0.00060 | -0.01641 | 0.01521 | 0.97177 |
| damage | 63.00000 | return | 17.00000 | 17.00000 | 15.00000 | 0.03187 | 0.00273 | -0.03708 | 0.04253 | 0.97177 |
| damage | 63.00000 | downside | 17.00000 | 17.00000 | 15.00000 | 0.23529 | -0.03095 | -0.23058 | 0.16868 | 0.97177 |
| damage | 63.00000 | drawdown | 17.00000 | 17.00000 | 15.00000 | -0.12478 | -0.05082 | -0.09013 | -0.01151 | 0.29387 |
| breadth | 63.00000 | return | 16.00000 | 16.00000 | 14.00000 | 0.01730 | -0.01184 | -0.05744 | 0.03375 | 0.93994 |
| breadth | 63.00000 | downside | 16.00000 | 16.00000 | 14.00000 | 0.37500 | 0.10876 | -0.13943 | 0.35694 | 0.83117 |
| breadth | 63.00000 | drawdown | 16.00000 | 16.00000 | 14.00000 | -0.10682 | -0.03286 | -0.06917 | 0.00346 | 0.47127 |
| confirmed | 63.00000 | return | 11.00000 | 11.00000 | 9.00000 | 0.02223 | -0.00691 | -0.07499 | 0.06117 | 0.97177 |
| confirmed | 63.00000 | downside | 11.00000 | 11.00000 | 9.00000 | 0.27273 | 0.00648 | -0.26037 | 0.27334 | 0.98693 |
| confirmed | 63.00000 | drawdown | 11.00000 | 11.00000 | 9.00000 | -0.09473 | -0.02076 | -0.07051 | 0.02898 | 0.84409 |

## Robustness
Window sizes and retention are fixed sensitivities, not ranked or selected. delay1 shifts all state/comparator indicators and matching covariates one trading session before attaching the current forward label; this is a delayed predictive observation, not a costed backtest. Crisis omissions exclude signal dates and all labels touching the omitted year because all labels are year-purged. Exact thresholds, rearming and abort behavior remain fixed. Full lag, damage-threshold, window, retention, delay, crisis and leave-one-year-out results are in robustness.csv.
| variant | horizon | n | nonoverlap_n | effect | ci_low | ci_high | q |
|---|---|---|---|---|---|---|---|
| wait42_10 | 21.00000 | 289.00000 | 15.00000 | -0.01014 | -0.03117 | 0.01089 | 0.82715 |
| wait42_10 | 63.00000 | 264.00000 | 13.00000 | -0.03057 | -0.08343 | 0.02228 | 0.77749 |
| wait84_42 | 21.00000 | 352.00000 | 18.00000 | -0.01592 | -0.03343 | 0.00159 | 0.48964 |
| wait84_42 | 63.00000 | 285.00000 | 14.00000 | -0.03068 | -0.07802 | 0.01666 | 0.70679 |
| retention10 | 21.00000 | 130.00000 | 13.00000 | -0.01284 | -0.03555 | 0.00988 | 0.78499 |
| retention10 | 63.00000 | 110.00000 | 9.00000 | -0.02535 | -0.08475 | 0.03406 | 0.84780 |
| retention42 | 21.00000 | 525.00000 | 26.00000 | -0.02406 | -0.04647 | -0.00165 | 0.43667 |
| retention42 | 63.00000 | 447.00000 | 11.00000 | -0.02750 | -0.06733 | 0.01233 | 0.66942 |
| damage15 | 21.00000 | 189.00000 | 9.00000 | -0.01113 | -0.03543 | 0.01317 | 0.82986 |
| damage15 | 63.00000 | 168.00000 | 8.00000 | -0.01134 | -0.08308 | 0.06039 | 0.98230 |
| delay1 | 21.00000 | 278.00000 | 14.00000 | -0.01775 | -0.03888 | 0.00338 | 0.53039 |
| delay1 | 63.00000 | 231.00000 | 11.00000 | -0.02551 | -0.08018 | 0.02917 | 0.82823 |
| omit_crises | 21.00000 | 172.00000 | 9.00000 | -0.01242 | -0.02768 | 0.00285 | 0.54876 |
| omit_crises | 63.00000 | 126.00000 | 6.00000 | 0.01572 | -0.00941 | 0.04085 | 0.72152 |
| omit_2008 | 21.00000 | 256.00000 | 13.00000 | -0.01674 | -0.03601 | 0.00254 | 0.51697 |
| omit_2008 | 63.00000 | 210.00000 | 10.00000 | -0.01037 | -0.05148 | 0.03075 | 0.94717 |
| omit_2009 | 21.00000 | 256.00000 | 13.00000 | -0.01698 | -0.03834 | 0.00439 | 0.56241 |
| omit_2009 | 63.00000 | 210.00000 | 10.00000 | -0.02630 | -0.08630 | 0.03370 | 0.83456 |
| omit_2020 | 21.00000 | 256.00000 | 13.00000 | -0.02066 | -0.04134 | 0.00002 | 0.46705 |
| omit_2020 | 63.00000 | 210.00000 | 10.00000 | -0.03217 | -0.09181 | 0.02747 | 0.81331 |
| omit_2022 | 21.00000 | 235.00000 | 12.00000 | -0.01051 | -0.03011 | 0.00909 | 0.81699 |
| omit_2022 | 63.00000 | 189.00000 | 9.00000 | -0.01344 | -0.07397 | 0.04709 | 0.96536 |
| lag126 | 21.00000 | 277.00000 | 14.00000 | -0.01687 | -0.03516 | 0.00142 | 0.48347 |
| lag126 | 63.00000 | 231.00000 | 11.00000 | -0.02673 | -0.08185 | 0.02839 | 0.82715 |

## Year-by-year historical stability
Annual results retain the fixed machine, without annual threshold fitting or rule selection. Each label must finish within its signal calendar year. All years 2006–2025, including empty years, are exported in annual_results.csv. They form chronological historical diagnostics; prior human inspection of 2017–2025 prevents an untouched OOS claim. Dates are sparse, years are dependent, and apparent sign consistency is not a significance test.
| year | horizon | n | nonoverlap_n | mean | baseline_mean | effect | ci_low | ci_high |
|---|---|---|---|---|---|---|---|---|
| 2006.00000 | 21.00000 | 0.00000 | 0.00000 | NA | 0.00867 | NA | NA | NA |
| 2006.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.05851 | NA | NA | NA |
| 2007.00000 | 21.00000 | 0.00000 | 0.00000 | NA | 0.03088 | NA | NA | NA |
| 2007.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.03795 | NA | NA | NA |
| 2008.00000 | 21.00000 | 21.00000 | 1.00000 | -0.09581 | -0.02564 | -0.07017 | -0.10569 | -0.03466 |
| 2008.00000 | 63.00000 | 21.00000 | 1.00000 | -0.31885 | -0.07654 | -0.24231 | -0.38028 | -0.10435 |
| 2009.00000 | 21.00000 | 21.00000 | 1.00000 | 0.04093 | 0.09824 | -0.05731 | -0.09410 | -0.02053 |
| 2009.00000 | 63.00000 | 21.00000 | 1.00000 | 0.09084 | 0.22850 | -0.13766 | -0.16991 | -0.10541 |
| 2010.00000 | 21.00000 | 42.00000 | 2.00000 | 0.01125 | 0.02899 | -0.01774 | -0.05726 | 0.02179 |
| 2010.00000 | 63.00000 | 38.00000 | 1.00000 | 0.09383 | 0.05916 | 0.03467 | 0.01017 | 0.05917 |
| 2011.00000 | 21.00000 | 21.00000 | 1.00000 | -0.00774 | 0.02088 | -0.02862 | -0.05430 | -0.00294 |
| 2011.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.01486 | NA | NA | NA |
| 2012.00000 | 21.00000 | 4.00000 | 1.00000 | 0.04992 | 0.02778 | NA | NA | NA |
| 2012.00000 | 63.00000 | 4.00000 | 1.00000 | 0.09910 | 0.07922 | NA | NA | NA |
| 2013.00000 | 21.00000 | 0.00000 | 0.00000 | NA | 0.04770 | NA | NA | NA |
| 2013.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.09296 | NA | NA | NA |
| 2014.00000 | 21.00000 | 0.00000 | 0.00000 | NA | 0.06672 | NA | NA | NA |
| 2014.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.07295 | NA | NA | NA |
| 2015.00000 | 21.00000 | 21.00000 | 1.00000 | 0.01343 | 0.02943 | -0.01599 | -0.03501 | 0.00302 |
| 2015.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.04070 | NA | NA | NA |
| 2016.00000 | 21.00000 | 21.00000 | 1.00000 | 0.03894 | 0.02233 | 0.01661 | 0.00067 | 0.03255 |
| 2016.00000 | 63.00000 | 21.00000 | 1.00000 | 0.05576 | 0.08585 | -0.03009 | -0.04588 | -0.01430 |
| 2017.00000 | 21.00000 | 0.00000 | 0.00000 | NA | NA | NA | NA | NA |
| 2017.00000 | 63.00000 | 0.00000 | 0.00000 | NA | NA | NA | NA | NA |
| 2018.00000 | 21.00000 | 21.00000 | 1.00000 | -0.00599 | -0.00103 | -0.00497 | -0.03199 | 0.02205 |
| 2018.00000 | 63.00000 | 21.00000 | 1.00000 | 0.03110 | 0.04248 | -0.01138 | -0.01629 | -0.00646 |
| 2019.00000 | 21.00000 | 21.00000 | 1.00000 | 0.04034 | 0.04985 | -0.00951 | -0.02623 | 0.00721 |
| 2019.00000 | 63.00000 | 21.00000 | 1.00000 | 0.08543 | 0.09180 | -0.00638 | -0.03592 | 0.02317 |
| 2020.00000 | 21.00000 | 21.00000 | 1.00000 | 0.06773 | 0.04472 | 0.02301 | -0.02526 | 0.07128 |
| 2020.00000 | 63.00000 | 21.00000 | 1.00000 | 0.15726 | 0.16422 | -0.00697 | -0.03329 | 0.01936 |
| 2021.00000 | 21.00000 | 0.00000 | 0.00000 | NA | 0.04889 | NA | NA | NA |
| 2021.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.07245 | NA | NA | NA |
| 2022.00000 | 21.00000 | 42.00000 | 2.00000 | -0.03017 | 0.02225 | -0.05242 | -0.11055 | 0.00572 |
| 2022.00000 | 63.00000 | 42.00000 | 2.00000 | -0.07123 | -0.00481 | -0.06642 | -0.10824 | -0.02460 |
| 2023.00000 | 21.00000 | 21.00000 | 1.00000 | 0.01044 | 0.02842 | -0.01798 | -0.04358 | 0.00763 |
| 2023.00000 | 63.00000 | 21.00000 | 1.00000 | 0.09986 | 0.08563 | 0.01422 | -0.00917 | 0.03762 |
| 2024.00000 | 21.00000 | 0.00000 | 0.00000 | NA | 0.05021 | NA | NA | NA |
| 2024.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.10189 | NA | NA | NA |
| 2025.00000 | 21.00000 | 0.00000 | 0.00000 | NA | 0.03304 | NA | NA | NA |
| 2025.00000 | 63.00000 | 0.00000 | 0.00000 | NA | 0.08629 | NA | NA | NA |

## Uncertainty and multiplicity
Marginal paired calendar influence-function HAC intervals use Bartlett lag max(63,2h), preserving zeros at calendar gaps and shared observations. Matching uses weighted control influence scores. At least five dates per arm are required for inference, but that is not an adequacy claim. Fewer than 20 runs or nonoverlap windows in either arm flags fragile. Small-event HAC can be overconfident and cannot repair retrospective hypothesis formation. BH is reported with limited guarantees under dependent tests; Bonferroni is the conservative dependence-robust adjustment. CIs are not simultaneous.

All 198 finite pooled tests across occupancy/pulses, stages, comparators, two horizons and three outcomes share one BH/Bonferroni family. All 732 finite annual contrasts share a separate family; all 5541 finite sensitivity contrasts share another. Undefined estimates remain NA. No significance is inferred from numerical residue in identical-arm contrasts.

Paired circular moving-block bootstrap uses 1000 fixed-seed replicates at 63/126 sessions for breadth and confirmation versus prior, weak and unconditional. It preserves within-block overlap but is also imperfect with few episodes; resamples with <5 dates per arm are discarded and counted. Intervals are marginal percentile intervals and not multiple-comparison adjusted. Matched results are not bootstrapped.
| horizon | metric | block | valid_replicates | ci_low | ci_high |
|---|---|---|---|---|---|
| 21.00000 | return | 63.00000 | 1000.00000 | -0.03938 | 0.00367 |
| 21.00000 | downside | 63.00000 | 1000.00000 | -0.10938 | 0.25990 |
| 21.00000 | drawdown | 63.00000 | 1000.00000 | -0.01050 | 0.02647 |
| 21.00000 | return | 126.00000 | 1000.00000 | -0.03920 | 0.00139 |
| 21.00000 | downside | 126.00000 | 1000.00000 | -0.10318 | 0.24690 |
| 21.00000 | drawdown | 126.00000 | 1000.00000 | -0.00990 | 0.02585 |
| 63.00000 | return | 63.00000 | 1000.00000 | -0.10312 | 0.02653 |
| 63.00000 | downside | 63.00000 | 1000.00000 | -0.17055 | 0.22574 |
| 63.00000 | drawdown | 63.00000 | 1000.00000 | -0.06220 | 0.03347 |
| 63.00000 | return | 126.00000 | 1000.00000 | -0.09523 | 0.03110 |
| 63.00000 | downside | 126.00000 | 1000.00000 | -0.17392 | 0.21775 |
| 63.00000 | drawdown | 126.00000 | 1000.00000 | -0.05975 | 0.03606 |

## Data and reproducibility
SPY and retrospective DEV79 adjusted closes are reused locally. Full input hashes, coverage, protocol/source/helper/test hashes and package versions are in run_metadata.json. data_quality.csv records missing cells and large moves without filtering. No forward fill or backfill is used. Every breadth observation needs complete trailing SMA50 prices per constituent and at least 20 eligible stocks. DEV79 has historical survivorship bias and prices have current-vintage adjustments: temporal code causality does not make the universe or vintage point-in-time correct. DEV87 is unavailable in prior work; no cross-universe replication or independent price certification is claimed.

Reproduce from the workspace:
```sh
/opt/mts/.venv/bin/python experiments/spy_recovery_sequence_20261031/study.py > experiments/spy_recovery_sequence_20261031/run.log 2>&1
/opt/mts/.venv/bin/python -m pytest -q experiments/spy_recovery_sequence_20261031/test_study.py > experiments/spy_recovery_sequence_20261031/tests.log 2>&1
/opt/mts/.venv/bin/python experiments/spy_recovery_sequence_20261031/report.py
```
Tests cover future perturbation, prefix invariance, strict ordering, inclusive deadlines, expiry/rearming, hard cap, missing data, delayed state alignment, drawdown arithmetic, year purging, matching weights/support, paired inference and identical-arm numerical handling. report.py additionally audits exported ordering and identical-arm outputs. Execution is bounded local research; no GA, paid data, MTS edits, other-project edits or long certification. Artifacts include features, signals, state_history, transitions, outcomes, results, annual_results, robustness, bootstrap, match_support, data_quality, run_metadata, run.log and tests.log.
