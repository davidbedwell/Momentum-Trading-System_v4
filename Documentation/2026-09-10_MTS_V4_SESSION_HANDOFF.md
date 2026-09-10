# MTS v4 Session Handoff — 2026-09-10

## Session Summary

This session continued the live AAPL end-to-end Qwen campaign on branch `mts-v4-unseen-ticker-verification-20260910` and focused on recovery after process loss when a checkpointed Research Director request depended on a temporary Analysis result that no longer existed in the restarted runtime.

The root `ChatGPT.md` remains the governing authority. It explicitly requires that future sessions read it before architecture or implementation changes, preserves AI scientific authority, allows deterministic enforcement only of objective execution/governance constraints, keeps reproducible/raw data temporary rather than durable Nexus payload, and says the root authority file must not become a chronological work diary. This handoff is therefore a separate document.

The core live campaign is:

- state directory: `/home/ubuntu/mts-v4-aapl-qwen-e2e-20260910_163621`
- campaign id: `mts-v4-aapl-qwen-e2e-20260910_163621`
- mode: live AAPL EXPLORATION, not retrospective historical blind validation
- runner: `scripts/run_aapl_qwen_e2e.py`
- configured analysis ceiling: 500
- Qwen runtime: `/home/ubuntu/hf-cache/Qwen3-32B-AWQ` through local vLLM at `http://127.0.0.1:8000`

Before this session the campaign had 6 RD decisions and 5 completed analyses. The checkpointed next request was `rq_006_darkpool_data_integrity`, method `analysis.descriptive.statistics`, question `q_darkpool_data_integrity_check`, intended to inspect columns `dark_pool_volume_sum` and `close` in an aligned derived dataset. That aligned dataset had been produced by temporary Analysis result `analysis-result:af7a5bf18b234aa18cd516a354299776` before the original process died.

Because Analysis payloads are temporary by architecture, that result payload was absent after restart. The durable RP/Nexus state retained lineage/metadata, but not the reusable derived rows. The correct recovery path therefore requires RD either to regenerate/reconstruct the needed intermediate dataset from currently available evidence, use another currently available valid Analysis output, or choose another scientific direction.

## Changes Completed This Session

A previously discovered persistence bug had already been repaired before this handoff: invalid RD repair requests are no longer persisted into a Research Package before objective validation. Current relevant commits in this branch include:

- `7c1457130fdcad8bc0afdf41f306a5341cd85b60` — Separate RD decision recording from accepted Analysis requests.
- `1ce1967c5f959ca920ffa233f2c690dd818bc6a1` — Persist Analysis requests only after objective validation.
- `4f804a5f45b82914ba841fa57641abbd9578e112` — Wire validated request persistence into campaigns.
- `10309b914333a6ef2e49e254db5fdc3222307ce1` — Test validated Analysis request persistence.

This session then made a narrow runtime-reference guidance repair after repeated live failures showed Qwen was preserving dead runtime references despite objective defects.

Commit `845c32b7dd63edfc7ad7a5204af1abd6cb382e8b` updates `MTS_V4/validation.py` so objective defects now explicitly state that:

- an unavailable/stale evidence ID must not be reused in the repaired request;
- an unavailable prior Analysis result payload must not be referenced again through `analysis_inputs`;
- if the same scientific work remains desired, RD may reconstruct/regenerate the prerequisite through a new executable Analysis request from currently available evidence or other currently available Analysis outputs, or choose another scientific direction;
- regenerated execution requires a new request ID;
- deterministic code does not select replacement inputs, method, parameters, or scientific direction.

Commit `4c3cb378a8fb0ada956f48b3b679dd22b5828b71` adds focused regression tests for this stale-runtime-reference guidance.

Thunder focused regression after these two commits: **18 passed**.

Current branch HEAD at handoff creation begins from `4c3cb378a8fb0ada956f48b3b679dd22b5828b71`; the handoff commit itself will advance HEAD.

## Live Evidence at Latest Resume

The latest resume reacquired six evidence streams successfully:

