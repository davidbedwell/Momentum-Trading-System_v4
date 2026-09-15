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

### Bounded market-reading calibration

A neutral, predictor-only Analysis representation may be shown to an approved AI in a separately labeled market-reading calibration before an autonomous scientific campaign. This is permitted only to assess whether the AI can coherently describe the represented market structure, breadth, participation, trend, momentum, volatility, dispersion, sector structure, cross-sectional organization, contradictions, and uncertainty.

Such a calibration must be explicitly bounded to a fixed number of AI calls and a human-authorized spend ceiling. It may not consume historical outcomes or reserved-cohort outcomes; create or test predictive or trading hypotheses; recommend trades; claim predictive accuracy or scientific validation; promote findings to Nexus; or satisfy, weaken, or bypass any scientific-campaign readiness gate. Its output is a non-scientific capability assessment. Scientific discovery remains governed by the normal Research Director, Analysis, control, partition, validation, and promotion contracts.

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

No fixed threshold, horizon, normalization, indicator, method family, or trading rule should be privileged unless explicitly approved or scientifically justified by the AI Research Director from evidence. Trading-hypothesis candidacy, scientific validation, and candidacy for trading promotion are distinct. Their human-approved requirements are governed by `GOVERNANCE_AMENDMENT_2026-09-15_TRADING_HYPOTHESIS_LIFECYCLE.md`, which supersedes the former fixed cumulative `success_rate >= 0.60` verification rule. The prior greater-than-60-percent success at at-least-1.5-ATR combination remains a strong reference example, not an exclusive discovery, validation, or promotion threshold.

## 14. Human Utility and Risk

MTS should seek opportunities that are practically useful to a human trader, not merely statistically nonzero.

Reward must be considered in relation to risk, adverse path, and time.

Adverse movement is defined relative to the hypothesized opportunity direction. What level of adverse movement is acceptable is a human utility/risk question, not a universal market fact.

Trading expectancy must be calculated from the chronological outcome of a frozen, human-executable policy. Favorable movement occurring after the policy would have stopped, invalidated, expired, or otherwise exited must not be credited. A scientifically supported relationship may remain durable knowledge without satisfying the separate economic requirements for trading promotion.

The approved trading-promotion rejection floor requires positive conservative net expectancy, point-estimate net expectancy of at least `0.15R`, and point-estimate gross expectancy of at least twice upper-bound all-in costs. Meeting that floor authorizes prospective paper testing only and must not become the Research Director's research objective.

The future Stock Screener Engine must record every eligible current candidate and rank eligibility separately from capital selection. The future Trading Engine may select only the best portfolio-compatible candidates under governed capital and risk constraints. Outcomes for selected and unselected eligible candidates must remain separately measurable so portfolio selection does not bias evaluation of the underlying hypothesis.

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

Future work affecting predictive hypotheses, blind validation, prospective paper testing, screening, or trading promotion must also read `GOVERNANCE_AMENDMENT_2026-09-15_TRADING_HYPOTHESIS_LIFECYCLE.md`.

The permanent sections above are governing authority. The Current Shift Handoff below is operational continuation state and may be replaced at session closeout without changing governance.

Use Git history, architecture documents, tests, and current source as the implementation record. If a future implementation appears to conflict with this document, stop and determine whether the implementation is wrong or the governance needs explicit human revision. Do not silently reinterpret the authority model.

---

# Current Shift Handoff — 2026-09-12

## Session Summary

This session completed the 20-year OHLCV history-depth repair, verified it end-to-end, and then identified the next scientific-continuation defect before any new Sol campaign was launched.

The accidental OHLCV boundary was literal source configuration: `YFinanceDailyOhlcvSource.period` was `"2y"`. It has now been changed to `"20y"` and committed/pushed.

Current branch:

- `mts-v4-cross-subject-generalization-20260912`

Current authoritative implementation commit before this handoff update:

- `dd52dcb` — `Expand OHLCV history to twenty years`

Thunder working tree was clean after that commit/push.

## 20-Year OHLCV Repair — COMPLETE

Changed:

`MTS_V4/live_sources.py`

from:

```python
@dataclass(frozen=True, slots=True)
class YFinanceDailyOhlcvSource:
    period: str = "2y"
```

to:

```python
@dataclass(frozen=True, slots=True)
class YFinanceDailyOhlcvSource:
    period: str = "20y"
```

This was intentionally a narrow source-depth repair. It did not change Sol prompts, scientific priorities, Analysis selection, hypothesis selection, cross-subject logic, or alternative-data history limits.

UW remains provider/recent-history limited, including existing 730-day settings where applicable. FINRA/options continue using their own available/provider coverage. Do not truncate master OHLCV to the shortest alternative-data history.

### Verification

Direct yfinance AAPL acquisition:

- requested period: `20y`
- rows: `5031`
- coverage start: `2006-09-12`
- coverage end: `2026-09-11`
- `20Y_PROVIDER_ACQUISITION: PASS`

Actual MTS `YFinanceDailyOhlcvSource.acquire()` verification:

- `SOURCE_IDENTITY: YFINANCE_DAILY`
- `EVIDENCE_TYPE: OHLCV`
- `ROW_COUNT: 5031`
- `COVERAGE_START: 2006-09-12`
- `COVERAGE_END: 2026-09-11`
- provenance included `provider=yfinance`, `period=20y`, `interval=1d`
- `MTS_20Y_INTAKE_ACQUISITION: PASS`

Regression test added:

`Tests/mts_v4/test_yfinance_20y_default.py`

It asserts:

```python
YFinanceDailyOhlcvSource().period == "20y"
```

Targeted regression: `1 passed`.

Full gate used in this session: `370 passed`.

Do not revert the 20-year OHLCV repair merely to align with shorter UW/FINRA/options history. Source-dependent history is the intended scientific boundary: OHLCV-derived questions may use long OHLCV history, while mixed-source questions naturally use the overlap needed for those sources.

## Scientific Consequence of the History Repair

The existing 11-ticker corpus was largely researched using approximately two years of OHLCV. Do not discard that work and do not silently reinterpret it as 20-year evidence.

Treat prior results as:

> recent-period exploratory relationships discovered within approximately a two-year research window

The intended next scientific phase is to revisit those 11 tickers using the newly available long OHLCV history while preserving the prior work as historical scientific context.

Sol must remain free to determine whether old relationships:

- persist over longer history;
- disappear;
- reverse;
- are temporally/regime dependent;
- require conditioning;
- should be reformulated;
- should be rejected;
- or whether different questions deserve investigation.

Deterministic code must not choose which old findings to retest or prioritize.

## Critical New Stop Point — Same-Subject Revisit Context Gap

Do **not** immediately launch the 11-ticker 20-year revisit.

At session end, the current scientific-context code was audited and a specific revisit-context gap was identified.

Relevant files:

- `MTS_V4/subject_scientific_context.py`
- `MTS_V4/cross_subject_context.py`
- `scripts/run_sol_batched_one_subject.py`

Current `load_prior_subject_science()` intentionally excludes the active ticker's packages:

```python
if subject_id == active_subject_id:
    continue
```

That is correct for cross-subject context.

Likewise, `build_cross_subject_context()` intentionally excludes the active subject from canonical cross-subject scientific memory. Its documentation explicitly says existing subject-local Nexus/RP context remains separate.

That is also correct during continuation of an existing campaign.

However, `scripts/run_sol_batched_one_subject.py` starts a new state directory and new Nexus for a fresh subject run. Therefore, if AAPL were simply rerun as a fresh 20-year subject, Sol would receive:

- newly reacquired 20-year AAPL evidence;
- durable scientific packages from other subjects;
- canonical cross-subject memory with active AAPL excluded;

but it may **not** receive AAPL's own old approximately two-year findings/packages.

That is wrong for the intended 20-year revisit.

## Required Revisit Semantics

For a designated 20-year revisit, Sol must receive all of the following simultaneously.

### 1. Same-subject prior science

For AAPL, expose AAPL's prior durable scientific learning as nonbinding historical scientific context, including where available:

