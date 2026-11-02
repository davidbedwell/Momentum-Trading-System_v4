Expanded PROVISIONAL partial-period Stage1 — COMPLETED.

Loaded 869,522 pre-2016 price rows for 322 exact-matching historical holdings; 317 symbols contribute known-sector outcomes.

The earlier 433-stock overlap cache begins in 2016 and supplies zero Stage1 observations. The separate existing reconstructed raw_yfinance cache supplies this run. No external MTS files were modified.

All 111 dated IVV holdings snapshots from 2006-10-31 through 2015-12-31 were processed. Sector evidence begins 2007-04-30; the preceding six snapshots have UNKNOWN sectors. January–September 2006 has no holdings snapshots. No current-sector backfill was used.

Labeled-month formation-price/sector coverage: 200–307 stocks per month (mean 247.79) against 499–506 equity holdings. See coverage.json for every missing ticker, unknown-sector count, horizon and signal count.

Results below are raw equal-sector monthly mean Spearman ICs and frozen Newey–West t statistics. H5 expects a negative raw IC/t. Six signals and their definitions remain frozen; H4 and H6 are unavailable. H3 uses all eight prior surprises and remains sparse. Its issuer cache originated in the contaminated, outcome-selected 2019 pilot, so H3 also carries selection bias. No unavailable hypothesis receives invented observations or placebo results.

Sample: dated_holdings_available

| Signal | 1m IC | NW t | 3m IC | NW t | 6m IC (exploratory) |
|---|---:|---:|---:|---:|---:|
| H1 | 0.00128 | 0.07356 | 0.00103 | 0.03577 | -0.00400 |
| H2 | -0.01070 | -0.55818 | -0.02706 | -0.92523 | -0.03876 |
| H3 | 0.00507 | 0.08251 | 0.02565 | 0.28102 | 0.14613 |
| H4 | unavailable | unavailable | unavailable | unavailable | unavailable |
| H5 | 0.00957 | 0.49011 | 0.02378 | 0.75330 | 0.02733 |
| H6 | unavailable | unavailable | unavailable | unavailable | unavailable |

| Signal/horizon | Months | Stocks | IC dates | Positive blocks | Positive-IC fraction (oriented) | Placebo real / 99th percentile | Beats placebo? |
|---|---:|---:|---|---:|---:|---|---|
| H1_1 | 104 | 313 | 2007-04-30–2015-11-30 | 2/4 | 0.50000 | 0.00128 / 0.02046 | False |
| H2_1 | 104 | 313 | 2007-04-30–2015-11-30 | 2/4 | 0.51923 | -0.01070 / 0.01984 | False |
| H3_1 | 104 | 10 | 2007-04-30–2015-11-30 | 3/4 | 0.50000 | 0.00507 / 0.12981 | False |
| H5_1 | 104 | 313 | 2007-04-30–2015-11-30 | 2/4 | 0.47115 | -0.00957 / 0.02058 | False |
| H1_3 | 102 | 311 | 2007-04-30–2015-09-30 | 3/4 | 0.50980 | 0.00103 / 0.02025 | False |
| H2_3 | 102 | 311 | 2007-04-30–2015-09-30 | 2/4 | 0.48039 | -0.02706 / 0.02089 | False |
| H3_3 | 102 | 10 | 2007-04-30–2015-09-30 | 3/4 | 0.48039 | 0.02565 / 0.15098 | False |
| H5_3 | 102 | 311 | 2007-04-30–2015-09-30 | 2/4 | 0.47059 | -0.02378 / 0.01954 | False |
| H1_6 | 99 | 309 | 2007-04-30–2015-06-30 | 2/4 | 0.56566 | -0.00400 / 0.02033 | False |
| H2_6 | 99 | 309 | 2007-04-30–2015-06-30 | 1/4 | 0.43434 | -0.03876 / 0.02118 | False |
| H3_6 | 99 | 10 | 2007-04-30–2015-06-30 | 4/4 | 0.57576 | 0.14613 / 0.13995 | True |
| H5_6 | 99 | 309 | 2007-04-30–2015-06-30 | 2/4 | 0.43434 | -0.02733 / 0.01931 | False |

Full-holdings benchmark rows: 0; explicit available-stock benchmark rows: 75,008. Neither establishes complete S&P500 benchmark coverage.

Sample: annual_corroborated_available

| Signal | 1m IC | NW t | 3m IC | NW t | 6m IC (exploratory) |
|---|---:|---:|---:|---:|---:|
| H1 | 0.00160 | 0.09171 | 0.00146 | 0.05053 | -0.00371 |
| H2 | -0.01072 | -0.55477 | -0.02725 | -0.92142 | -0.03874 |
| H3 | 0.00507 | 0.08251 | 0.02565 | 0.28102 | 0.14613 |
| H4 | unavailable | unavailable | unavailable | unavailable | unavailable |
| H5 | 0.01000 | 0.51158 | 0.02411 | 0.75825 | 0.02798 |
| H6 | unavailable | unavailable | unavailable | unavailable | unavailable |