- OHLCV: `evidence:equity:AAPL:4bc622ae5a559ed926625498`, 502 rows, 2024-09-10 through 2026-09-10.
- dark-pool price levels: `evidence:equity:AAPL:a000de447b4b7cf7503b6eb4`, 2184 rows, 2026-05-01 through 2026-09-10.
- unusual options flow alerts: `evidence:equity:AAPL:533a1d09752807036d5aef0d`, 500 rows; its raw epoch-like coverage metadata remains suspicious but is not the current repair scope.
- options Greek exposure by expiry: `evidence:equity:AAPL:af529e78d58cc88e80633916`, 24 rows, 2026-09-10.
- options flow by expiry: `evidence:equity:AAPL:0d767759ea19717160e9b85d`, 24 rows, 2026-09-10.
- FINRA OTC weekly: `evidence:equity:AAPL:8d8ba19cb1c2a66eed8a0876`, 5526 rows, 2021-12-06 through 2026-08-17.

## Exact Current Failure

After the stale-runtime-reference guidance repair passed 18 focused tests, the same AAPL campaign was resumed again (`RESUME4`). The process exited with:

```text
MTS_V4.orchestrator.ResearchLoopError: objective contract repair budget exhausted: Prior Analysis result payload is unavailable in the active campaign runtime: analysis-result:af7a5bf18b234aa18cd516a354299776. Do not reference this unavailable result_id again in analysis_inputs of the repaired request. If the same scientific work is still desired, the Research Director may reconstruct or regenerate the needed intermediate result by issuing a new executable Analysis request from currently available evidence or other currently available Analysis outputs, or may choose another scientific direction. A regenerated execution requires its own new request_id. Deterministic code will not select the replacement inputs, method, parameters, or scientific direction.
```

The corresponding decision journal proves Qwen did not converge on a repair. Decisions 11 through 14 all preserved the same unavailable `analysis-result:af7a5bf18b234aa18cd516a354299776` in `analysis_inputs`. Decisions 11-14 also kept request ID `rq_007_darkpool_data_integrity` and the same descriptive-statistics request. Therefore increasing the objective repair budget is not currently justified; it would likely only generate more repeated invalid requests.

This is the critical stopping point.

## Current Diagnosis

The deterministic validator is correctly detecting the runtime-invalid dependency and correctly returning the exact objective defect. The persistence lifecycle repair is also functioning: invalid repair requests are no longer automatically poisoning the durable RP merely because RD emitted them.

The unresolved problem is RD recovery behavior. Qwen receives explicit instruction that the prior Analysis payload no longer exists and must not be reused, yet it repeats that exact dead dependency across repair attempts. The immediate question is whether this should be treated as:

- a recovery-state representation problem in the orchestration/provider layer, because the impossible checkpointed request is still being framed primarily as a request to "repair" rather than as an objectively non-resumable execution whose prerequisite must first be reconstructed; or
- a Qwen capability/instruction-following limitation requiring escalation to a stronger AI authority.

Do not change architecture merely to accommodate Qwen without first inspecting the intended AI escalation/appeal design.

## Critical Newly Raised User Question — Sol Appeal Authority

Immediately before requesting this handoff, Dave stated that **Sol is supposed to be the appeal AI** and that he believed this architecture had already been built. He asked why Sol had not been running during the repeated Qwen repair failures.

This question was not resolved before handoff.

The root `ChatGPT.md` currently says the AI Research Director may use Qwen, Sol, or another explicitly approved AI reasoning provider and that AI is the scientific reasoning authority. It does not itself define an appeal/escalation protocol. Current code used in this live campaign is the Qwen-backed `ResearchPackageAwareResearchDirector` through the OpenAI-compatible local provider. No Sol escalation occurred during the observed repair failures.

The next session must therefore inspect GitHub for the actual implemented/provider architecture governing Qwen→Sol appeal/escalation before proposing any new mechanism. Specifically determine:

- whether a Sol appeal provider/router already exists in v4 source;
- whether it was designed but not wired into the current live runner;
- whether it exists only in a stale/superseded architecture document;
- what conditions were supposed to trigger appeal;
- whether Sol was intended to be scientific authority over Qwen on appeal, as Dave states;
- whether the current AAPL runner accidentally bypasses that path.

