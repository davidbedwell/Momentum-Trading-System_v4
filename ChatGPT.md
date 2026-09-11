# ChatGPT Continuation Authority — MTS v4

This file is the root continuation authority for ChatGPT-assisted development of Momentum Trading System v4.

MTS v4 is a clean reconstruction. It is not a continuation of the prior RD-B series architecture. The prior B-series may be inspected as historical evidence or as a source of isolated implementation techniques, but it is not authoritative for v4 design.

## 1. Governing Purpose

The purpose of MTS is to discover reproducible relationships between market information observable at time T and subsequent market behavior at T+1 onward, with sufficient predictive value in direction, magnitude, timing, continuation or reversal, and path quality to be practically exploitable as trades.

MTS is therefore fundamentally a prospective-prediction research system, not merely a descriptive market-analysis system. Descriptive and contemporaneous findings are useful when they help identify, explain, discriminate, refine, or falsify conditions that may have subsequent predictive force.

A profitable price move is not necessarily a useful trading opportunity. Human utility depends on reward in relation to risk, path, adverse movement, and time.

The system must actively support scientifically defensible predictive discovery without hard-coding the scientific conclusions it is intended to discover.

## 2. Human Authority and AI Engineering Latitude

The human establishes:

- the mission and purpose of MTS;
- governance and authority boundaries;
- non-negotiable scientific and safety constraints;
- approved external resources, credentials, and operational limits;
- final approval for changes that alter those governing principles.

Within those boundaries, ChatGPT has broad engineering latitude during the creation of v4.

ChatGPT may design, reorganize, refactor, replace, simplify, or create modules, interfaces, abstractions, tests, orchestration, validation mechanisms, and internal architecture as necessary to bring the approved vision and governance to life through code.

ChatGPT does not need separate approval for ordinary implementation choices that remain within this document's authority boundaries. It must not silently change the mission, scientific authority model, Nexus retention boundary, or other non-negotiable governance rules in order to make implementation easier.

## 3. Scientific Authority

AI is the scientific reasoning authority in MTS v4.

The AI Research Director may use Qwen, Sol, or another explicitly approved AI reasoning provider. The AI Research Director owns scientific judgment, including:

- research-question formation;
- hypothesis formation and revision;
- interpretation of evidence;
- selection of scientific methods and analyses;
- scientific parameter choice where the parameter expresses scientific judgment;
- actively seeking prospective relationships between presently observable conditions and subsequent market behavior during exploration;
- determining relevance, novelty, uncertainty, contradiction, discrimination value, and next research direction;
- deciding whether evidence supports, weakens, rejects, generalizes, qualifies, or leaves a hypothesis unresolved;
- determining when a finding is scientifically significant enough for durable research memory;
- deciding whether further scientific work is required.

Deterministic code may not overrule valid scientific judgment merely because deterministic logic considers another scientific choice better.

The controlling rule is:

> Deterministic code may reject invalid execution contracts. It may not reject valid scientific judgment.

## 4. Deterministic Authority

Deterministic code may enforce objective execution and governance constraints, including:

- schema validity;
- identifiers and references;
- method existence and capability availability;
- parameter type, shape, and cardinality;
- required-field presence;
- artifact existence;
- lineage and provenance integrity;
- temporal and look-ahead restrictions applicable to the current research phase;
- historical blind-verification subject eligibility;
- permissions and authority claims;
- reproducibility mechanics;
- resource and execution safety;
- objective cache and lifecycle rules.

When a valid scientific request cannot execute because an objective contract is incomplete or invalid, deterministic code should return the exact defect to the AI Research Director for repair.

Deterministic code must not:

- generate scientific questions as a substitute for AI reasoning;
- form scientific hypotheses as a substitute for AI reasoning;
- rank or select research questions by deterministic scientific-value scoring;
- infer or choose scientific methods from question wording as a substitute for RD choice;
- resolve scientific ambiguity;
- invent scientifically meaningful missing parameters;
- determine scientific relevance, convergence, adequacy, novelty, plausibility, or importance;
- redirect scientifically valid research because deterministic logic prefers another direction.

## 5. Core v4 Research Flow

The intended high-level flow is:

**External source → Intake Engine → temporary research cache → AI Research Director → Analysis Engine → governed result/finding → Research Nexus → AI Research Director → next scientific action**

The exact software decomposition may evolve, but the authority boundaries may not be violated without explicit human approval.

