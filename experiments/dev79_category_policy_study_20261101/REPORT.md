# DEV79 category-conditioned management — measured Phase 1

Completed one real-OHLCV replay of the existing four policies. No selector fitted, no policy switching, no production changes. Claude, Gemini and Grok DEV79 implementations are approximations; exact Claude/Grok source was unavailable. State rules, split, horizon, benchmark and uncertainty procedure were frozen in [PROTOCOL.md](PROTOCOL.md) before execution.

## Interpretation

No category policy winner is established. Same-date/ticker matching removes different opportunity sets, but inventory, sizing, cash, turnover and earlier decisions remain policy-dependent. The primary result is a local one-session incremental management contribution versus holding the pre-execution inventory. It is not a counterfactual full portfolio, a category NAV, a long-horizon realized alpha estimate or a causal treatment effect. Realized sell PnL is reported separately and includes cost basis from previous states. Portfolio-level results below are replay parity context, not category evidence.

## Main measured findings

Matched coverage is 329,927 / 351,629 opportunities per policy (93.83%). Later-segment local incremental dollars against hold are below. These sums use each historical portfolio’s actual size, so their dollar levels are not directly comparable policy skill estimates. All four are negative at this one-session horizon; this does not imply all trades were harmful over their full holding periods.

| policy | local_incremental_dollars | fees_all_fills |
| --- | --- | --- |
| manager | -19192.6322 | 11493.0255 |
| claude_approx | -72879.5905 | 42268.8346 |
| gemini_approx | -77958.3423 | 48498.3593 |
| grok_dev79_approx | -8423.2572 | 1994.7063 |

Of 30 later-segment known-state pair contrasts, 1 has a family-adjusted interval excluding zero: Gemini approximation minus Grok DEV79 approximation in consolidation, -0.5069 basis points of NAV per decision day, interval [-1.8673, -0.0231]. This remains exposure/turnover/path-confounded and does not establish a category winner. All six later uptrend family-adjusted intervals include zero. Discovery differences therefore do not justify an uptrend selector.

Later-segment common all-four-flat known-state opportunities: zero. All-four-held support in deterioration is one opportunity and reversal is 42. These cannot identify an entry/exit winner. There is no category selector or retrospective switching.

## Actual replay context

| policy | final_nav | return_pct | mean_exposure_pct | fees | fills |
| --- | --- | --- | --- | --- | --- |
| manager | 95981.9940 | -4.0180 | 46.3312 | 36601.4188 | 18944 |
| claude_approx | 322734.4402 | 222.7344 | 67.4776 | 74863.9208 | 46061 |
| gemini_approx | 948380.9006 | 848.3809 | 96.1031 | 67566.9949 | 157562 |
| grok_dev79_approx | 1240500.4384 | 1140.5004 | 91.8967 | 2568.5167 | 15521 |

## State and matched coverage

Categories at decision close t use only data through t-1. Priority is reversal, deterioration, acceleration, uptrend, then residual consolidation; unknown requires more history. Exact formulas are in the protocol. Consolidation is deliberately an exhaustive residual, not solely a low-volatility range. No verified sector time series/membership was established: relative strength uses the local SPY close archive. SPY is price-only and was checked for unique dates, positive closes and session coverage; it is not independently vendor-certified.

| segment | category | opportunities | matched | all_flat | all_held |
| --- | --- | --- | --- | --- | --- |
| discovery | acceleration | 11005 | 11003 | 1 | 1762 |
| discovery | consolidation | 34304 | 34256 | 17 | 683 |
| discovery | deterioration | 49588 | 49560 | 7 | 3 |
| discovery | reversal | 9610 | 9608 | 18 | 50 |
| discovery | unknown | 19762 | 765 | 19132 | 0 |
| discovery | uptrend | 54666 | 54592 | 19 | 6487 |
| test | acceleration | 10417 | 10413 | 0 | 1711 |
| test | consolidation | 34523 | 34505 | 0 | 663 |
| test | deterioration | 60399 | 60317 | 0 | 1 |
| test | reversal | 11065 | 11063 | 0 | 42 |
| test | unknown | 2495 | 102 | 2410 | 0 |
| test | uptrend | 53795 | 53743 | 0 | 6182 |

