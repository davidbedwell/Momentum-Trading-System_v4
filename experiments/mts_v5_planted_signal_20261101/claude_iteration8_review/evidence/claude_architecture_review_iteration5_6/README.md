# Iteration5/6 external architecture review — NOT SUBMITTED

The evidence package and exact Sonnet 4.6 request are ready. No authenticated POST was issued, no HTTP 200 was obtained, and no Claude architecture review exists in this directory. `review.md` is an explicit failure notice, not a model response. `response.json` records local failure. The historical Claude review is preserved separately under `evidence/claude_external_review/` and is also included in the package.

The configured `/opt/mts/thunder-migration/.openrouter_api_env` raises PermissionError in this restricted session despite uid 0. No OPENROUTER_API_KEY or OPENROUTER_KEY is inherited. Sudo is unavailable. This requires credential access through an authorized execution environment; further user authorization alone does not remove the filesystem restriction. No secrets were printed or copied into these artifacts.

`package.md` requests mathematical PIT identification and delay bounds, concrete sequential detector algorithms and corrected thresholds, stable-return versus false-GREAT tradeoffs, training-only restoration of AVERAGE, and a complete alternative architecture with equations/pseudocode, training/calibration, validation, prioritized changes and falsification/stop criteria. It explicitly marks the synthetic DGP and rejects real-alpha claims and reviewed-holdout tuning.

`source_manifest.json` records source paths, sizes, SHA256 and transmission mode. `evidence/` contains exact source artifacts, full reports and compressed ledgers. Reports transmit all fields except repeated date-index arrays and daily channel traces, summarized with exact counts/hashes and alarm neighborhoods. Ledger excerpts are deterministic representative samples with full group row/funding/trade/day denominators, not a substitute for whole-ledger inference. The pre-correction raw iteration5 report is archived only; corrected final report is transmitted. Original test logs are included; tests and portfolios were not rerun.

Scripts:

- `python3 build_package.py`: read-only source assembly; writes only this directory.
- `python3 submit.py`: reuse of proven historical urllib/OpenRouter workflow, exact `anthropic/claude-sonnet-4.6` only, live model/context check, sanitized artifacts and verified HTTP 200, complete finish and nonempty substantive response. Retries transient DNS failures at most three attempts per network operation; credential denial is not transient and is not retried. Credential values stay in memory.
- `python3 validate_package.py`: source/archive hashes, request and Python syntax checks; no experiments or tests run.

No production edits, GA, implementation of suggestions, source-freeze alteration or extra portfolio replays were performed. See `submission_metadata.json`, `submission.log` and `validation.json` for exact status. The submission is incomplete until run successfully in an environment with authorized credential access.
