# ChatGPT Continuation Authority — MTS v4

This file is the root continuation authority for ChatGPT-assisted development of Momentum Trading System v4.

MTS v4 is a clean reconstruction. It is not a continuation of the prior RD-B series architecture. The prior B-series may be inspected as historical evidence or as a source of isolated implementation techniques, but it is not authoritative for v4 design.

## 1. Governing Purpose

The purpose of MTS is to identify, scientifically evaluate, validate, retain, and exploit reproducible market conditions, predictive strategies, and theories that can identify subsequent price movements with sufficient magnitude, directionality, timing, and path quality to be practically exploitable as trades.

Candidate predictive knowledge may originate from established market knowledge, published or otherwise externally supplied research and trading theory, prior MTS knowledge, or novel AI-directed discovery. Novelty is not required for a relationship, strategy, or theory to be valuable to MTS, and prior recognition or conventional acceptance does not make one inherently more valuable than a novel candidate.

MTS may make efficient use of known effective or credibly supported predictive strategies and theories rather than requiring the AI Research Director to rediscover established market knowledge from raw evidence. Such prior knowledge is a legitimate source of research questions, hypotheses, candidate strategies, conditioning variables, mechanisms, and interactions. Prior knowledge does not become accepted MTS truth merely because it is established, published, conventional, or externally supplied: MTS must evaluate it under the same applicable scientific, temporal, evidentiary, and validation standards used for internally generated hypotheses.

MTS must not systematically bias scientific attention toward either known or novel predictive relationships merely because of their origin. The AI Research Director should allocate research attention according to scientific promise, evidence, uncertainty, practical trading relevance, information value, and available resources. Known knowledge may prevent unnecessary rediscovery, while unexplained evidence, interactions, residual structure, boundary conditions, and novel hypotheses remain fully legitimate research directions.

A profitable price move is not necessarily a useful trading opportunity. Human utility depends on reward in relation to risk, path, adverse movement, and time.

The system must support rigorous evaluation and practical use of known predictive knowledge as well as open-ended scientific discovery, without hard-coding scientific conclusions merely because they are known, conventional, or novel.

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
- determining relevance, novelty, uncertainty, contradiction, discrimination value, and next research direction;
- deciding whether evidence supports, weakens, rejects, generalizes, qualifies, or leaves a hypothesis unresolved;
- determining when a finding is scientifically significant enough for durable research memory;
- deciding whether further scientific work is required.

Known predictive strategies, theories, and externally supplied research may inform the AI Research Director's scientific judgment and may be investigated directly without first being independently rediscovered by MTS. The AI Research Director remains responsible for deciding how such prior knowledge should be tested, qualified, combined, generalized, rejected, or used, subject to applicable governance and validation requirements. The origin of a hypothesis as known or novel must not itself determine its scientific priority or disposition.

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

Known predictive knowledge, strategies, and theories may enter the research process as governed scientific context or candidate hypotheses without being treated as validated findings until MTS has evaluated them under the applicable standards.

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

It reasons backward from the MTS mission, available evidence, prior MTS knowledge, and relevant known predictive strategies or theories to determine:

- what scientific question should be asked;
- what evidence is relevant;
- what Analysis operation should be performed;
- what parameters are scientifically appropriate;
- what the result means;
- what should be investigated next.

The AI Research Director may use credible prior predictive knowledge where useful rather than spending research resources merely rediscovering it. It must also remain alert to evidence that known relationships fail, reverse, depend on previously unidentified conditions, interact with other evidence streams, or reveal novel predictive structure. Prior knowledge is context, not a scientific preference: evidence and scientific judgment determine what deserves continued investigation.

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

Known external strategies or theories should be distinguishable from findings empirically established by MTS so that prior knowledge is not silently promoted into validated MTS knowledge without evidence.

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

During exploratory learning, look-ahead may be used where explicitly appropriate to discover candidate zones, relationships, or hypotheses.

Exploration includes both the scientific evaluation and refinement of known predictive strategies or theories and the search for previously unidentified predictive relationships. MTS need not consume research resources recreating established knowledge merely to claim internal discovery. Where credible prior predictive knowledge exists, the AI Research Director may begin from that knowledge and investigate whether it survives, how it should be conditioned, where it fails, how it interacts with other evidence, and whether it is practically exploitable in the MTS context.

Neither known nor novel predictive structure receives an inherent scientific preference because of its origin. The AI Research Director retains authority to pursue established strategies, anomalies, unexplained residuals, cross-evidence interactions, contradictory observations, and novel hypotheses according to their scientific and practical merit.
