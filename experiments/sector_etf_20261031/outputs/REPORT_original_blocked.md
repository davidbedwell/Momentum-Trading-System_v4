# Independent sector ETF experiment — STOP: data unavailable

The acquisition gate was implemented and run on 2026-10-31. **No market results were produced.** The empirical experiment stopped under the user's explicit instruction to stop if data could not be obtained. This is a data-access failure, not evidence against momentum, reversal, or trend control. No claim of a completed backtest or validation is made.

The experiment is isolated in `experiments/sector_etf_20261031/`. No MTS v5, earlier Stage2, stock-signal code, or existing project files were edited. No paid data calls, GitHub operations, commits, or pushes occurred. Existing uncommitted workspace changes were left alone.

## Frozen registration and holdout

`PREREGISTRATION.md` was frozen at **2026-10-31 10:37:02 UTC**, before price acquisition and before any outcome calculation. SHA256:

`23a49749f06cfc44c4c7f5a203e5f18cd04343d5763e7541100c4f977a2f756f`

Discovery is 2000–2016; validation is 2017–2025. 2026 is excluded. Validation remains unopened. No parameters were retuned and no hypothesis was selected. The protocol pre-specifies H1 six-month relative momentum, H2 twelve-month relative momentum, H3 one-month relative reversal, and H4 standalone SPY 200-session trend control. These labels do not refer to original MTS stock signals.

Universe is the nine original sector SPDRs from actual observed trading history no earlier than 1998-12-16, XLRE no earlier than 2015-10-07, and XLC no earlier than 2018-06-18, with full required lookbacks. SPY is the benchmark. SGOV can only be used after actual available history following its 2020-05-26 inception; pre-SGOV defense is explicitly zero-interest cash. Sources for inception dates are linked in the protocol; inception dates do not imply a fabricated first trading price.

## Actual execution evidence

The logged acquisition attempt ran at **10:38:28 UTC** and returned exit code **2 (`BLOCKED_DATA`)**. See `outputs/acquisition.json` and `outputs/run.log`.

| Check | Observed result |
|---|---|
| Yahoo query1 daily adjusted-price endpoint | DNS `gaierror`: temporary failure in name resolution |
| Yahoo query2 daily adjusted-price endpoint | Same DNS failure |
| Stooq connectivity diagnostic | Same DNS failure; no Stooq prices accepted |
| Separate shell curl probes for all three hosts | Exit 6, could not resolve host |
| Web-tool Yahoo historical endpoint fallback | Endpoint inaccessible; no complete daily series returned |
| Local sector/SGOV filename cache search under readable `/opt/mts` and `/tmp` | No matching symbol files |
| Successfully acquired symbols / requested symbols | **0 / 13** |
| Prices admitted to analysis | **0** |
| Market outcomes calculated / validation opened | **No / No** |
| Acquisition-gate tests | **8 passed** |

The cache search was a filename/path inventory, not an exhaustive inspection of every arbitrary multi-asset store. It did not identify a usable free adjusted daily sector ETF cache. Benchmark-only SPY and explicitly synthetic files were visible in unrelated directories; neither can supply the required sector panel and neither was used. Existing stock research outputs were not substituted for ETF data. No prior strategy outcomes were read.

The cloud runtime's environment-status tool was not exposed in the active tools, and `/etc/codex/network-policy.json` was absent. This report therefore identifies observed connectivity failures without asserting a specific network-policy cause. Installing numerical dependencies into an isolated virtual environment also failed DNS resolution; a pre-existing Python environment with scientific packages was found, so that was not the decisive blocker. The executed acquisition gate and its tests require only Python's standard library.

## Requested statistics: unavailable, not zero

| Requested output | Status |
|---|---|
| H1 IC and spread, 1m / 3m | Not computed: no adjusted price panel |
| H2 IC and spread, 1m / 3m | Not computed: no adjusted price panel |
| H3 reversal IC and spread, 1m | Not computed: no adjusted price panel |
| H4 versus SPY and cash/SGOV | Not computed: no adjusted price panel |
| CAGR, maximum drawdown, Calmar, turnover | Not computed |
| 15bps and 30bps one-way sensitivity | Pre-specified, not measured |
| Discovery, sealed validation, chronological subperiods | Pre-specified, not evaluated |
| HAC inference, block bootstrap, Holm adjustment | Pre-specified, not estimated |

The planned implementation uses vendor adjusted opens only if directly supplied; otherwise signals execute at the next session close and returns are delayed close-to-close. **No executable prices or portfolio returns were simulated.** Portfolio/inference code was not completed after the stop condition; only acquisition, protocol integrity, and data-admission gates were implemented and tested. The statistical design is documented, not presented as executed analysis.

## Limitations and decision

**STOP — blocked on data.** No production GO and no empirical replication GO can be awarded. The frozen economic/statistical criteria remain unevaluated. Reaching the four-hour ceiling was unnecessary because the explicit data stop condition was reached first; work ended within minutes, with no prolonged retry loop or compute expenditure.

Even with data, this design has only 9–11 related assets, sector-definition changes, overlapping three-month labels, a single historical holdout, vendor retrospective adjustment risk, and no independent data-source reconciliation. The protocol addresses dependence by aggregating IC/spreads by month and using fixed time-series HAC/bootstrap inference, rather than counting ETF rows as independent samples. Long-short diagnostics exclude borrow and financing. Zero-interest cash understates historical attainable cash yields. None of these caveats was resolved by actual analysis in this blocked run.

A future continuation requires freely sourced, provenance-documented adjusted daily prices for the sector universe, SPY and SGOV over their real histories, or working access to a free source. Preserve this registration and holdout; complete and test the analysis against discovery only, freeze its code and discovery outputs, then run validation once. A successful future acquisition alone is not a completed experiment.

## Reproducibility and files

From `/opt/mts/sector-leadership-independent`:

```bash
python3 -m unittest discover -s experiments/sector_etf_20261031/tests -v
python3 experiments/sector_etf_20261031/run.py
```

The runner verifies the registration hash before any data access, bounds per-request timeout to eight seconds by default, records source failures, and exits 2 when data are blocked. If all symbols are downloaded in a future run, it exits 3 (`ACQUIRED_NOT_ANALYZED`), requiring explicit completion of the registered analysis. Rerunning overwrites `outputs/acquisition.json`; preserve the original evidence first if needed.

- `PREREGISTRATION.md`: frozen design, split, costs, inference, decision criteria, source references.
- `preregistration.lock.json`: UTC registration timestamp and protocol SHA256.
- `run.py`: standard-library acquisition gate, strict adjusted-close parsing, inception checks, bounded free endpoints.
- `tests/test_gate.py`: eight integrity/admission/failure-path tests. Small fabricated payloads are unit-test fixtures only and never market evidence.
- `outputs/acquisition.json`, `outputs/run.log`: actual failed acquisition evidence.
- `outputs/tests.log`: actual passing test run.
- `outputs/local_symbol_cache_search.txt`: empty output from exact sector/SGOV symbol filename search; inaccessible paths were skipped.
- `outputs/artifact_hashes.json`: hashes of experiment source, protocol and evidence at completion, excluding itself.
