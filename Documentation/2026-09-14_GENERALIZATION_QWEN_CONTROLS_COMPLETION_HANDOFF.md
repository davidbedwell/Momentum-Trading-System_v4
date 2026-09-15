# MTS v4 Generalization / Qwen Shadow / Scientific Controls Completion Handoff — 2026-09-14

## Branch

`mts-v4-generalization-qwen-controls-20260914`

Draft PR: #11, targeting `mts-v4-cross-sectional-backend-completion-20260914`.

Deterministic code head validated by GitHub Actions: `7495be8edf79791bcae6e4c3e0e082aafafadb44`.

GitHub Actions run `34920844049` / MTS v4 core run 223 completed successfully:

- install dependencies — PASS;
- compile `MTS_V4` and `scripts` — PASS;
- unittest compatibility gate — PASS;
- full `pytest Tests/mts_v4` — PASS;
- CSV adapter regression — PASS;
- wheel/sdist build — PASS;
- installed-package verification outside checkout — PASS.

The first PR CI attempt exposed one pre-existing prompt-contract regression caused by the new generalization prompt replacing the exact authority sentence required by `test_cross_subject_generalization`. The sentence was restored without changing the approved scientific-authority boundary. The later code gate above is green.

## 1. Durable explicit generalization state

`MTS_V4/generalization_state.py`

Implements an append-only RD-authored generalization ledger with explicit states:

`SUBJECT_TENTATIVE -> CROSS_SUBJECT_CANDIDATE -> CROSS_SUBJECT_VALIDATING -> CROSS_SUBJECT_VERIFIED | CROSS_SUBJECT_NOT_VERIFIED`

Deterministic code validates identity/transition representation only. It does not infer a candidate, validation state, verification, or rejection from Findings/statistics.

Representation guardrails:

- subject-tentative creation requires source-subject provenance;
- cross-subject candidate requires provenance from at least two subjects;
- entering validation requires frozen RD-authored validation criteria;
- terminal disposition after validation requires validation-trial IDs;
- materially revised proposition requires a new generalization identity;
- transition history is append-only and persisted atomically.

`MTS_V4/cross_subject_generalization.py` now exposes the durable state to Sol and adds explicit `research_state.generalization_updates`. The update field is decision-local delta state, not cumulative science. The original authority rule is preserved: deterministic code does not choose subjects, normalization, variables, methods, or whether a generalization is supported.

`scripts/run_sol_cross_subject_generalization_stateful.py` enables durable state persistence for the existing generalization campaign via an explicit `--generalization-state-path`.

## 2. Qwen supervised replay/shadow gate

`MTS_V4/qwen_shadow_gate.py`

Adds:

- exact Sol governed-prompt replay capture for universe/control Sol runs;
- structured Qwen shadow observations;
- objective transport/decode/contract counts;
- the previously approved minimum shadow exposure of 20 Analysis operations;
- explicit reviewer fields for scientific-loop continuation, toolkit use, cross-evidence reasoning, `LACK_RESOURCE` behavior, market-science output, scientific usefulness, and unnecessary work;
- a gate that can only reach `READY_FOR_HUMAN_AUTONOMY_DECISION` and **cannot authorize autonomy**.

No numeric scientific pass-rate or contract-failure threshold was invented. Human authorization remains mandatory.

`scripts/run_qwen_shadow_replay.py`

- defaults to the existing Thunder/Qwen OpenAI-compatible endpoint contract (`MTS_RD_AI_BASE_URL`, default localhost port 8000);
- discovers the Qwen model through `/v1/models` when `MTS_RD_AI_MODEL` is not set;
- replays only corpus records containing exact preserved Sol messages;
- legacy Sol records without exact prompt envelopes are skipped for exact replay but can remain historical approach examples;
- does not route Qwen failures to Sol appeal because the purpose is to measure Qwen itself.

`scripts/evaluate_qwen_shadow_gate.py` assembles the autonomy-review evidence and always reports `QWEN_AUTONOMY_AUTHORIZED=False`.

`scripts/build_sol_qwen_shadow_corpus.py` is upgraded to corpus format V2. It includes exact replay messages when `sol_replay_envelopes.jsonl` exists and labels legacy records separately.

The universe Sol runner now captures `sol_replay_envelopes.jsonl`, so the scientific-control runs and future universe Sol calibration become exact Qwen replay cases.

## 3. Single five-control Sol calibration harness

`MTS_V4/scientific_control_campaign.py`

Preserves the agreed independent grading rubric:

- PASS: independently recovers the known effect with roughly correct direction, horizon, conditioning and robustness; negative control correctly rejects stable predictive information;
- PARTIAL: related structure is detected but an important formulation/stability condition is missed; negative control may show weak/unstable structure without a robust predictive claim;
- FAIL: reasonable inquiry is exhausted without detecting an effect demonstrably present in supplied data, or stable predictive information is promoted from the deterministic negative control.

The grading rubric is never sent to Sol. Deterministic code assembles an assessment but does not assign scientific grades.

`scripts/run_sol_scientific_controls.py`

Runs all five blinded controls through `run_sol_batched_universe.py`:

1. cross-sectional medium-term momentum;
2. medium-term trend persistence;
3. short-horizon reversal/continuation;
4. post-earnings behavior;
5. deterministic negative control.

It requires an explicit per-control Sol spend ceiling, disables interactive spend extension, stops on technical/spend failure by default, captures per-control logs/state, and writes one `scientific_control_campaign_report.json`. Optional independent post-run assessments can be supplied once and are assembled automatically into PASS/PARTIAL/FAIL status without manual result stitching.

`Documentation/2026-09-14_SCIENTIFIC_CONTROL_CAMPAIGN_CONFIG.md` defines the evidence-only configuration contract. Expected effects are deliberately absent from that config.

## 4. Isolated negative-control substrate

`MTS_V4/acceptance_control_store.py`

Defines `mts_acceptance_negative_control:v1` containing only `deterministic_null__v1`, a SHA-256 stable-security-ID/effective-date hash mapped to [0,1]. Its value does not depend on price, return, volume, volatility, event, sector, breadth, or any other market measurement.

`scripts/build_negative_control_feature_set.py` incrementally creates that feature set from an existing derived-store identity surface while copying no market values. This prevents a real predictor from contaminating the negative control.

## What is still a live-data/integration gate

No deterministic software work can substitute for these next steps:

1. choose/validate authoritative point-in-time historical universe membership/security identity source;
2. build and inspect the real historical Nexus-derived market store;
3. validate feature arithmetic on real samples;
4. validate historical earnings event timestamp/coverage source before PEAD;
5. build the isolated negative-control feature set;
6. run the five blinded controls through Sol with a deliberately bounded spend authorization;
7. independently grade PASS/PARTIAL/FAIL;
8. preserve Sol replay envelopes and build the V2 Sol/Qwen corpus;
9. launch Qwen successfully in the existing vLLM/OpenAI-compatible environment;
10. replay/shadow Qwen for at least the approved 20 Analysis-operation exposure and review scientific autonomy behavior;
11. only a later explicit human decision may authorize Qwen autonomy.

Do not merge PR #11 merely because deterministic CI is green. Real-data scientific calibration and Qwen replay remain acceptance gates.
