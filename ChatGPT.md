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

MTS is not a deterministic strategy tester. Deterministic machinery may execute, validate, reproduce, route, store, and enforce objective contracts, but it must not reduce the scientific mission to testing a fixed catalog of human-specified strategies or replace AI-directed scientific reasoning and exploration.

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

The AI Research Director is a governed scientific role, not necessarily a single model. It may use Qwen, Terra, Sol, Jev, or another explicitly approved AI reasoning provider or combination of providers, provided that the resulting system preserves AI scientific authority and the governance boundaries in this document.

The AI Research Director owns scientific judgment, including:

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

Different AI providers may perform different scientific roles according to demonstrated capability, reliability, cost, latency, and uncertainty. Provider assignment is an implementation and empirical-performance question rather than a permanent scientific hierarchy. A lower-cost provider may perform routine scientific reasoning when it demonstrates adequate reliability, while a stronger provider may be used for difficult, ambiguous, consequential, contradictory, or otherwise escalation-worthy scientific work.

No provider may become an unreviewable scientific bottleneck merely because it is cheaper. Uncertainty, repeated contract failure, material disagreement, scientifically consequential novelty, or evidence conflict must be capable of escalating to a stronger approved reasoning provider. Conversely, expensive providers should not be invoked merely by habit when a less costly approved provider has demonstrated reliable performance for the task.

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

Deterministic orchestration may route work among approved AI providers using objective operational criteria and governed escalation rules, but it may not encode scientific conclusions or use a deterministic proxy score to decide scientific merit.

## 5. Core v4 Research Flow

The intended high-level flow is:

**External source / prior predictive knowledge → Intake and governed context → temporary research cache → AI Research Director → Analysis Engine → governed result/finding → AI Research Director → Research Nexus / next scientific action**

The AI Research Director may internally distribute work among approved AI providers. Routine generative reasoning, bounded AI judgments, frontier scientific reasoning, and mathematical execution may therefore be performed by different components while remaining one governed scientific process.

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

### 8.1 AI Provider Roles and Cost Discipline

MTS should seek the lowest-total-cost approved AI capability that has demonstrated sufficient reliability for a given scientific workload, with escalation based on empirical failure, uncertainty, disagreement, or scientific difficulty rather than fixed call percentages. Total cost includes API charges, GPU/runtime expense, retries, repair work, engineering burden, and unnecessary downstream computation.

The intended provider roles are provisional and must be validated empirically:

- **Qwen** is the initial candidate for high-volume routine generative scientific reasoning, including ordinary RP formation and continuation, translation of known predictive knowledge into testable questions, interpretation of ordinary Analysis results, hypothesis refinement, follow-up design, and Nexus-context reasoning. Because locally/self-hosted Qwen inference can have negligible marginal per-call model cost once runtime is available, MTS should make a serious but time-efficient effort to obtain reliable Qwen performance before replacing it with a metered routine provider.
- **Terra** is the principal candidate comparator to Qwen for those same routine generative scientific workloads. Terra should displace or materially reduce Qwen's routine role only when controlled MTS-specific evidence shows that its improvement in scientific quality, reliability, operational simplicity, or downstream efficiency is substantial enough to justify its greater marginal inference cost.
- **Sol** is the stronger escalation provider for difficult scientific reasoning, consequential ambiguity, unresolved contract/semantic failures, conflicting evidence, important novel findings, difficult synthesis, adversarial scientific review, and other work for which routine providers have not demonstrated sufficient reliability.
- **Jev**, if approved and integrated, may be used for bounded AI judgments such as evidence classification, relevance assessment, support/weakening/contradiction judgments, confidence estimation, or other constrained semantic decisions. Jev must not become a deterministic scientific gate or silently prevent evidence from reaching generative RD reasoning merely because a bounded judgment scores it as unimportant.
- **Analysis Engine** performs mathematical and statistical execution requested by AI scientific reasoning. Numerical work that can be performed exactly and reproducibly by Analysis should not be repeatedly delegated to expensive generative models merely for convenience.