| Signal/horizon | Months | Stocks | IC dates | Positive blocks | Positive-IC fraction (oriented) | Placebo real / 99th percentile | Beats placebo? |
|---|---:|---:|---|---:|---:|---|---|
| H1_1 | 104 | 311 | 2007-04-30–2015-11-30 | 2/4 | 0.50000 | 0.00160 / 0.01874 | False |
| H2_1 | 104 | 311 | 2007-04-30–2015-11-30 | 2/4 | 0.53846 | -0.01072 / 0.02083 | False |
| H3_1 | 104 | 10 | 2007-04-30–2015-11-30 | 3/4 | 0.50000 | 0.00507 / 0.12981 | False |
| H5_1 | 104 | 311 | 2007-04-30–2015-11-30 | 2/4 | 0.46154 | -0.01000 / 0.02242 | False |
| H1_3 | 102 | 309 | 2007-04-30–2015-09-30 | 3/4 | 0.51961 | 0.00146 / 0.02076 | False |
| H2_3 | 102 | 309 | 2007-04-30–2015-09-30 | 2/4 | 0.48039 | -0.02725 / 0.02258 | False |
| H3_3 | 102 | 10 | 2007-04-30–2015-09-30 | 3/4 | 0.48039 | 0.02565 / 0.15098 | False |
| H5_3 | 102 | 309 | 2007-04-30–2015-09-30 | 2/4 | 0.47059 | -0.02411 / 0.02113 | False |
| H1_6 | 99 | 306 | 2007-04-30–2015-06-30 | 2/4 | 0.57576 | -0.00371 / 0.02121 | False |
| H2_6 | 99 | 306 | 2007-04-30–2015-06-30 | 1/4 | 0.44444 | -0.03874 / 0.02283 | False |
| H3_6 | 99 | 10 | 2007-04-30–2015-06-30 | 4/4 | 0.57576 | 0.14613 / 0.13995 | True |
| H5_6 | 99 | 306 | 2007-04-30–2015-06-30 | 2/4 | 0.43434 | -0.02798 / 0.02067 | False |

Full-holdings benchmark rows: 0; explicit available-stock benchmark rows: 74,330. Neither establishes complete S&P500 benchmark coverage.

Each defined statistic received exactly 1,000 within-sector-month permutations with fixed seed 0. H4/H6 have undefined ICs and zero shuffles. All means, HAC errors/t/p, twelve-test and twenty-four-test Holm p values, four-block counts, spreads, turnover, 15bp one-way net costs and lookahead diagnostics are in report.json; per-sector monthly observations and statistics are saved under each sample directory.

The first chronological block is partial, membership is a dated tracking-fund proxy, publication/sector vintage is retrospective and unverified, and prices exclude many removed/delisted issuers. Retrospective holdings also contain normalized/repeated symbols: CB includes ACE/Chubb names and MRK two CUSIPs. One observation per ticker is retained because sector labels agree; permanent identity remains UNKNOWN. See duplicate_identity_evidence.json. This does not establish original historical ticker or share-class PIT history. Full-holdings counts refer to deduplicated ticker proxies. No certification, full-period pass or predictive claim is justified. Both variants are exploratory, and neither can release Stage2. Available-stock medians do not repair survivor bias.

All price rows and exits end by 2015-12-31. Primary 1m/3m and exploratory 6m outcomes are right-censored accordingly. No 2016+ formations/outcome rows were loaded. Sealed manifest, protocols, core statistical engine, executor and gate hashes match before/after. 2019/2020 remain contaminated and are not evaluated by this run.

Sources: [dated IVV snapshot repository](https://github.com/riazarbi/sp500-scraper), [annual membership cross-check](https://github.com/shardul0701/SP500-Survivorship-bias-data-2004-2026), [ticker ambiguity evidence](https://github.com/lawcal/sp500-components-history). URLs/blob IDs are in sources/acquisition.json; SHA256s are in report.json. Missing historical prices/identities, verified as-filed H4 inputs, complete historical membership/sector publication evidence and terminal delisting returns remain blockers to certification.

Reproduce: `/opt/mts/.venv/bin/python -m sector_pipeline.expanded_stage1` then `/opt/mts/.venv/bin/python -m sector_pipeline.finalize_expanded`. The first command requires read access to the existing historical MTS cache and writes only here. Optional analysis dependencies: numpy, pandas, pyarrow; YAML source parsing uses system PyYAML. Tests: analysis environment 43 passed; default environment 39 passed, one optional module skipped. Artifact validation: PASS, including independent recomputation of saved sector ICs and verification of all downloaded source hashes.