- originating questions;
- originating rationales;
- hypotheses;
- predictive hypotheses;
- findings;
- unresolved issues;
- close reasons;
- final assessments;
- provenance/status.

Do **not** expose as reusable revisit state:

- old raw market rows;
- old reusable Analysis payloads;
- deterministic scientific ranking;
- a mandatory retest agenda.

The old approximately two-year findings remain prior exploratory evidence. Sol may test, challenge, reformulate, condition, defer, ignore, or reject them.

### 2. Cross-subject prior science

Continue providing the existing compact durable scientific outputs from all **other** subjects.

Do not change existing cross-subject exclusion semantics merely to solve this revisit problem.

### 3. Canonical cross-subject memory/frontier

Continue providing the canonical transferable scientific memory/frontier with the active subject excluded from the specifically cross-subject portion.

### 4. Current reacquired evidence

Reacquire current evidence normally:

- approximately 20-year OHLCV where available;
- UW/FINRA/options at whatever history their sources actually provide.

Do not resurrect the old two-year raw execution state simply to expose its scientific conclusions.

Conceptually the Sol revisit payload should contain four distinct scientific/evidence channels:

```text
same_subject_prior_science
    active ticker's old durable scientific learning

prior_subject_scientific_context
    durable science from other tickers

cross_subject_scientific_memory
    transferable memory/frontier, active ticker excluded

current evidence
    newly reacquired 20-year OHLCV + provider-limited alternative data
```

The old same-subject science is context, not a deterministic instruction to reproduce or validate any specific proposition.

## Immediate Next Engineering Question

Before launching Sol, answer this exact question against current HEAD/code:

> What is the smallest governed change that lets a designated 20-year revisit campaign expose the active ticker's prior durable approximately two-year scientific learning to Sol, while preserving existing cross-subject context, reacquiring fresh 20-year OHLCV, avoiding old raw/Analysis state, and leaving all scientific selection and interpretation to Sol?

Likely direction, subject to current-code audit:

- add a compact same-subject prior-science loader analogous to the current compact prior-subject package loader;
- expose it to Sol under a clearly separate payload field such as `same_subject_prior_science`;
- activate it only for an explicit revisit mode/path instead of silently changing ordinary fresh-subject semantics;
- preserve provenance and status;
- exclude raw rows and reusable Analysis payloads;
- do not rank/select findings;
- do not create a deterministic retest list;
- keep current cross-subject behavior unchanged.

Do not launch Sol until this same-subject revisit-context issue is resolved and tested.

## Important Corpus Completeness Caveat

The locally preserved 11-ticker package corpus contains 44 unique research-package JSON documents:

- AAPL: 4
- AMD: 14
- AMZN: 3
- BA: 3
- GOOGL: 3
- JPM: 2
- META: 3
- MSFT: 4
- NVDA: 1
- TSLA: 3
- XOM: 4

Total: 44.

However, package-only extraction may not include every promoted Nexus finding. XOM is a known example: a promoted finding existed in Nexus even though its research package showed zero findings.

Therefore, before declaring `same_subject_prior_science` complete, audit whether research packages alone are sufficient or whether durable Nexus/canonical records for the active ticker must also be included. Avoid silent duplication and do not deterministically rank duplicate scientific records.

## Existing Tentative Predictive Propositions

The existing corpus includes tentative recent-period propositions involving:

- AAPL normalized-slope H20 exhaustion;
- AAPL relative-volume H20 recovery;
- AMD SMA20/H10;
- BA ATR14/H20;
- GOOGL relative-volume H3/H5;
- JPM normalized-slope H20 exhaustion;
- MSFT ATR14/H20 normalized favorable behavior;
- NVDA ATR20-normalized one-day downshock/T+5;
- META range-position20/H20 mean reversion;
- TSLA wide Bollinger-band/H20 positive return.

All remain tentative/exploratory and unvalidated. Because the original master OHLCV boundary was approximately two years, these must be understood as recent-period exploratory propositions until revisited over deeper evidence.

Do not encode them into deterministic retest logic.