## 6. Intake Engine

Intake is responsible for acquiring and preparing evidence for research.

Its responsibilities may include:

- source acquisition;
- source identity and provenance;
- schema and coverage validation;
- normalization and staging;
- neutral semantic description of what the evidence represents;
- safe transfer into temporary campaign storage.

Intake does not decide what evidence means scientifically and does not determine scientific research direction.

## 7. Temporary Research Cache

Raw or otherwise reproducible market data belongs in temporary research/campaign storage, not in the Research Nexus.

Examples include OHLCV, off-exchange records, block-equity data, options data, and other reacquirable or reconstructable source datasets.

The temporary cache may exist for as long as active research requires it. After durable findings and necessary lineage have been preserved and the campaign no longer requires the source data, the cache should be eligible for cleanup.

If the source data is needed again, Intake should reacquire or reconstruct it according to source and resource policy.

## 8. AI Research Director

The AI Research Director is the first scientific actor after evidence preparation.

It reasons backward from the MTS mission and available evidence to determine:

- what scientific question should be asked;
- what evidence is relevant;
- what Analysis operation should be performed;
- what parameters are scientifically appropriate;
- what the result means;
- whether an observed or contemporaneous relationship has scientifically testable implications for later market behavior;
- what should be investigated next.

During EXPLORATION, the AI Research Director should actively seek scientifically defensible predictive structure. It should ask whether conditions observable at time T precede, discriminate, or improve prediction of subsequent direction, magnitude, timing, continuation or reversal, path quality, or interactions among evidence streams. Historical look-ahead is an explicitly legitimate discovery tool during this phase when scientifically useful.

The AI Research Director should not manufacture predictive claims merely to satisfy the mission. It should reject unsupported relationships just as readily as it advances promising ones. A falsifiable predictive hypothesis that later fails blind validation is scientifically useful and should not be avoided merely because it may fail.

The AI Research Director may revise its own requests when objective execution feedback identifies a contract defect.

## 9. Analysis Engine

Analysis executes scientific and mathematical operations requested by the AI Research Director.

Analysis may expose a governed method catalog and objective execution contracts. It should not become a second scientific authority that substitutes deterministic method preference for RD judgment.

Analysis returns governed results with sufficient metadata and lineage for RD interpretation and durable promotion when appropriate.

## 10. Research Nexus

The Research Nexus is durable research memory, not a reproducible-data warehouse.

Its primary contents are:

- ticker or subject metadata, including durable provenance sufficient to determine whether a ticker has previously entered MTS historical analysis;
- significant findings promoted by the AI Research Director;
- durable hypotheses or research-state records when needed;
- provenance and lineage needed to understand those findings;
- relationships among findings, subjects, hypotheses, and prior research;
- unresolved scientific issues that materially affect future research;
- compact context necessary for future RD reasoning.

Nexus shall not be used as the durable repository for raw or otherwise reproducible market datasets.

Nexus should preserve what MTS learned, not warehouse the data from which it learned it.

Not every Analysis result belongs in Nexus. The AI Research Director determines scientific significance. Deterministic code may validate the promoted record's schema, lineage, integrity, provenance, and objective historical-verification eligibility but may not decide scientific importance.

## 11. B-Series Status

The prior RD-B series is abandoned as an architecture for v4.

B-series code may be mined only as a parts source. A component enters v4 only if it is independently justified under the v4 authority model.

Do not preserve B-series behavior merely because it existed previously.

In particular, deterministic scientific-cognition mechanisms such as deterministic hypothesis generation, candidate-question generation, scientific-value scoring, question selection, scientific critics, convergence evaluators, method-suitability ranking, scientific specification resolution, and deterministic scientific continuation must not be transplanted as scientific authority.

Reusable mechanical code may be retained where appropriate, including hashing, canonicalization, persistence mechanics, objective validation, lineage, orchestration, cache management, provider infrastructure, and other non-scientific capabilities.

## 12. Reconstruction Rule

MTS v4 is built by positive admission, not subtraction.

Do not copy modern v2 wholesale and attempt to remove undesirable behavior afterward.

For each candidate component from v2 or the B-series, ask:

> Would we design this component today under the rule that AI owns scientific reasoning?

If yes, it may be kept or adapted.

If it exists primarily to imitate scientific intelligence deterministically, leave it behind.

