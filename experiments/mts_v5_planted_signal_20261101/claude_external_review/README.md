# External Claude scientific review — NOT SUBMITTED

No authenticated POST was possible and no Claude review was received. The local runtime denies reading `/opt/mts/thunder-migration/.openrouter_api_env`; no OpenRouter variable was present. HTTPS model discovery failed DNS resolution. Alternate Desktop Commander server execution returned `MCP tool call requires approval, but approval policy is never`. Existing submission code could not be searched in the inaccessible thunder-migration directory; no submission code was found in the accessible repository. No access controls were changed.

`package.md` is the complete prepared scientific request: five chronological reports representing four iterations, all experimental README/preregistrations, existing local reviews where present, semantic structured numerical evidence, exact aggregate latent/realized 5x6 matrices, all per-seed discrimination summaries, all portfolio/paired records, aggregate tier metrics, limitations, and experiment/model source. Full original reports and relevant CSVs are archived in `evidence/`; large redundant per-cell dumps and per-seed duplicate matrices are retained there rather than copied into the prompt. The source manifest records SHA256 provenance. No experiment was rerun or fitted.

`request.json` is sanitized and has no Authorization header. Its initial model is an UNVERIFIED DRAFT preference, not a model confirmed offered. `submit.py` must fetch the live OpenRouter catalog, choose an offered Anthropic Sonnet/Opus with enough context, and overwrite that draft preference before any POST. It uses at most 14,000 output tokens and a conservative input context budget. Provider identity, substantive text and complete finish checks must pass before `review.md` can contain a verified review. Token usage, HTTP status and timestamps are persisted; currently model/status/usage are null because no provider transaction occurred. `response.json` currently records a local failure, not a fabricated provider response. `review.md` currently records the absence of a review.

On an authorized executor with readable credentials and working HTTPS/DNS, run:

```bash
python3 experiments/mts_v5_planted_signal_20261101/claude_external_review/submit.py
python3 experiments/mts_v5_planted_signal_20261101/claude_external_review/validate_package.py
```

The script reads a literal OpenRouter credential assignment into memory; it does not execute the credential file or print the key. API keys/Authorization headers are never written into the request JSON or logs. TLS verification and inherited proxy settings remain enabled. Only this review directory is written by the submitter. Original reports, production files, parameters and GA are untouched.

`build_package.py` rebuilds the evidence bundle from the recorded experiment paths. `validate_package.py` checks source hashes, all exact aggregate matrices against original CSVs, opportunity denominators, all five report sections, and sanitized request equality. `submission_metadata.json`, `submission.log` and `validation.json` preserve the observed outcome.