These roles are not permanent model entitlements. They may change when controlled evidence demonstrates a better capability/cost allocation, provided the scientific authority model remains intact.

### 8.2 Qwen Optimization Before Comparative Judgment

Before MTS decides whether Qwen should remain the routine generative provider or be displaced by Terra, Qwen must be brought to a fair best-achievable configuration within the approved architecture and governance.

This effort must be **time-efficient and bounded**. The goal is not to spend prolonged engineering effort making Qwen imitate a stronger model. MTS should first address the highest-leverage known causes of Qwen failure: provider/runtime correctness, prompt and context packaging, appropriate thinking-mode configuration, recommended generation parameters, schema/contract presentation, batch structure, repair behavior, and semantic continuation handling. Once Qwen reliably performs the representative routine workload, optimization should stop and controlled comparison should begin. If a small number of focused repair iterations do not materially improve a persistent failure mode, that failure should be recorded as part of Qwen's measured operational burden rather than triggering open-ended repair work.

Qwen must not be intentionally handicapped to make another provider appear superior, and governance must not be weakened merely to make Qwen pass. Known Qwen failures should be repaired at their actual semantic, packaging, runtime, or contract boundary rather than hidden by deterministic scientific cognition.

The goal is therefore the best **practically achievable** Qwen for MTS: sufficiently optimized to provide a fair comparison, but not subsidized by disproportionate engineering effort that would erase its cost advantage.

### 8.3 Qwen-versus-Terra Controlled Evaluation

After Qwen reaches a stable practically achievable configuration, Qwen and Terra should be compared on the same frozen MTS-specific workload and evidence wherever practicable.

The comparison should evaluate at least:

- scientific validity and quality of questions and hypotheses;
- preservation of known and novel research opportunities;
- correct interpretation of Analysis evidence;
- RP lineage and continuation semantics;
- contract/schema compliance and repair burden;
- false rejection or premature abandonment of worthwhile research;
- unnecessary or low-information Analysis work;
- ability to identify boundary conditions, contradictions, and useful follow-ups;
- escalation frequency;
- latency and operational reliability;
- total end-to-end cost, including model/API cost, GPU/runtime cost, retries, repair calls, engineering burden, and downstream Analysis work generated by each provider.

Generic public benchmarks may inform expectations but may not decide the MTS provider choice. MTS-specific controlled evidence is authoritative for provider assignment.

Because Qwen may have near-zero marginal inference cost in the intended self-hosted environment, modest Terra superiority alone is not sufficient reason to replace a scientifically adequate Qwen. Terra should earn routine-provider displacement by demonstrating a **material end-to-end MTS advantage** after its metered cost is included. If Qwen is scientifically adequate but Terra is materially better only for particular workload classes, MTS may route those classes to Terra while retaining Qwen elsewhere. If neither provider is sufficiently reliable, routine work must escalate rather than lowering scientific standards.

### 8.4 Batching and Escalation

AI scientific autonomy does not require one model call per scientific micro-decision. Where scientifically appropriate, the Research Director should formulate and evaluate coherent batches of related questions, Analysis requests, results, or RPs so that context and reasoning are reused efficiently.

Escalation should preserve the scientific record. A stronger provider should receive the relevant evidence, prior AI reasoning outputs, bounded judgments where applicable, Analysis results, Nexus context, contract failures, and unresolved questions necessary to make an informed scientific decision without needless reconstruction.

The AI Research Director may revise its own requests when objective execution feedback identifies a contract defect.

## 9. Analysis Engine

Analysis executes scientific and mathematical operations requested by the AI Research Director.

Analysis may expose a governed method catalog and objective execution contracts. It should not become a second scientific authority that substitutes deterministic method preference for RD judgment.

Analysis should support scientifically coherent batching where doing so preserves the requested scientific meaning and reduces unnecessary AI round trips. Analysis may calculate exact statistics, transformations, comparisons, matrices, and other reproducible outputs in bulk when requested by RD; this does not transfer scientific authority to Analysis.

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