The old v2 tree remains useful as a forensic reference and comparison control.

## 13. Scientific Exploration and Validation

EXPLORATION and VALIDATION intentionally operate under different information rules because they serve different scientific purposes.

During EXPLORATION, the central objective is predictive discovery. The AI Research Director should actively investigate whether information observable at time T has subsequent predictive force at T+1 onward. Historical look-ahead may be used freely where scientifically appropriate to discover candidate zones, relationships, horizons, directionality, continuation or reversal behavior, magnitude, timing, path characteristics, cross-evidence interactions, or other predictive structure.

Exploration should encourage prospective reasoning rather than stop at contemporaneous description. When evidence supports it, the AI Research Director should convert promising relationships into explicit, falsifiable tentative predictive hypotheses suitable for later blind testing. It should also freely reject candidate relationships that do not withstand exploratory scrutiny.

For retrospective historical blind verification, a ticker may serve as the unseen verification subject only if MTS had not previously analyzed that ticker before the historical verification campaign began. Findings and tentative predictive hypotheses may arise from one or many previously analyzed tickers and may then be tested against a genuinely unseen ticker. After those historical verification results are durably recorded, that ticker may enter unrestricted EXPLORATION and its results and later findings may be folded into the cumulative research corpus. New or materially revised hypotheses arising from that enlarged corpus should be historically verified on another ticker that was unseen at the start of its verification campaign.

This historical unseen-ticker rule does not prohibit live prospective prediction or trading on a ticker MTS has analyzed before. Once the prediction point is genuinely current and the future outcome has not occurred, Qwen may make prospective predictions on previously analyzed tickers, including tickers used extensively in prior research. Such live predictions are not made invalid merely because the ticker is scientifically familiar. MTS must remain able to trade and continue evaluating signals on familiar tickers.

Within any historical blind trial, the prediction stage must also be protected from temporal look-ahead. The AI Research Director may use only information available through the declared prediction point, must make and lock the prediction before hidden future information is exposed, and may then evaluate the revealed outcome against the frozen success definition.

The purpose of the validation restrictions is not to suppress predictive reasoning. They make exploratory claims honestly testable while preserving MTS's ability to make genuine prospective predictions in live or future-facing use.

Do not confuse exploratory discovery, retrospective historical verification, and genuine live prospective prediction. The unseen-ticker restriction applies to retrospective historical blind verification, not to current or future-facing prediction/trading.

No fixed threshold, horizon, normalization, indicator, method family, or trading rule should be privileged unless explicitly approved or scientifically justified by the AI Research Director from evidence. Human-approved governance thresholds, such as an explicitly approved predictive-verification success-rate floor, are permitted as objective validation rules and do not substitute for AI scientific judgment about the hypothesis itself.

## 14. Human Utility and Risk

MTS should seek opportunities that are practically useful to a human trader, not merely statistically nonzero.

Reward must be considered in relation to risk, adverse path, and time.

Adverse movement is defined relative to the hypothesized opportunity direction. What level of adverse movement is acceptable is a human utility/risk question, not a universal market fact.

Do not hard-code universal numerical utility thresholds without explicit approval.

## 15. External Systems and Credentials

During the v4 reconstruction, avoid requiring human interaction with local machines, Thunder, paid data vendors, API keys, or other credentials until the architecture and local/GitHub codebase are ready for end-to-end testing.

Where practical, defer credential-dependent work to the final integration stage.

When v4 reaches that stage, provide the human with a concise activation procedure covering only what is necessary, such as:

- pulling the completed v4 branch/repository;
- creating or activating the local environment;
- entering required credentials or environment variables;
- connecting to Thunder or another approved compute resource;
- running smoke tests and production proofs.

Do not embed secrets or credentials in source control.

## 16. Testing and Evidence

Tests should prove authority boundaries and behavior, not merely encode obsolete implementation assumptions.

Prefer tests that establish:

- AI scientific authority is preserved;
- exploratory research actively supports scientifically defensible prospective/predictive discovery;
- retrospective historical verification is mechanically rejected on a ticker already analyzed before that verification campaign;
- a genuinely unseen ticker remains eligible for retrospective historical blind verification;
- live prospective prediction remains allowed on previously analyzed tickers;
- blind validation prevents temporal look-ahead at the prediction stage without weakening exploratory freedom;
- deterministic validation remains objective;
- invalid execution contracts fail with precise feedback;
- valid scientific requests are not rejected because of deterministic scientific preference;
- lineage and temporal integrity are preserved;
- temporary data does not become unintended durable Nexus storage;
- significant findings can be durably reconstructed and related;
- the complete RD → Analysis → RD research loop can operate autonomously once infrastructure and credentials are available.

