PROVISIONAL contaminated-2019 offline pilot — executed 2026-10-31.

Reproduce from the existing local caches:

```sh
/opt/mts/.venv/bin/python -m sector_pipeline.offline_pilot
```

The Python environment above supplies pandas/pyarrow; /usr/bin/python3 supplies PyYAML. No network access, credentials, certified executor, ledger, or gate is used by this command. Read report.json for source hashes, monthly coverage/missing symbol lists, all six hypotheses, lookahead diagnostics, 1000-shuffle placebo results, fixed HAC estimates and twelve-test Holm correction. observations.csv, monthly_metrics.csv, membership_used.csv and prices_used.csv contain the actual inputs and results.

The 534 unique recorded members include 505 members at every reconstructed month end. There are 433 cached symbols and 324,137 usable daily price rows from 2017–2019; only 2019 formations and exits are evaluated. Exact ticker filenames are required; no guessed alias or replacement issuer is used. 101 symbols lack usable caches. Monthly priced membership ranges from 406/505 to 423/505. Price identities, adjustments, delisting causes and third-party historical membership remain unverified.

Only 15 stocks have existing legacy sector labels (five each Technology, Healthcare, Financials), which are unverified proxies for historical GICS. The other 490 monthly members have UNKNOWN sectors and are excluded from sector metrics. The legacy sample was selected with knowledge of 2019 outcomes, so this is biased, contaminated exploration. Sector medians use available sample stocks, not full historical sectors. The cached panel must not be interpreted as full universe coverage.

All six original hypotheses are retained. H1/H2/H5 have 15 stocks per evaluable month; H3 has 10 with actual cached earnings and eight prior surprises; H4 and consequently H6 have zero observations. No missing signal, sector or price is imputed. Signal counts in monthly coverage are conditioned on an available 1m outcome; December's zero is right-censoring, not proof signals are absent.

1m has 11 formation months, 3m nine, 6m six. No 2020 exit observations are used. The six-month HAC t is undefined because six monthly observations do not support lag 5 inference. The five-stock sector groups cannot form both frozen top/bottom deciles: spreads, turnover and net cost results are unavailable. Lookahead output is a warning diagnostic only. Missing delisted terminal prices cannot be distinguished from other cache gaps.

No direction-correct placebo passes were found. H3's 3m IC is negative (opposite its hypothesis), with nominal HAC t -4.763 and two-sided twelve-test Holm p approximately 0.00002287; this is not positive evidence for H3 and cannot be a certified finding in this selected sample. No 2006–2015 chronological blocks are represented. No Stage1 pass or Stage2 release is possible from this run. manifest.json hashes before and after match; Stage2 remains sealed.

The runtime Wikipedia request failed with URLError: [Errno -3] Temporary failure in name resolution. The separate permitted web.run route successfully read the official Wikipedia page and constituent table. See network_attempt.json for the exact runtime error. Neither route supplied data to the offline pilot. The environment_status tool and /etc/codex/network-policy.json are unavailable; no proxy bypass, DNS workaround or policy change was attempted.

Validation: existing test suite 39 passed. Output checks also verify 2019-only formations/exits, exact membership intervals, no duplicate stock/date/horizon rows, finite observed returns and unchanged sealed manifest.