## Cross-Ticker Scientific Families — Context, Not Rules

Recurring structures have appeared around:

- extension/exhaustion;
- participation/relative volume;
- volatility.

Evidence is heterogeneous and sometimes contradictory.

Examples:

- AAPL/JPM extension measures suggested H20 exhaustion;
- META range-position suggested related mean-reversion behavior;
- XOM initially appeared similar but failed exact chronological stability, with strong earlier-period behavior disappearing later;
- AMD normalized slope showed continuation rather than exhaustion and was concentrated in the later portion of its short history.

Therefore do not hard-code `extension -> reversal`.

Likewise do not hard-code `high relative volume -> bullish` or `high volatility -> bullish`.

Sol must determine whether these structures are ticker-specific, regime-specific, conditional, transferable, coincidental, or unsupported.

## Alternative-Data Resource Patch Already Completed

Current branch already contains these resource-gap commits:

- `ffe5611` — Expand neutral Analysis representation resources
- `293ef44` — Preserve categorical group identity and numeric strings
- `f11e00d` — Expand governed liquidity measurements
- `991a335` — Test XOM resource gap repairs

Those repairs added capabilities including:

- numeric-string coercion at the Analysis boundary;
- categorical group-key preservation;
- exact categorical filtering;
- datetime components;
- parent-row-position composition;
- richer neutral liquidity measurements;
- Corwin-Schultz spread **estimate**, not an actual quote-spread measurement.

Several older alternative-data packages were closed because the previous Analysis apparatus could not represent the evidence. Those may now be legitimate scientific reopen candidates, but Sol must decide whether they deserve attention.

Still unresolved scientifically/data-wise:

- FINRA prediction-time/publication availability and no-look-ahead treatment;
- repeated historical options snapshots / validated historical alert sequence;
- no actual historical quoted/effective spread or order-book depth.

## Sequential Learning Requirement

The intended future learning loop remains:

```text
Ticker 1
→ durable learning
→ Ticker 2 sees prior durable learning
→ durable learning
→ Ticker 3 sees 1+2
→ ...
```

Most of the first 11 tickers did not receive this complete cumulative sequence because much of the corpus predates the final cross-subject architecture.

AAPL → MSFT → XOM approximated the intended sequential approach more closely.

After the 11-ticker deep-history revisit is correctly supported, the planned next 10 new tickers should receive true cumulative sequential learning.

Do not launch those next 10 yet.

Do not launch the dedicated multi-ticker generalization campaign yet.

## Local + Transferable Science Requirement

The human explicitly requires **both**:

1. ticker-local scientific discovery;
2. transferable/cross-subject scientific discovery.

Do not sacrifice local market-state research in favor of generalized market-state research.

Sol may use prior cross-subject knowledge to challenge or condition local findings, but local subject discovery remains independently important.

## Cross-Subject Context Architecture Already Present

Current fresh-subject architecture provides:

- canonical cross-subject scientific memory/frontier;
- compact durable prior-subject packages;
- no raw prior-subject rows;
- no reusable prior Analysis payloads;
- no deterministic scientific ranking/agenda.

`SubjectContextSolBatchResearchDirector` injects prior-subject scientific context into the Sol batch payload.

`load_prior_subject_science()` deduplicates exact package content and excludes the active subject.

These exclusion semantics should remain intact for cross-subject context. The revisit repair should add a **separate same-subject context channel**, not redefine cross-subject context to include the active ticker.

## Operational State

Thunder repository:

`/home/ubuntu/Momentum-Trading-System_v4`

Thunder instance ID:

`0`

Mac transfer command:

```bash
tnr scp 0:/home/ubuntu/<filename> ~/Downloads/
```

For timestamp wildcards, escape the wildcard when needed.

Mac canonical repository:

`/Users/davidbedwell/Documents/Momentum-Trading-System_v4`

Use the repository venv:

```bash
.venv/bin/python -m pytest ...
```

Do not use `/usr/bin/python` for pytest.

Large diagnostics should be saved to timestamped `.txt` on Thunder and accompanied by an explicit Mac transfer command.

