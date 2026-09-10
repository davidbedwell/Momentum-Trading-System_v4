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

- ticker or subject metadata;
- significant findings promoted by the AI Research Director;
- durable hypotheses or research-state records when needed;
- provenance and lineage needed to understand those findings;
- relationships among findings, subjects, hypotheses, and prior research;
- unresolved scientific issues that materially affect future research;
- compact context necessary for future RD reasoning.

Nexus shall not be used as the durable repository for raw or otherwise reproducible market datasets.

Nexus should preserve what MTS learned, not warehouse the data from which it learned it.

Not every Analysis result belongs in Nexus. The AI Research Director determines scientific significance. Deterministic code may validate the promoted record's schema, lineage, integrity, and provenance but may not decide scientific importance.

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

Once a predictive hypothesis is frozen for VALIDATION, the prediction stage must be protected from look-ahead. The AI Research Director may use only information available through the declared prediction point, must make and lock the prediction before hidden future information is exposed, and may then evaluate the revealed outcome against the frozen success definition. Historical, forward, holdout, or otherwise out-of-sample testing should be used as appropriate to evaluate predictive validity.

The purpose of the validation restriction is not to suppress predictive reasoning. It is to make the predictive claims discovered during exploration falsifiable and honestly testable.

Do not confuse exploratory discovery with prospective validation, and do not weaken exploratory predictive discovery merely to simplify validation controls.

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
- blind validation prevents look-ahead at the prediction stage without weakening exploratory freedom;
- deterministic validation remains objective;
- invalid execution contracts fail with precise feedback;
- valid scientific requests are not rejected because of deterministic scientific preference;
- lineage and temporal integrity are preserved;
- temporary data does not become unintended durable Nexus storage;
- significant findings can be durably reconstructed and related;
- the complete RD → Analysis → RD research loop can operate autonomously once infrastructure and credentials are available.

## 17. Continuation Discipline

Future ChatGPT sessions working on v4 must read this file before making architectural or implementation changes.

This file intentionally contains no historical shift log. v4 starts with a clean development history.

Use Git history, architecture documents, tests, and current source as the implementation record. Add separate architecture or handoff documents when they materially improve continuation, but do not turn this root authority file into a chronological work diary.

If a future implementation appears to conflict with this document, stop and determine whether the implementation is wrong or the governance needs explicit human revision. Do not silently reinterpret the authority model.