Do not assume absence merely because a quick code-search for the literal word `appeal` or `Sol` returns nothing on the default code index. Inspect the current branch source and relevant architecture/history directly.

## In-Progress Actions

No live AAPL runner is currently active. The most recent `RESUME4` process exited with status 1 after objective repair budget exhaustion.

Do not start another Qwen-only resume before resolving the appeal-routing question or explicitly choosing a single controlled recovery experiment. Repeated resumes have already shown the same behavior.

The campaign state should be preserved. Do not delete, reset, truncate, or rewrite `/home/ubuntu/mts-v4-aapl-qwen-e2e-20260910_163621` without a specific, reviewed reason. A pre-lifecycle-cleanup backup also exists on Thunder from the earlier cleanup operation.

## Next-Session Horizon

Start with repository truth, not assumptions.

First read root `ChatGPT.md` on the active branch in full. Then inspect the current branch Git history and source specifically for AI provider selection, authority routing, escalation, appeal, Qwen, Sol, model/provider adapters, runner construction, and any prior design/commit that introduced Sol authority. Compare implementation to the governing authority and to Dave's stated design intent that Sol is the appeal AI.

Then answer the user’s unresolved question: **why did Sol not run here?** The answer must distinguish clearly between architecture that exists, architecture that was proposed but superseded, and code actually wired into the current `run_aapl_qwen_e2e.py` path.

Only after that inspection should the next session recommend one of the following, based on evidence:

- wire an already-existing Sol appeal path into the current runner if it was omitted;
- repair an existing but broken escalation trigger/router;
- if no appeal architecture was ever implemented in v4, present that discrepancy explicitly before designing one;
- if the current problem is better solved by objective non-resumable-state representation before appeal, explain why and keep it a single-variable change.

Do not simply raise the repair budget. Do not persist temporary Analysis payloads into Nexus as a workaround. Do not deterministically choose the reconstruction science.

## Decision Ledger

Human-approved/frozen decisions that remain controlling:

- Root `ChatGPT.md` is governing authority; no silent deviation.
- AI owns scientific reasoning. Deterministic code may reject invalid execution contracts but not valid scientific judgment.
- MTS v4 is a clean reconstruction; B-series architecture is not controlling.
- Exploration should actively seek predictive structure and may use historical lookahead as discovery.
- Retrospective historical blind validation requires a ticker unseen before that verification campaign; live prospective prediction may use familiar tickers.
- Raw/reproducible source data and Analysis payloads are temporary; Nexus stores durable research learning/metadata/lineage, not reproducible datasets.
- Predictive verification status uses the approved cumulative success-rate floor of 0.60 after RD-declared minimum required trials; this is separate from trading/deployment utility.
- Request persistence occurs only after objective validation; checkpointing an RD decision must not make an invalid Analysis request durable as accepted execution.
- Exact replay of a pending request ID is allowed only for the same checkpointed pending execution identity during `RESUME_RESEARCH`; changed execution identity requires a new request ID.
- One-variable discipline applies to debugging and repairs.
- Do not increase repair budgets merely to mask repeated nonconvergent AI behavior.
- Dave states Sol is intended as the appeal AI; next session must verify and reconcile implementation with that intended architecture before inventing a replacement design.

ChatGPT recommendations made this session:

- strengthened stale-runtime-reference defect guidance without selecting science;
- after live proof still showed exact repetition, concluded that more repair attempts alone are not justified;
- suggested that an objectively non-resumable checkpoint may need to be represented to RD as a fresh-next-action decision rather than endlessly framed as repair of an impossible request;
- also suggested stronger AI escalation may be appropriate, but this must now be evaluated against the pre-existing Sol appeal design before implementation.

## Constraints and Non-Negotiables for Continuation

Do not use deterministic logic to pick scientific methods, inputs, hypotheses, thresholds, or research direction.

Do not fix process restart by making temporary Analysis rows durable in Nexus.

Do not conflate historical blind-verification eligibility with live prediction/trading eligibility.