## 17. Continuation Discipline

Future ChatGPT sessions working on v4 must read this file before making architectural or implementation changes.

The permanent sections above are governing authority. The Current Shift Handoff below is operational continuation state and may be replaced at session closeout without changing governance.

Use Git history, architecture documents, tests, and current source as the implementation record. If a future implementation appears to conflict with this document, stop and determine whether the implementation is wrong or the governance needs explicit human revision. Do not silently reinterpret the authority model.

---

# Current Shift Handoff — 2026-09-11

## Session Summary

The session moved MTS v4 from the completed six-subject Sol adaptive campaign into a discovery-space architecture audit and an approved remediation branch.

Completed six-subject campaign: `mts-v4-sol-six-20260911_174430`. Subjects were JPM, TSLA, BA, META, AMZN, and GOOGL. The campaign artifacts were preserved off-Thunder on the user's Mac and SHA256-verified against Thunder copies before later work. The campaign was scientifically signal-poor but architecturally informative: roughly 50 Analysis executions represented only about six substantive relationship propositions, with repeated use of short-horizon univariate/marginal Spearman workflows. Sol itself learned that raw marginal screens were low-yield and authored a broader frontier involving normalized shocks, interactions, abnormal activity, regimes, relative moves, non-overlapping event studies, and richer outcomes.

Audit conclusion approved by the human: the discovery-space problem is real. The problem is not merely the old exact 5-day/-5% bounceback formulation. The executable Analysis vocabulary and subject lifecycle make narrow propositions cheap to exhaust and richer science comparatively difficult. RP closure can also effectively become subject closure without an explicit AI-owned distinction between exhaustion of one Research Package and adequate exploration of the ticker. A separate concern was identified that the legitimate unseen-ticker rule for retrospective blind validation could be interpreted as a priority for unexposed tickers during ordinary EXPLORATION. The human approved correcting all of these issues without deterministic scientific menus, rankings, fixed horizons, indicators, or hypotheses.

## Current Branch and Tested Baseline

Known-good pre-audit integrated branch/commit:

- branch: `mts-v4-sol-adaptive-batch-runner-20260911`
- commit: `83278f306e91e6b0faffa6999352d5d36d4b078a`
- prior full gate on that integrated content: 316/316 default tests passed.

Current remediation branch:

- `mts-v4-discovery-space-expansion-20260911`
- created from `83278f306e91e6b0faffa6999352d5d36d4b078a`
- current known branch commit before this handoff update: `ae01bfe4be0d7adea5324ce7e402233c15ba49eb`

Thunder live checkout is `/home/ubuntu/Momentum-Trading-System_v4` and was switched to the remediation branch. The user ran the focused new tests: 9 passed. The default suite: 316 passed. The combined explicit gate `python -m pytest -q Tests tests` reported **440 passed**. Note that `pyproject.toml` currently has `testpaths = ["Tests"]`, so plain `python -m pytest -q` does not collect lowercase `tests/`; use the combined command when gating this branch unless test configuration is deliberately changed.

## Discovery-Space Changes Implemented

The remediation branch adds/changes:

1. `MTS_V4/sol_primary_provider.py`
   - reinforces that prior memory/frontier informs but does not delimit EXPLORATION;
   - tells Sol to distinguish exhaustion of the current RP from adequate exploration of the subject;
   - closing one RP is not evidence the ticker is adequately explored;
   - if a materially different scientifically worthwhile proposition remains, Sol should continue by opening another RP;
   - this is not a mandate to manufacture analyses.

2. `MTS_V4/subject_selection.py`
   - separates prior exposure, durable completed scientific memory, and retrospective blind-validation eligibility;
   - explicitly makes exposure status scientifically neutral for EXPLORATION;
   - retrospective blind-validation eligibility must not rank exploration subjects;
   - revisiting completed or incomplete prior subjects is allowed when accumulated knowledge makes that scientifically preferable;
   - no inherited lookback/horizon/threshold/method/hypothesis becomes a within-subject contract.