SPY missing on replay sessions: 0. Each policy has 351,629 date/ticker opportunities; 329,927 meet the common horizon/price/split rules. Missing/listing and boundary/terminal outcomes remain excluded, never filled with synthetic prices. All unknown categories remain separately recorded.

## Category management measurements

Exposure columns are mean contributions to total portfolio NAV over all segment days. Incremental dollars are the sum of actual-sized one-session action outcomes net of fees/slippage against unchanged pre-execution shares; they are not terminal wealth. Fees and realized PnL include every actual fill attributed by its signal category, including fills lacking a complete forward horizon. Action counts are actual filled entry/add/reduce/exit counts, distinguished from intentions in the CSV. Price returns exclude dividends.

| segment | category | policy | matched_opportunities | mean_pre_exposure | mean_post_exposure | incremental_pnl | realized_pnl_all_fills | fees_all_fills | filled_enter | filled_add | filled_reduce | filled_exit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| discovery | acceleration | manager | 11003 | 0.1287 | 0.1251 | -715.0356 | 8237.1746 | 3609.3983 | 426 | 302 | 299 | 555 |
| discovery | consolidation | manager | 34256 | 0.0578 | 0.0713 | -6647.6780 | -13218.4601 | 5447.9290 | 1141 | 121 | 95 | 605 |
| discovery | deterioration | manager | 49560 | 0.0004 | 0.0035 | 1511.2591 | 575.3045 | 386.6117 | 141 | 3 | 1 | 6 |
| discovery | reversal | manager | 9608 | 0.0085 | 0.0085 | -697.2468 | -1865.8308 | 494.5651 | 89 | 25 | 20 | 82 |
| discovery | unknown | manager | 765 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 |
| discovery | uptrend | manager | 54592 | 0.4363 | 0.4229 | -44760.3588 | 7465.2509 | 15169.8892 | 1890 | 1189 | 1019 | 2429 |
| test | acceleration | manager | 10413 | 0.0634 | 0.0613 | -2552.9382 | 6286.4506 | 1588.8611 | 417 | 125 | 189 | 526 |
| test | consolidation | manager | 34505 | 0.0310 | 0.0381 | -4702.8514 | -9436.0046 | 2658.5428 | 1045 | 42 | 77 | 571 |
| test | deterioration | manager | 60317 | 0.0002 | 0.0021 | -901.2418 | -933.5603 | 232.6465 | 131 | 0 | 1 | 10 |
| test | reversal | manager | 11063 | 0.0047 | 0.0046 | -330.3533 | -291.5746 | 254.9320 | 81 | 16 | 20 | 76 |
| test | unknown | manager | 102 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 |
| test | uptrend | manager | 53743 | 0.2177 | 0.2101 | -10705.2475 | -1130.0310 | 6758.0431 | 1774 | 546 | 594 | 2265 |
| discovery | acceleration | claude_approx | 11003 | 0.0966 | 0.0945 | -9813.9543 | 40604.6021 | 3126.1028 | 227 | 1130 | 1199 | 290 |
| discovery | consolidation | claude_approx | 34256 | 0.1385 | 0.1386 | -23842.2166 | -10129.0274 | 7728.5549 | 652 | 1630 | 1921 | 648 |
| discovery | deterioration | claude_approx | 49560 | 0.0778 | 0.0817 | -14364.4901 | -103399.2349 | 6372.3410 | 609 | 844 | 1071 | 475 |
| discovery | reversal | claude_approx | 9608 | 0.0233 | 0.0230 | -1554.0127 | -1758.0542 | 1039.6470 | 81 | 237 | 256 | 91 |
| discovery | unknown | claude_approx | 765 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 |
| discovery | uptrend | claude_approx | 54592 | 0.3588 | 0.3571 | -28669.7809 | 155585.4998 | 14328.4405 | 1178 | 4497 | 5127 | 1233 |
| test | acceleration | claude_approx | 10413 | 0.0969 | 0.0961 | -6841.5728 | 92469.0438 | 4181.6037 | 259 | 1029 | 1198 | 282 |
| test | consolidation | claude_approx | 34505 | 0.1318 | 0.1338 | -27821.2903 | -66868.3767 | 9299.6362 | 659 | 1493 | 1816 | 600 |
| test | deterioration | claude_approx | 60317 | 0.0769 | 0.0793 | -20628.3905 | -155138.9013 | 8080.5214 | 583 | 831 | 938 | 504 |
| test | reversal | claude_approx | 11063 | 0.0237 | 0.0237 | -2196.1121 | 3730.8970 | 1287.0140 | 88 | 201 | 314 | 86 |
| test | unknown | claude_approx | 102 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 |
| test | uptrend | claude_approx | 53743 | 0.3598 | 0.3559 | -15392.2249 | 254021.2265 | 19420.0594 | 1219 | 4228 | 5001 | 1336 |
| discovery | acceleration | gemini_approx | 11003 | 0.1189 | 0.1199 | -2239.3083 | 79276.8820 | 1309.8373 | 75 | 3696 | 4844 | 7 |
| discovery | consolidation | gemini_approx | 34256 | 0.2487 | 0.2482 | -5662.5741 | 115310.5914 | 3479.9079 | 283 | 9072 | 11392 | 249 |
| discovery | deterioration | gemini_approx | 49560 | 0.1439 | 0.1324 | -18581.0858 | -197328.4178 | 6022.5267 | 136 | 5390 | 3728 | 1422 |
| discovery | reversal | gemini_approx | 9608 | 0.0158 | 0.0170 | 2131.8677 | 11762.6745 | 550.7717 | 136 | 383 | 573 | 16 |
| discovery | unknown | gemini_approx | 765 | 0.0001 | 0.0002 | -453.3220 | -4.2768 | 28.7720 | 9 | 3 | 3 | 0 |
| discovery | uptrend | gemini_approx | 54592 | 0.4529 | 0.4632 | -18935.7843 | 271097.5114 | 7676.8200 | 1137 | 15419 | 20588 | 19 |
| test | acceleration | gemini_approx | 10413 | 0.1140 | 0.1148 | 12603.5511 | 249085.6761 | 3244.1279 | 75 | 3400 | 4793 | 6 |
| test | consolidation | gemini_approx | 34505 | 0.2479 | 0.2480 | -45829.8042 | 307520.1534 | 9028.5681 | 304 | 9169 | 11039 | 274 |
| test | deterioration | gemini_approx | 60317 | 0.1640 | 0.1504 | -27962.6286 | -763001.4921 | 16178.5119 | 152 | 6187 | 4296 | 1587 |
| test | reversal | gemini_approx | 11063 | 0.0155 | 0.0168 | -375.0899 | 24473.4295 | 1398.6367 | 147 | 425 | 608 | 18 |
| test | unknown | gemini_approx | 102 | 0.0000 | 0.0000 | 380.2053 | 0.0000 | 7.4623 | 1 | 1 | 0 | 0 |
| test | uptrend | gemini_approx | 53743 | 0.4383 | 0.4498 | -16774.5760 | 699251.5135 | 18641.0524 | 1220 | 15235 | 20017 | 28 |
| discovery | acceleration | grok_dev79_approx | 11003 | 0.0703 | 0.0701 | -12.6893 | 35230.3090 | 51.8167 | 1 | 46 | 562 | 0 |
| discovery | consolidation | grok_dev79_approx | 34256 | 0.1868 | 0.1870 | 55.5469 | 9384.3536 | 72.4097 | 17 | 1147 | 484 | 0 |
| discovery | deterioration | grok_dev79_approx | 49560 | 0.2639 | 0.2646 | 214.6978 | 3634.4328 | 193.6368 | 7 | 2032 | 327 | 0 |
| discovery | reversal | grok_dev79_approx | 9608 | 0.0663 | 0.0665 | 140.4565 | 4573.9614 | 35.0236 | 18 | 289 | 167 | 0 |
| discovery | unknown | grok_dev79_approx | 765 | 0.0034 | 0.0035 | -196.7828 | 260.0122 | 21.6133 | 15 | 12 | 10 | 0 |
| discovery | uptrend | grok_dev79_approx | 54592 | 0.3078 | 0.3072 | -1105.5421 | 123141.2891 | 199.3102 | 19 | 270 | 2197 | 0 |
| test | acceleration | grok_dev79_approx | 10413 | 0.0703 | 0.0699 | 2078.9902 | 184831.4432 | 238.7145 | 0 | 87 | 622 | 0 |
| test | consolidation | grok_dev79_approx | 34505 | 0.1952 | 0.1953 | -792.0608 | 43589.9264 | 241.4680 | 0 | 990 | 574 | 0 |
| test | deterioration | grok_dev79_approx | 60317 | 0.3299 | 0.3308 | -287.7385 | 18486.0571 | 765.6822 | 0 | 2331 | 463 | 0 |
| test | reversal | grok_dev79_approx | 11063 | 0.0737 | 0.0737 | -1141.0517 | 17266.9071 | 105.8048 | 0 | 312 | 236 | 0 |
| test | unknown | grok_dev79_approx | 102 | 0.0006 | 0.0006 | -271.9947 | 198.2505 | 11.2672 | 2 | 1 | 2 | 0 |
| test | uptrend | grok_dev79_approx | 53743 | 0.3150 | 0.3142 | -8009.4017 | 406283.3086 | 631.7695 | 0 | 292 | 1989 | 0 |