Do not give the human copyable shell commands containing placeholders or `...`.

Do not ask the human to paste secrets.

Sol runtime variables remain:

- `MTS_SOL_BASE_URL`
- `MTS_SOL_MODEL`
- `MTS_SOL_API_KEY`

## Decision Ledger — 2026-09-12

Approved/frozen during this session:

- Correct the accidental yfinance OHLCV default from approximately two years to approximately twenty years.
- Keep UW/FINRA/options history independently provider-limited rather than truncating OHLCV to their depth.
- Preserve existing approximately two-year findings as prior exploratory scientific evidence rather than discarding or overwriting them.
- Revisit existing tickers with deeper OHLCV before proceeding to the next new-ticker sequence.
- Sol, not deterministic code, decides what old findings to challenge, retest, reformulate, condition, ignore, or reject.
- Preserve both ticker-local discovery and transferable/cross-subject discovery.
- Do not launch the 11-ticker revisit until same-subject prior scientific learning is available to Sol in the new deep-history campaign.
- Same-subject prior science must be exposed separately from cross-subject context; do not contaminate cross-subject semantics merely to solve revisit continuity.
- Old raw rows and reusable Analysis payloads must not be carried forward as the mechanism for scientific continuity.
- Do not launch the next 10 new tickers or the dedicated multi-ticker generalization campaign yet.

## Immediate Next Session Action

1. Read this entire `ChatGPT.md` before changing code.
2. Verify current branch/HEAD and clean status; implementation baseline should include `dd52dcb` plus this handoff-only update.
3. Inspect the current same-subject durable sources: research packages, Nexus records, and canonical memory records, including the known XOM package/Nexus discrepancy.
4. Determine the smallest explicit revisit-mode implementation that exposes active-ticker durable prior science without old raw/Analysis state.
5. Add focused tests proving:
   - ordinary fresh-subject behavior is unchanged;
   - cross-subject context still excludes the active subject;
   - explicit revisit mode exposes active-subject durable prior science;
   - same-subject revisit context contains no raw rows/reusable Analysis payloads and no deterministic ranking/agenda;
   - 20-year OHLCV is reacquired normally.
6. Run the full gate before any Sol API spend.
7. Only after those tests pass should a first 20-year revisit campaign be launched.

Do not treat the history-depth repair itself as incomplete. That repair is finished, tested, committed, and pushed. The unresolved issue is specifically **scientific continuity for the active ticker during a new deep-history revisit campaign**.

## Economic-Efficiency Repair — 2026-09-12

The first AAPL deep-history revisit was stopped at the human authorization boundary after 22 Sol calls and $14.78406 of Sol spend. The archived audit showed 2,964,685 prompt tokens, 146,266 completion tokens, no HTTP/provider retries, and 383 Analysis records. Sol was performing the scientifically intended autonomous exploration; the dominant defect was the economic interface around that work, not inappropriate scientific breadth.

The human approved the following repair while preserving Sol as the scientific authority:

- Analysis precomputes a versioned, neutral standard OHLCV substrate before the first Sol call. It contains the complete governed measurement inventory, the 11 recurring predictor representations observed in the audited AAPL preliminary program, all standard H1/H3/H5/H10/H20 path outcomes, descriptive measurements, full/chronological-half unranked Pearson and Spearman measurements, and calendar outcome summaries. It creates no hypothesis or finding, ranks nothing, and does not prevent Sol from opening new RPs or requesting any other relationship.
- The first Sol call receives full prior-subject, same-subject revisit, cross-subject, method, and substrate context.
- Every continuing Sol decision must author a cumulative `research_state.scientific_continuation_state`. Later calls transport that AI-authored state, the newest batch report, exact chainability catalog, and compact RP summaries instead of replaying full prior science, prior plan bodies, and open-package execution journals.
- Deterministic code transports but never writes or summarizes the scientific continuation state.
- Group-aggregate scalar/category results remain visible to Sol even though reusable row datasets remain behind the raw-row transport boundary.
- The eleven-ticker sequential revisit runner now defaults to a $5.00 human authorization ceiling per ticker. The ceiling remains an operational stop, not a scientific truncation instruction to Sol.