3. `MTS_V4/discovery_methods.py` (new)
   - exposes existing governed deterministic computation families as an RD-selectable Analysis capability rather than a deterministic scientific ranking;
   - adds a neutral reusable arithmetic transform for AI-authored add/subtract/multiply/divide derived features, intended to make normalized and interaction representations executable without deterministic choice of variables or meaning.

4. `MTS_V4/bootstrap.py`
   - registers the discovery method catalog and Analysis implementations into the live runtime.

5. Tests
   - `tests/test_discovery_capability_expansion.py`
   - expanded `tests/test_exploration_discovery_space.py`
   - initial failures were brittle `inspect.getsource()` exact-string assertions, not behavior defects; assertions were repaired to verify the same semantics without dependence on physical string splitting.

Do not replace these AI-authority-preserving changes with deterministic diversification requirements such as mandatory 2/5/10/20-day horizons, required indicators, fixed interaction menus, or deterministic scientific ranking. The human explicitly approved broadening capability and progression while preserving Sol's scientific authority.

## Critical Stop Point / Unresolved Packaging Defect

After the 440-test gate, the human authorized a one-subject experiment restricted to previously researched Sol subjects to see whether the broadened architecture actually changes Sol's research behavior.

The attempted experiment did **not start**. It failed immediately during import:

`ModuleNotFoundError: No module named 'Core'`

Trace path:

- `scripts/run_sol_adaptive_batch.py`
- imports `MTS_V4.bootstrap`
- imports new `MTS_V4.discovery_methods`
- `discovery_methods.py` imports `from Core.deterministic_computation import execute_computations`
- production script environment cannot resolve `Core`.