Do not transplant stale v2/B-series deterministic scientific cognition into v4.

Do not commit `.env` or `.mts_rd_ai_env` or expose API keys.

Do not perform broad refactors while diagnosing this failure. Preserve one-variable causality.

Do not rely on stale architecture documents when they conflict with root `ChatGPT.md`; mark them as historical/proposed and resolve conflicts explicitly.

## Conflict Prompt for Future ChatGPT

If current implementation, an architecture document, a prior handoff, or a proposed repair conflicts with root `ChatGPT.md`, stop implementation and identify the conflict explicitly. Determine whether the implementation/document is stale or whether Dave must explicitly revise governance. Never silently reinterpret the authority model to make the code easier to run.

If Dave’s stated Sol-appeal requirement conflicts with current implementation, report the discrepancy before changing code. If it is already implemented but bypassed, identify exactly where and why.

## GitHub Inspection Record

Current repository: `davidbedwell/Momentum-Trading-System_v4`.

Current active branch: `mts-v4-unseen-ticker-verification-20260910`.

Root `ChatGPT.md` was read in full immediately before preparing this handoff.

Relevant current-branch files inspected in this session include:

- `ChatGPT.md`
- `MTS_V4/validation.py`
- `MTS_V4/research_package_provider.py`
- `tests/test_research_package_provider.py`
- `Architecture/Engines/RESEARCH_DIRECTOR_ARCHITECTURE.md`
- `Architecture/Technical-Design/RESEARCH_DIRECTOR_TECHNICAL_DESIGN.md`

Important warning: the two inspected RD architecture/design files are marked proposed/amended and contain deterministic-cognition concepts that conflict with the current root v4 authority model. They must not be treated as controlling merely because they remain in the repository.

At handoff time, quick current-index searches for literal `Sol appeal`, `appeal`, and similar terms returned no useful result. That is not proof that the implementation never existed; branch-specific source/history inspection remains required next session.

## Workflow for Next Session

Use GitHub inspection directly for repository state rather than asking Dave to manually print file after file. Use Thunder only for runtime evidence, live Qwen/Sol execution, or focused tests that cannot be established from GitHub.

Before any implementation change, re-read root `ChatGPT.md` on the exact active branch. For long shell commands that risk heredoc/paste corruption, minimize multiline terminal entry or provide a safer alternative. When asking Dave to retrieve runtime artifacts, provide exact commands and save requested output to `/home/ubuntu` or, when copying to his Mac, to `~/Downloads` with date-stamped filenames.

Thunder environment currently used for Qwen:

```bash
cd /home/ubuntu/Momentum-Trading-System_v4
export PATH=/home/ubuntu/vllm-venv/bin:$PATH
set -a
source .env
source .mts_rd_ai_env
set +a
export MTS_RD_BASE_URL="http://127.0.0.1:8000"
export MTS_RD_MODEL="/home/ubuntu/hf-cache/Qwen3-32B-AWQ"
export MTS_RD_TIMEOUT_SECONDS="600"
```

Latest campaign resume pattern:

```bash
cd /home/ubuntu/Momentum-Trading-System_v4
export MTS_E2E_RESUME_STATE_DIR="/home/ubuntu/mts-v4-aapl-qwen-e2e-20260910_163621"
LOG="/home/ubuntu/MTS_V4_AAPL_QWEN_E2E_RESUME_20260910_$(date +%H%M%S).txt"
python scripts/run_aapl_qwen_e2e.py > "$LOG" 2>&1 &
echo "E2E_PID=$!"
echo "E2E_LOG=$LOG"
```

Do not run that again automatically next session. First resolve the Sol appeal-routing question.

## Exact Restart Point

The next session should begin with this question:

> Dave says Sol is supposed to be the appeal AI. Inspect the current v4 branch and Git history to determine whether the Sol escalation/appeal architecture already exists, whether the AAPL Qwen E2E runner bypassed it, and why no appeal occurred after repeated objective-contract repair failure. Do not design or implement a new mechanism until that repository inspection is complete.

That is the current frontier.