Offline AAPL-scale verification found:

- prior-decision transport was 78.3% smaller when the old AI-authored `other_state` was used as a proxy for the new cumulative continuation state;
- 165,908 bytes of full prior/same-subject context are removed from every continuation call after being supplied on the begin call;
- the AAPL-scale neutral substrate covered 5,031 rows, 196 governed measurement columns, 11 precomputed predictor directions, 35 forward outcomes, and 385 unranked relationship records;
- the RD-visible substrate was 308,728 JSON bytes (approximately 77,182 tokens at a conservative four-bytes-per-token estimate), while its 42.7 MB reusable panel remained campaign-local and was not transported to Sol;
- the full test gate passed with 429 tests.

These are measured transport and coverage improvements, not a claim that Sol will finish every ticker for $5. A paid replay is still required to measure actual call-count adaptation. Do not resume or launch a paid sequence without an explicit human instruction after this repair is pushed and preflighted.


## Universe Scientific Partition and Compact Transfer — 2026-09-15

The human approved a strict separation between complete derived-store coverage and scientific outcome exposure.

The server derived market store may contain the complete universe. Before historical universe outcomes reach Sol/Qwen, stable security identities must be assigned to an immutable exact-size `DISCOVERY`, `VERIFICATION_A`, and `VERIFICATION_B` partition. Cohort sizes are explicit human governance inputs; deterministic code has no default scientific split. Full-universe predictor-time context may support ranks, breadth, and other contemporaneous measurements without itself consuming a security's future outcomes.

The universe discovery runner may expose historical outcomes only for the frozen `DISCOVERY` cohort. Reserved verification cohorts remain inaccessible until a separate locked-hypothesis blind-verification path is implemented and tested. Outcome participation must not be hidden by administrative labeling.

Campaign transfer to the local Nexus is compact. Transfer scientific metadata/findings, Research Packages, compact Analysis reports/decisions, lineage/context, exposure records, and run/spend summaries. Do not transfer the server's derived-market Parquet corpus, raw/reacquirable data, Analysis cache datasets, or bulky AI transport/replay files.

Authoritative detail:

`Documentation/2026-09-15_MTS_V4_UNIVERSE_SCIENTIFIC_PARTITION.md`

## Full-Universe Neutral Market Representation — 2026-09-15

Before any Sol/Qwen universe interpretation or predictive discovery, Analysis must build a deterministic, predictor-time-only representation of the complete authorized universe as of an explicit observation boundary. For the current daily derived store, the supported boundary is date `D` at completed `DAILY_CLOSE`; the system must not claim arbitrary intraday `T` state from daily evidence.

The neutral representation must give RD compact, reproducible context for current cross-sections and multi-session market structure, including returns, trend position and slope, momentum, participation/breadth, volatility, relative volume, dispersion, drawdown/range position, sector grouping when labels are available, rank persistence, feature dependence, coverage, and known capability gaps. Large reproducible panels remain server-side or campaign-local and are not transported to Sol or the local Nexus.

This preprocessing:

- may consume the full-universe predictor stream;
- must not consume the historical outcome stream;
- creates no hypothesis, finding, scientific ranking, trading signal, or prediction;
- must preserve the current-universe/survivorship and non-PIT classification limitations of calibration evidence;
- may use the frozen membership CSV to restore ticker and current sector labels, but may not describe those labels as authoritative historical PIT classifications;
- leaves all interpretation, hypothesis creation, research direction, and scientific significance judgments to AI RD; and
- must report zero Sol calls when run as the standalone Stage 2A preprocessing command.

Predictive universe discovery is a separate later stage. It may receive full-universe predictor context, but historical outcomes remain restricted to the frozen `DISCOVERY` cohort under the universe scientific-partition rules above. Reserved verification outcomes remain hidden until an explicitly governed blind-verification path is authorized.