## Matched contrasts and uncertainty

Each effect is policy a minus b in basis points of NAV per calendar decision day: sum the paired ticker contributions in that category, include zero category-absent days, then average. Thus it combines actual sizing and opportunity frequency; it is not per-trade return. Calendar-month block bootstrap, seed 79, 2,000 draws, preserves contemporaneous stock dependence. 95% and family-adjusted 99.8333% intervals are descriptive, conditional on this archive and policy paths. Monte Carlo tail resolution is limited with 2,000 draws; no exact significance claim. Family adjustment covers 30 comparisons per segment for the five defined states; unknown is diagnostic.

| segment | category | a | b | discordant_actions | discordant_months | mean_daily_bps | ci95_low_bps | ci95_high_bps | family_low_bps | family_high_bps | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| discovery | acceleration | manager | claude_approx | 3507 | 108 | 0.2333 | -0.1785 | 0.6521 | -0.4082 | 0.9958 | descriptive_path_confounded |
| discovery | acceleration | manager | gemini_approx | 8457 | 108 | 0.0246 | -0.3099 | 0.3773 | -0.4677 | 0.5960 | descriptive_path_confounded |
| discovery | acceleration | manager | grok_dev79_approx | 2039 | 108 | -0.0250 | -0.3482 | 0.3166 | -0.4936 | 0.5175 | descriptive_path_confounded |
| discovery | acceleration | claude_approx | gemini_approx | 7788 | 108 | -0.2087 | -0.4879 | 0.0561 | -0.6360 | 0.2038 | descriptive_path_confounded |
| discovery | acceleration | claude_approx | grok_dev79_approx | 3202 | 108 | -0.2583 | -0.5393 | 0.0058 | -0.6895 | 0.1458 | descriptive_path_confounded |
| discovery | acceleration | gemini_approx | grok_dev79_approx | 8539 | 108 | -0.0497 | -0.1428 | 0.0484 | -0.2015 | 0.0878 | descriptive_path_confounded |
| discovery | uptrend | manager | claude_approx | 14765 | 108 | -1.1767 | -1.8782 | -0.4576 | -2.3824 | -0.0807 | descriptive_path_confounded |
| discovery | uptrend | manager | gemini_approx | 36860 | 108 | -1.6021 | -2.1765 | -1.0025 | -2.5564 | -0.6324 | descriptive_path_confounded |
| discovery | uptrend | manager | grok_dev79_approx | 8505 | 108 | -1.9167 | -2.4155 | -1.4141 | -2.7089 | -0.9649 | descriptive_path_confounded |
| discovery | uptrend | claude_approx | gemini_approx | 34658 | 108 | -0.4254 | -1.0306 | 0.1887 | -1.3784 | 0.5697 | descriptive_path_confounded |
| discovery | uptrend | claude_approx | grok_dev79_approx | 13670 | 108 | -0.7400 | -1.2685 | -0.2160 | -1.5560 | -0.0128 | descriptive_path_confounded |
| discovery | uptrend | gemini_approx | grok_dev79_approx | 36989 | 108 | -0.3146 | -0.6107 | -0.0532 | -0.7989 | 0.1056 | descriptive_path_confounded |
| discovery | consolidation | manager | claude_approx | 5779 | 108 | 0.3698 | -0.1443 | 0.8647 | -0.4347 | 1.0937 | descriptive_path_confounded |
| discovery | consolidation | manager | gemini_approx | 20737 | 108 | -0.2250 | -0.6271 | 0.1714 | -0.8066 | 0.3818 | descriptive_path_confounded |
| discovery | consolidation | manager | grok_dev79_approx | 3443 | 108 | -0.3149 | -0.6696 | 0.0532 | -0.9118 | 0.2144 | descriptive_path_confounded |
| discovery | consolidation | claude_approx | gemini_approx | 20310 | 108 | -0.5948 | -1.0215 | -0.1862 | -1.2403 | 0.0237 | descriptive_path_confounded |
| discovery | consolidation | claude_approx | grok_dev79_approx | 6105 | 108 | -0.6848 | -1.1121 | -0.2731 | -1.3346 | -0.0564 | descriptive_path_confounded |
| discovery | consolidation | gemini_approx | grok_dev79_approx | 21035 | 108 | -0.0900 | -0.2335 | 0.0671 | -0.2949 | 0.1601 | descriptive_path_confounded |
| discovery | deterioration | manager | claude_approx | 3070 | 103 | 0.4250 | -0.0818 | 0.9331 | -0.3053 | 1.3295 | descriptive_path_confounded |
| discovery | deterioration | manager | gemini_approx | 10708 | 108 | 0.4231 | 0.1458 | 0.7419 | -0.0082 | 0.9451 | descriptive_path_confounded |
| discovery | deterioration | manager | grok_dev79_approx | 2511 | 108 | 0.0695 | -0.0754 | 0.2465 | -0.1394 | 0.3912 | descriptive_path_confounded |
| discovery | deterioration | claude_approx | gemini_approx | 11717 | 108 | -0.0019 | -0.5610 | 0.5908 | -0.8582 | 0.8924 | descriptive_path_confounded |
| discovery | deterioration | claude_approx | grok_dev79_approx | 5156 | 108 | -0.3555 | -0.8973 | 0.1842 | -1.2450 | 0.4224 | descriptive_path_confounded |
| discovery | deterioration | gemini_approx | grok_dev79_approx | 12292 | 108 | -0.3536 | -0.6199 | -0.1176 | -0.8162 | 0.0397 | descriptive_path_confounded |
| discovery | reversal | manager | claude_approx | 794 | 97 | -0.0010 | -0.1814 | 0.1704 | -0.3505 | 0.2862 | descriptive_path_confounded |
| discovery | reversal | manager | gemini_approx | 1209 | 108 | -0.0819 | -0.1897 | 0.0197 | -0.2642 | 0.0805 | descriptive_path_confounded |
| discovery | reversal | manager | grok_dev79_approx | 675 | 100 | -0.0486 | -0.1414 | 0.0420 | -0.2042 | 0.0943 | descriptive_path_confounded |
| discovery | reversal | claude_approx | gemini_approx | 1532 | 108 | -0.0809 | -0.2347 | 0.0803 | -0.3348 | 0.2018 | descriptive_path_confounded |
| discovery | reversal | claude_approx | grok_dev79_approx | 1101 | 106 | -0.0476 | -0.1949 | 0.1070 | -0.2697 | 0.2232 | descriptive_path_confounded |
| discovery | reversal | gemini_approx | grok_dev79_approx | 1510 | 108 | 0.0333 | -0.0180 | 0.0955 | -0.0531 | 0.1263 | descriptive_path_confounded |
| test | acceleration | manager | claude_approx | 3298 | 105 | -0.0393 | -0.3577 | 0.2643 | -0.5321 | 0.4107 | descriptive_path_confounded |
| test | acceleration | manager | gemini_approx | 8173 | 105 | -0.2645 | -0.5273 | -0.0131 | -0.6659 | 0.1183 | descriptive_path_confounded |
| test | acceleration | manager | grok_dev79_approx | 1842 | 105 | -0.1204 | -0.3139 | 0.0831 | -0.4382 | 0.1786 | descriptive_path_confounded |
| test | acceleration | claude_approx | gemini_approx | 7386 | 105 | -0.2252 | -0.5640 | 0.0948 | -0.7787 | 0.2564 | descriptive_path_confounded |
| test | acceleration | claude_approx | grok_dev79_approx | 3194 | 105 | -0.0811 | -0.3724 | 0.2163 | -0.5313 | 0.3894 | descriptive_path_confounded |
| test | acceleration | gemini_approx | grok_dev79_approx | 8110 | 105 | 0.1441 | -0.0009 | 0.3413 | -0.0515 | 0.4687 | descriptive_path_confounded |
| test | uptrend | manager | claude_approx | 14158 | 105 | -0.0942 | -0.7235 | 0.5654 | -0.9973 | 1.0079 | descriptive_path_confounded |
| test | uptrend | manager | gemini_approx | 36389 | 105 | -0.4127 | -0.8290 | 0.0099 | -1.0127 | 0.2046 | descriptive_path_confounded |
| test | uptrend | manager | grok_dev79_approx | 7038 | 105 | -0.4547 | -0.7830 | -0.1275 | -0.9488 | 0.0070 | descriptive_path_confounded |
| test | uptrend | claude_approx | gemini_approx | 34104 | 105 | -0.3185 | -0.9554 | 0.3382 | -1.3747 | 0.6479 | descriptive_path_confounded |
| test | uptrend | claude_approx | grok_dev79_approx | 13315 | 105 | -0.3605 | -0.9526 | 0.2197 | -1.3649 | 0.5838 | descriptive_path_confounded |
| test | uptrend | gemini_approx | grok_dev79_approx | 36554 | 105 | -0.0420 | -0.3091 | 0.2245 | -0.5161 | 0.3790 | descriptive_path_confounded |
| test | consolidation | manager | claude_approx | 5420 | 105 | 0.3853 | -0.1433 | 0.8791 | -0.3510 | 1.1686 | descriptive_path_confounded |
| test | consolidation | manager | gemini_approx | 20687 | 105 | 0.2891 | -0.2813 | 1.2095 | -0.4376 | 1.9313 | descriptive_path_confounded |
| test | consolidation | manager | grok_dev79_approx | 3182 | 105 | -0.2178 | -0.4448 | 0.0188 | -0.5581 | 0.1237 | descriptive_path_confounded |
| test | consolidation | claude_approx | gemini_approx | 20267 | 105 | -0.0962 | -0.7838 | 0.8186 | -1.1120 | 1.4370 | descriptive_path_confounded |
| test | consolidation | claude_approx | grok_dev79_approx | 5790 | 105 | -0.6031 | -1.0816 | -0.1144 | -1.3651 | 0.1039 | descriptive_path_confounded |
| test | consolidation | gemini_approx | grok_dev79_approx | 20964 | 105 | -0.5069 | -1.2496 | -0.0896 | -1.8673 | -0.0231 | descriptive_path_confounded |
| test | deterioration | manager | claude_approx | 2928 | 99 | 0.4645 | -0.2539 | 1.1611 | -0.6644 | 1.7805 | descriptive_path_confounded |
| test | deterioration | manager | gemini_approx | 12275 | 105 | 0.1770 | -0.0852 | 0.4297 | -0.2119 | 0.5490 | descriptive_path_confounded |
| test | deterioration | manager | grok_dev79_approx | 2919 | 105 | -0.0444 | -0.1322 | 0.0429 | -0.2026 | 0.0882 | descriptive_path_confounded |
| test | deterioration | claude_approx | gemini_approx | 13247 | 105 | -0.2876 | -1.0432 | 0.4453 | -1.5759 | 0.8798 | descriptive_path_confounded |
| test | deterioration | claude_approx | grok_dev79_approx | 5433 | 105 | -0.5089 | -1.1893 | 0.1999 | -1.8195 | 0.5997 | descriptive_path_confounded |
| test | deterioration | gemini_approx | grok_dev79_approx | 14103 | 105 | -0.2214 | -0.4707 | 0.0300 | -0.5538 | 0.1754 | descriptive_path_confounded |
| test | reversal | manager | claude_approx | 793 | 94 | 0.0552 | -0.1437 | 0.2632 | -0.2323 | 0.4005 | descriptive_path_confounded |
| test | reversal | manager | gemini_approx | 1302 | 104 | 0.0062 | -0.1122 | 0.1403 | -0.1737 | 0.2270 | descriptive_path_confounded |
| test | reversal | manager | grok_dev79_approx | 724 | 95 | -0.0079 | -0.0928 | 0.0798 | -0.1442 | 0.1356 | descriptive_path_confounded |
| test | reversal | claude_approx | gemini_approx | 1659 | 105 | -0.0489 | -0.2578 | 0.1573 | -0.3684 | 0.2446 | descriptive_path_confounded |
| test | reversal | claude_approx | grok_dev79_approx | 1184 | 103 | -0.0630 | -0.2593 | 0.1264 | -0.3731 | 0.2110 | descriptive_path_confounded |
| test | reversal | gemini_approx | grok_dev79_approx | 1665 | 104 | -0.0141 | -0.1031 | 0.0684 | -0.1534 | 0.1157 | descriptive_path_confounded |

