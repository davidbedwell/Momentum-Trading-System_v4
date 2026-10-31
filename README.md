# Independent sector leadership pipeline

Python 3.10+, standard-library runtime. All paths are restricted to this independent workspace. No protected datasets, secrets directory access, or GitHub push.

```sh
python3 -m venv .venv
.venv/bin/pip install pytest
.venv/bin/python -m pytest
.venv/bin/python -m sector_pipeline smoke --symbols 6
.venv/bin/python -m sector_pipeline run --prices reports/smoke/prices.csv --members reports/smoke/members.csv --years 2019 --out reports/replay
```

Smoke downloads real daily prices for the first six existing pilot symbols, with no fundamentals fabricated. Network failure produces an incomplete JSON report and nonzero exit. Downloaded CSV permits offline replay. Existing pilot files have annual/quarterly derived values, not cached OHLCV, so they cannot replace a daily-price download. Never run legacy root-level `test_*.py` as pytest: they contain vendor probes; pytest configuration restricts collection to `tests/`.

Inputs: prices CSV `symbol,date,adj_close,adj_open` (blank open allowed), optional `close,volume,source`; constituent CSV `symbol,sector,start,end,source` with exclusive end dates. Unique symbol/date and nonoverlapping membership intervals required. Symbols must identify continuous security history; use reconciled identities, not unverified ticker reuse. Optional `--fundamentals` and `--earnings` are JSON maps from these same symbols to raw SEC companyfacts / Alpha Vantage EARNINGS responses.

```sh
# Use environment credentials, never command-line secrets.
.venv/bin/python -m sector_pipeline fetch sec 320193 --out reports/aapl_facts.json
.venv/bin/python -m sector_pipeline fetch alpha AAPL --out reports/aapl_earnings.json
.venv/bin/python -m sector_pipeline fetch fred UNRATE --asof 2019-01-31 --out reports/unrate_vintage.json
```

SEC requires `SEC_USER_AGENT` with contact; Alpha requires `ALPHAVANTAGE_API_KEY`; FRED requires `FRED_API_KEY`. Adapters surface access/rate/entitlement failures; no automatic fallback. FRED output is a regime input artifact; regime-stratified metrics are not implemented. Historical analyst revisions have no free-data assumption.

Outputs: observations.csv, monthly_metrics.csv (sector/year breakdown), price_diagnostics.csv and report.json with coverage, exclusions, source limitations, manifest hash, HAC and Holm summaries. Read RESEARCH_PROTOCOL.md and manifest.json before interpretation. All runs currently report incomplete and prohibit predictive claims; certified PIT/delisting coverage and blind release remain outstanding.

Source contracts: [SEC APIs](https://www.sec.gov/edgar/sec-api-documentation), [Alpha Vantage earnings](https://www.alphavantage.co/documentation/), [FRED vintage semantics](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html).