The human has determined that authoritative historical point-in-time index membership is not a prerequisite for the present-day market-understanding and predictive-discovery program. The frozen universe is classified as `CURRENT_MEMBER_CONDITIONED`: former constituents are absent, and results describe the available histories of the current-member population. This scope does not create a material disqualifying bias for the approved present-day objective, but the results may not be represented as an authoritative historical S&P 500 reconstruction or generalized to securities outside the observed population. This decision removes historical membership acquisition as a readiness gate; it does not relax prediction-time integrity for predictors, outcomes, earnings, shares, timestamps, or blind validation.

The authoritative Stage 2A Analysis artifact and the AI transport view are distinct. The full artifact must remain unchanged for audit and reproducibility. The AI transport may use a documented schema-plus-array encoding to eliminate repeated field names and may apply the same predeclared descriptive field set uniformly to every multi-window measurement. It may not select features, sectors, horizons, correlation pairs, or persistence records based on their values. Full distributions and reusable datasets remain available in the authoritative Analysis artifact but are not automatically inserted into the paid AI prompt.

The AI transport may replace repeated measurement/feature names with shared indexed dictionaries and may normalize floating-point presentation to eight significant digits. This is a reasoning-context encoding only. Transport-rounded values are not authoritative for thresholds, validation, promotion, or trading decisions; those operations must use the full-precision Analysis result or execute again against the derived store.

For the 503-security calibration campaign, the human approved exact scientific cohort sizes of `303 DISCOVERY / 100 VERIFICATION_A / 100 VERIFICATION_B`. The frozen assignment must be stratified jointly by current sector and relative current-market-cap tercile, with salted randomization inside each stratum and a balance audit published before outcomes are exposed. Market capitalization must enter through Intake and is authorized only as a current governance-balancing attribute; it is neither historical PIT evidence nor an RD predictor in this partition operation.

Securities previously researched by Sol cannot remain in either verification cohort. Before universe outcome exposure, replace each such reserved member with an unexposed `DISCOVERY` member from the exact same sector/current-market-cap stratum. Preserve 303/100/100 totals and all joint-stratum counts, issue a new partition identity, retain the old partition as superseded, and publish the exact swap audit. Fail closed when no exact in-kind replacement exists.

## Context-Enriched Same-Subject Reconsideration — 2026-09-15

When a previously researched ticker is reconsidered after material evidence or governance changes, preserve and expose its prior durable science rather than describing the campaign as a from-scratch evaluation. Supply the new evidence and the changed standards neutrally, then ask Sol whether those changes affect any prior analysis, recommendation, finding, hypothesis, unresolved question, or conclusion. Deterministic code must not prescribe a retest list or decide which prior work survives; Sol retains that scientific judgment and may repeat, extend, revise, reject, or leave prior analyses unchanged as the evidence warrants.

For the AAPL and XOM reconsiderations, the new evidence is time-aligned ticker, full-current-member-universe, and current-sector predictor context at every historical daily observation `T`, plus the separately bounded current market-reading calibration. Historical ticker outcomes are authorized for exploration only, and only when the ticker belongs to the repaired frozen `DISCOVERY` cohort. Current market reading is current-applicability context, not historical evidence.

Sol must also receive the amended candidate definition. A scientific observation or finding is not automatically a trading-hypothesis candidate. New candidacy requires exploratory support for a specific falsifiable `T`-to-future relationship and a human-executable chronological policy with positive estimated net expectancy after estimated all-in costs. The policy must define entry, direction/instrument, prediction point, favorable exit, adverse-risk unit, stop/invalidation, maximum horizon, gap/fill treatment, position management, costs, and applicability. No favorable movement after the policy would have exited may be credited.

There is no universal candidacy win-rate, ATR-movement, or payoff threshold; the former greater-than-60-percent/1.5-ATR rule is not the candidate definition. Scientific validation remains separate and requires untouched evidence plus the governed uncertainty assessment. Trading-promotion candidacy remains later and separate, with conservative net expectancy greater than zero, point-estimate net expectancy at least `0.15R`, and point-estimate gross expectancy at least `2C`. These are rejection floors, not discovery targets. A material revision to a frozen proposition or policy requires a new hypothesis identity; prior records are not overwritten.