Insufficient support means fewer than 100 discordant executed-direction opportunities or 24 discordant calendar months. Other rows remain descriptive and path-confounded even when an interval excludes zero. All-four-flat and all-four-held matched support is in matched_contrasts.csv; empty or small strata cannot identify the relative quality of an entry or exit rule. No category selector is warranted by these diagnostics alone, and none was preregistered or run.

## Chronology, limitations and audit

Discovery is 2009–2017; later descriptive test is 2018–2026-09-14, with horizons crossing the split embargoed. No state thresholds or policies were tuned on test. Prior work examined these policies and history, so this later period is not an untouched prospective holdout for policy discovery. No claim of independent OOS alpha.

DEV79 is a retrospective fixed-survivor archive, not point-in-time membership. Historical revisions and present-day split adjustment may restate earlier prices; no independent vendor receipts/as-of publication timestamps. Split-adjusted price treatment inherits the prior audit, no double share adjustment. No dividends, merger/delisting cashflow reconstruction, taxes, market impact calibration or historical settlement schedule. Missing opens cancel orders, stale closes are valuation-only. One-session outcomes omit subsequent management, cash opportunity yield and subsequent liquidation costs. Next-open admission caps, sell-first alphabetical processing and T+1 settlement are inherited unchanged. Full rules/limitations are in artifacts/provenance.json and the original four-policy report.

