# PROVISIONAL free-source exploration

User authorization on 2026-10-31 permits free-data exploratory Stage1 before paid PIT certification. This supplements the earlier no-fetch audit restriction in DATA_SOURCE_POLICY.md; certified rules and the sealed executor remain unchanged. No purchases, GitHub push, external MTS writes, or Stage2 formation analysis are authorized by this workflow.

Run a small real-data acquisition and analysis pilot:

```sh
.venv/bin/python -m sector_pipeline.exploratory --out reports/provisional-pilot --symbols AAPL,MSFT,IBM,INTC,CSCO,ORCL --start 2009 --end 2009
```

After resolving acquisition gaps, run the reconstructed Stage1 universe:

```sh
.venv/bin/python -m sector_pipeline.exploratory --out reports/provisional-stage1
```

Repeat the identical command to resume. Each successful provider/request payload is hashed and atomically checkpointed under its output directory; failures remain retryable. Corrupt checkpoints are rejected. Keep the same output directory to retain its retrieval vintage. Alpha Vantage requires ALPHAVANTAGE_API_KEY; SEC requires SEC_USER_AGENT with contact information. Credentials are neither printed nor cached. No paid fallback occurs. Wikipedia is the reconstruction anchor; unavailable or unparseable membership blocks evaluation rather than substituting present constituents.

The report labels every result PROVISIONAL. It includes reconstructed universe size, reverse-reconstruction anomalies, monthly expected members, missing symbols, unknown sectors, source failures, signal availability and sensitivity outputs. UNKNOWN sectors are excluded from sector statistics, never pooled as an invented sector. Current Wikipedia sectors are explicitly historical proxies. CIKs are available only for current Wikipedia identities; unresolved removed identities remain missing. Reverse reconstruction does not establish complete historical membership or permanent identity.

All six signal definitions and existing statistical routines are reused without changes: next-open returns, 1/3-month primary horizons, 6-month exploratory decay, sector Spearman IC, equal-sector monthly means, fixed HAC lags, frozen four chronological blocks, twelve-test primary Holm family, 1000 within-sector-month placebos, turnover and 15bp one-way costs, and lookahead warning diagnostics. H5 retains raw negative direction in summary mean/t; fraction-positive, placebo and portfolio orientation use the frozen negative direction. H3 needs all eight prior surprises; H6 needs all four components. Missing observations are never imputed. SEC eligibility uses filing date plus one day; earnings are conservatively available after reported date. Provider retrieval vintages do not establish independently archived historical availability.

Sensitivity variants are predeclared here: available-stock sector medians; complete H1/H3/H4/H5 cases using those same available-stock ranks; and balanced observed formation coverage, also retaining the original ranks. These change sample/benchmark coverage, never signal definitions. Each variant reports the frozen twelve-test Holm correction; comparisons across variants are exploratory and cannot select or certify winners. Full-membership median row availability is reported separately. A small pilot has insufficient historical blocks for a Stage1 conclusion. Balanced coverage is over observed dates, not proof of complete exchange sessions. Calendar dates derive from the Yahoo panel and remain provisional. Missing delisted terminal prices cannot be distinguished from other unavailable prices without historical identity evidence; missing symbols/outcomes must not be read as zero returns.

Exploratory outputs cannot consume the certified once-only Stage1 slot, produce certified passers or release Stage2. They never call execute(), publish certification claims, or inspect Stage2 inputs. No PIT certification or predictive claim follows from these outputs.

2026-10-31 execution status: real-source pilot command attempted; Wikipedia acquisition failed in this runtime, including elevated execution. No real-data outcome analysis or full Stage1 run completed. See reports/provisional-pilot/report.json for the exact latest failure. Existing 2019/2020 data remain contaminated and are not substituted into this pilot.

The subsequent RUN ASAP authorization permits existing universe_2019 and cache reuse for a separate contaminated-2019 offline pilot. This supersedes the earlier statement above barring those inputs solely for this pilot. Executed results: reports/offline-provisional-2019/README.md and report.json. It is not Stage1 and cannot release Stage2. Reproduce with `/opt/mts/.venv/bin/python -m sector_pipeline.offline_pilot`. Wikipedia is accessible through the permitted web tool; runtime urllib remains blocked by DNS.

The subsequent expansion authorization has now been executed: [expanded partial-period Stage1](reports/expanded-stage1/README.md). This uses dated historical IVV sector fields, not current-sector substitutions. Source snapshots begin October 2006; usable sector fields begin April 2007. Existing reconstructed local Yahoo prices, filtered through December 2015, replace the unusable-for-Stage1 2016+ broad cache. All six definitions remain frozen; two declared sample variants were completed, with 1000 permutations for each defined statistic and twelve-/twenty-four-test primary Holm corrections. Full-sector benchmark coverage is zero, so available-stock median sensitivities are explicitly labeled. Repeated/back-normalized source tickers and unknown permanent identities are recorded; this is not original PIT ticker history. No certified ledger was invoked, no paid sources or external writes occurred, and Stage2 remains sealed.
