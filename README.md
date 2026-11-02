# Independent sector leadership pipeline — controlling v2

CONTROLLING_PROTOCOL_V2.md is the user authority and supersedes CODEX_IMPLEMENTATION_BRIEF.md (historical v1). RESEARCH_PROTOCOL.md repeats v2 with frozen implementation conventions; manifest.json records the seal. Work remains within this repository. No subscriptions, protected datasets, or GitHub push.

Run offline fixture tests only:

```sh
.venv/bin/python -m pytest -q
```

The local v2 executor is implemented and tested with synthetic fixtures. See [EXECUTOR_V2.md](EXECUTOR_V2.md) for bundle schema, commands, immutable once-only ledger, source verification, stage release, diagnostics and limitations. Stage2 remains sealed until a valid complete Stage1 result logs passing signal/horizon pairs. No real-data pilot has run: a verified Stage1 source bundle is unavailable.

Existing reports/smoke are exploratory/old protocol v1. No 2006–2026 certification or predictive claim is made. No push or external MTS writes.

A separately authorized **PROVISIONAL free-source Stage1** workflow is now available; see [PROVISIONAL_EXPLORATORY.md](PROVISIONAL_EXPLORATORY.md) for resumable pilot/full-universe commands and limitations. It cannot release Stage2 or consume the certified ledger. The real-source pilot was attempted but blocked at Wikipedia acquisition; no completed exploratory Stage1 result exists.

2026-10-31: executed the separately authorized contaminated-2019 offline real-data pilot. See [results and limitations](reports/offline-provisional-2019/README.md) and [machine-readable results](reports/offline-provisional-2019/report.json). The earlier acquisition status above refers to the Wikipedia-dependent Stage1 command; Stage2 remains sealed.

2026-10-31: completed the expanded **PROVISIONAL partial-period Stage1** using dated IVV sector evidence and existing pre-2016 local Yahoo prices. See [completed results](reports/expanded-stage1/README.md), [full statistics/provenance/missingness](reports/expanded-stage1/report.json), and [artifact validation](reports/expanded-stage1/validation.json). The older historical cache supplies 322 priced symbols; 317 contribute known-sector outcomes, compared with the former 15-label sample. Sector evidence starts April 2007; this is not complete 2006–2015 PIT coverage. No primary placebo passes; no certified passers or Stage2 release. The earlier 433-stock cache starts in 2016 and cannot supply Stage1 prices. Tests: 43 passed with the analysis dependencies; default fixture environment 39 passed, one optional module skipped.