Verification: copied replay tests, category prefix/future and same-decision-bar mutation tests, missing-history test, all-four common matching, hold identity, fill/fee/realized-PnL reconciliation, and exact original daily/fill/decision parity. See tests.log. All replay/analysis execution is pinned to one CPU and numerical threads to one, with a 1,150-second command ceiling.

Reproduce: `bash experiments/dev79_category_policy_study_20261101/run.sh`. Full pre-decision features/states in artifacts/state_opportunities.csv.gz; per-policy opportunity and fill attribution ledgers; original execution/decision/position/NAV ledgers; category_summary.csv; matched_contrasts.csv; paired_daily.csv.gz; support.csv; study_audit.json. checksums.json hashes all run inputs/code/results except itself and runtime log. Runtime resource records are runtime.log and supplemental_runtime.log (inventory strata only). No network, GA, monitoring or external review used. Resource deviation: the first six-second supplemental inventory-stratum pass initialized numerical libraries before setting CPU affinity (112% CPU in supplemental_runtime_initial.log). It was rerun with affinity/thread limits set before numerical imports; the core replay/analysis/tests were always taskset-pinned to one CPU. The initial resource log is retained for audit.

## Inventory-status matched diagnostics

| segment | stratum | comparisons | insufficient | max_matched | max_discordant |
| --- | --- | --- | --- | --- | --- |
| discovery | all_four_flat | 30 | 30 | 19 | 18 |
| discovery | all_four_held | 30 | 12 | 6478 | 5987 |
| test | all_four_flat | 30 | 30 | 0 | 0 |
| test | all_four_held | 30 | 12 | 6179 | 5688 |

Full paired effects and 95% month-block intervals (2,000 draws, separate seed 7901) are in artifacts/inventory_stratum_contrasts.csv. These are exploratory support diagnostics without additional multiplicity claims; starting dollar inventory and policy history still differ. Opportunity cost against hold is explicitly the negative of incremental dollars, in artifacts/opportunity_cost_summary.csv; positive means forgone hold profit.