This was hidden by pytest because repository test configuration adds the repository root to Python's test path. The project packaging configuration currently discovers only `MTS_V4*`:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["MTS_V4*"]
```

Therefore the next implementation task is to repair the actual packaging/bootstrap contract so the production runtime can import the existing `Core` deterministic-computation package without a `PYTHONPATH=.` shell workaround. The user said “do it,” but immediately afterward ended the session and requested this handoff. **No packaging fix has yet been committed.** Do not claim otherwise.

Recommended next-session sequence:

1. Read this entire `ChatGPT.md` first.
2. Inspect the `Core` package structure and packaging implications before editing. The likely fix is to include the required `Core` package(s) in setuptools discovery, but verify package boundaries and avoid unintentionally packaging stale/unwanted code.
3. Add a regression test that exercises the production-style import/entry path without relying on pytest's repository-root `pythonpath`, so this defect cannot recur silently.
4. Reinstall editable environment as needed and run `python -m pytest -q Tests tests`; require the full combined gate to pass.
5. Run a production import/preflight of `scripts/run_sol_adaptive_batch.py` before consuming Sol API calls.
6. Only then retry the one-subject revisit experiment.

Do not use `PYTHONPATH=.` as the permanent solution.

## Planned One-Subject Revisit Experiment

Purpose: test whether the architecture repair broadens actual autonomous research, not whether a profitable signal is found.

Candidate set should contain only already researched Sol subjects, e.g.:

`MSFT,NVDA,XOM,JPM,TSLA,BA,META,AMZN,GOOGL`

Prior exposure list should preserve:

`AAPL,MSFT,XOM,NVDA,AMD,JPM,TSLA,BA,META,AMZN,GOOGL`

Use the completed six-subject campaign's `cross_subject_memory.json` as seed memory. Subject limit 1. Max analyses per subject 100. Sol chooses which prior ticker deserves re-examination and owns the science. Do not tell it which horizon, indicator, interaction, or hypothesis to pursue.

Evaluate the resulting decision journal/state, not merely the terminal summary. Strong evidence of improvement would include materially different representations, normalization, interactions, regimes, different horizons where scientifically warranted, richer use of deterministic measurement families, or multiple RPs when distinct propositions remain worthwhile. A quick return to `one variable → 5-day future → several correlations → close` would indicate the discovery architecture remains inadequate.

The failed attempted run created names based on timestamp `20260911_200813`:

- state target: `/home/ubuntu/mts-v4-sol-revisit-20260911_200813`
- log: `/home/ubuntu/MTS_V4_SOL_REVISIT_20260911_200813.txt`

It failed before scientific execution, so it contains no valid campaign result and must not be interpreted as research evidence.

## Scientific Memory / Exposure Status

Preserved clean Sol-only seed from earlier work:

- `/home/ubuntu/MTS_V4_SOL_ONLY_SEED_MSFT_NVDA_XOM_20260911.json`
- SHA256 `dd17bfded31e36edc764d09ff064fefaa502bebd5d348a9fc09e1501fa8fe77a`
- contains MSFT, NVDA, XOM only; no AAPL/Qwen scientific seed.

Completed six-subject campaign:

- batch: `mts-v4-sol-six-20260911_174430`
- state: `/home/ubuntu/mts-v4-sol-six-20260911_174430`
- log: `/home/ubuntu/MTS_V4_SOL_SIX_20260911_174430.txt`
- state tarball: `/home/ubuntu/MTS_V4_SOL_SIX_20260911_174430_STATE.tar.gz`
- completed artifacts copied to Mac and hash-verified.

Exposure distinctions remain important:

- AAPL: prior exposure, substantive prior campaign Qwen; do not treat Qwen findings as trusted Sol scientific seed; not retrospectively blind/unseen.
- MSFT: completed Sol campaign/durable memory.
- NVDA: completed Sol campaign/durable memory; tentative subject-specific severe-loss rebound candidate remains unvalidated.
- XOM: completed Sol campaign/durable memory.
- AMD: prior exposure/incomplete Sol campaign due infrastructure/HTTP failure; no durable scientific conclusion.
- JPM, TSLA, BA, META, AMZN, GOOGL: completed in the six-subject Sol campaign and now exposed; durable campaign memory exists.

Retrospective blind-validation unseen-subject eligibility is distinct from exploration priority. During EXPLORATION, prior exposure versus unexposed status must not be deterministically ranked. Sol may revisit old subjects when scientifically preferable.

## Infrastructure State Relevant to Continuation

Thunder instance ID 0 / UUID `n5u2mzxc`, RTX A6000, 6 vCPU, 48 GB RAM, 100 GB disk. Connect with `tnr connect 0`; do not use raw SSH.

Live repo: `/home/ubuntu/Momentum-Trading-System_v4`
Virtual environment: `/home/ubuntu/Momentum-Trading-System_v4/.venv`
Use `python -m pytest`.

`.env` is the authoritative runtime secrets/config file and must not be printed or committed. It contains required UW/FINRA/Sol variables. The retired `.mts_rd_ai_env*` backups were moved out of the repo to `/home/ubuntu/mts-private-env-backups`, with restricted permissions. Do not delete them without explicit cleanup review.

GitHub auth works via `gh`; explicit credential helper configuration was required on the old Ubuntu `gh` version. Do not ask the user to type GitHub username/password into Thunder.

Dependency/bootstrap repairs already integrated before this discovery branch include `yfinance`, `pandas`, `jsonschema`, and runtime `pyarrow`; prior integrated full gate reached 316/316.

## Snapshot / Closeout Status

The human explicitly deferred the golden Thunder snapshot until closeout, then chose to end this session while the packaging defect remains unresolved. **No golden snapshot was created in this session.** Do not create one automatically next session; first finish and validate the discovery-space production path and revisit experiment unless the human changes priorities.

Campaign artifacts and private env backups were intentionally preserved. Do not delete scientific/audit material merely because copies exist elsewhere without an explicit cleanup decision.

## Decision Ledger

Human-approved/frozen decisions this session:

- Discovery space remains too narrow after nine analyzed tickers; breadth of actual propositions matters more than nominal analysis/ticker count.
- Audit Analysis/tool affordances and Sol behavior rather than assuming Sol alone is at fault.
- Broaden executable Analysis capability without deterministic scientific menus or rankings.
- Make RP exhaustion distinct from subject exhaustion while leaving the decision to continue/stop with Sol.
- Retrospective blind-validation unseen-ticker requirements must not become an EXPLORATION priority signal.
- Sol must be allowed to revisit previously analyzed tickers as its scientific knowledge broadens.
- Test the repair by forcing the candidate universe to previously seen Sol tickers, while letting Sol choose which ticker and what science to perform.
- If the revisit exhausts quickly in another narrow workflow, treat that as evidence the discovery-space problem remains unresolved; if horizons/representations/propositions broaden materially, begin allowing systematic re-analysis of prior tickers.
- Do not use a `PYTHONPATH=.` workaround as the permanent production fix for the newly exposed `Core` import defect.
- Golden snapshot deferred; no snapshot at this stopping point.
