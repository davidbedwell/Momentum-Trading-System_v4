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

The human establishes the mission and purpose of MTS; governance and authority boundaries; non-negotiable scientific and safety constraints; approved external resources, credentials, and operational limits; and final approval for changes that alter those governing principles.

Within those boundaries, ChatGPT has broad engineering latitude during the creation of v4. ChatGPT may design, reorganize, refactor, replace, simplify, or create modules, interfaces, abstractions, tests, orchestration, validation mechanisms, and internal architecture as necessary to bring the approved vision and governance to life through code.

ChatGPT does not need separate approval for ordinary implementation choices that remain within this document's authority boundaries. It must not silently change the mission, scientific authority model, Nexus retention boundary, or other non-negotiable governance rules in order to make implementation easier.

## 3. Scientific Authority

AI is the scientific reasoning authority in MTS v4.

The AI Research Director is a governed scientific role, not necessarily a single model. It may use Qwen, Terra, Sol, Jev, or another explicitly approved AI reasoning provider or combination of providers, provided that the resulting system preserves AI scientific authority and the governance boundaries in this document.

The AI Research Director owns scientific judgment, including research-question and hypothesis formation, interpretation of evidence, scientific method and parameter choice, relevance, novelty, uncertainty, contradiction, discrimination value, scientific disposition, durable significance, and next research direction.

Known predictive strategies, theories, and externally supplied research may inform the AI Research Director's scientific judgment and may be investigated directly without first being independently rediscovered by MTS. Their origin as known or novel must not itself determine scientific priority or disposition.

Different AI providers may perform different scientific roles according to demonstrated capability, reliability, cost, latency, and uncertainty. Lower-cost providers may perform routine scientific reasoning when sufficiently reliable, while stronger providers may handle difficult, ambiguous, consequential, contradictory, novel, or escalation-worthy work.

No provider may become an unreviewable scientific bottleneck merely because it is cheaper. Uncertainty, repeated contract failure, material disagreement, scientifically consequential novelty, or evidence conflict must be capable of escalating to a stronger approved reasoning provider.

Deterministic code may reject invalid execution contracts. It may not reject valid scientific judgment.

## 4. Deterministic Authority

Deterministic code may enforce objective execution and governance constraints including schema validity, identifiers, method/capability availability, parameter type and shape, required fields, artifact existence, lineage and provenance integrity, temporal restrictions, permissions, reproducibility mechanics, resource safety, and objective lifecycle rules.

When a valid scientific request cannot execute because an objective contract is incomplete or invalid, deterministic code should return the exact defect to the AI Research Director for repair.

Deterministic code must not generate hypotheses or questions as a substitute for AI reasoning; rank research by deterministic scientific-value scoring; choose scientific methods from wording as a substitute for RD choice; resolve scientific ambiguity; invent scientifically meaningful missing parameters; determine scientific relevance, convergence, adequacy, novelty, plausibility, or importance; or redirect valid research because deterministic logic prefers another direction.

Deterministic orchestration may route work among approved AI providers using objective operational criteria and governed escalation rules, but it may not encode scientific conclusions or use a deterministic proxy score to decide scientific merit.

## 5. Core v4 Research Flow

The intended high-level flow is:

**External source / prior predictive knowledge → Intake and governed context → temporary research cache → AI Research Director → Analysis Engine → governed result/finding → AI Research Director → Research Nexus / next scientific action**

The AI Research Director may internally distribute work among approved AI providers. Routine generative reasoning, bounded AI judgments, frontier scientific reasoning, and mathematical execution may therefore be performed by different components while remaining one governed scientific process.

Known predictive knowledge, strategies, and theories may enter as governed scientific context or candidate hypotheses without being treated as validated findings until MTS evaluates them under applicable standards.

## 6. Intake Engine

Intake acquires and prepares evidence for research, including source acquisition, identity and provenance, schema and coverage validation, normalization and staging, neutral semantic description, and safe transfer into temporary campaign storage. Intake does not decide what evidence means scientifically or determine scientific direction.

## 7. Temporary Research Cache

Raw or otherwise reproducible market data belongs in temporary research/campaign storage, not in the Research Nexus. This includes OHLCV, off-exchange records, block-equity data, options data, and other reacquirable or reconstructable source datasets.

The cache may exist as long as active research requires it. Once durable findings and necessary lineage are preserved and the campaign no longer requires source data, it should be eligible for cleanup and later reacquisition if needed.

## 8. AI Research Director

The AI Research Director is the first scientific actor after evidence preparation. It reasons backward from the MTS mission, available evidence, prior MTS knowledge, and relevant known predictive strategies or theories to determine the scientific question, relevant evidence, Analysis operation, scientifically appropriate parameters, interpretation, and next action.

The AI Research Director may use credible prior predictive knowledge rather than spending resources merely rediscovering it. It must also remain alert to failure, reversal, unidentified conditions, interactions, residuals, and novel predictive structure. Prior knowledge is context, not a scientific preference.

### 8.1 AI Provider Roles and Cost Discipline

MTS should seek the lowest-total-cost approved AI capability that has demonstrated sufficient reliability for a given scientific workload, with escalation based on empirical failure, uncertainty, disagreement, or scientific difficulty rather than fixed call percentages. Total cost includes API charges, GPU/runtime expense, retries, repair work, engineering burden, and unnecessary downstream computation.

The intended roles are provisional and empirically validated:

- **Qwen** is the initial candidate for high-volume routine generative scientific reasoning. Because self-hosted Qwen can have negligible marginal model cost once runtime is available, MTS should make a serious but time-efficient effort to obtain reliable Qwen performance.
- **Terra** is the principal comparator to Qwen for routine generative scientific workloads and should materially reduce Qwen's role only when controlled MTS evidence shows an end-to-end advantage sufficient to justify its greater marginal inference cost.
- **Sol** is the stronger escalation and independent scientific-challenge provider for difficult reasoning, consequential ambiguity, unresolved semantic failures, conflicting evidence, important novel findings, synthesis, adversarial review, and other work for which routine providers have not demonstrated sufficient reliability.
- **Jev**, if approved and integrated, may perform bounded AI judgments such as evidence classification, relevance, support/weakening/contradiction, and confidence estimation. Jev must not become a scientific gate or silently prevent evidence from reaching generative RD reasoning.
- **Analysis Engine** performs mathematical and statistical execution requested by AI scientific reasoning. Exact reproducible numerical work should not be repeatedly delegated to expensive generative models merely for convenience.

These roles are not permanent model entitlements and may change when controlled evidence demonstrates a better capability/cost allocation without changing the scientific authority model.

### 8.2 Qwen Optimization Before Comparative Judgment

Before deciding whether Qwen remains the routine generative provider or is displaced by Terra, Qwen must be brought to a fair, practically achievable configuration within approved architecture and governance.

This effort must be time-efficient and bounded. Address the highest-leverage causes of Qwen failure: provider/runtime correctness, prompt and context packaging, thinking-mode configuration, generation parameters, schema/contract presentation, batch structure, repair behavior, and semantic continuation handling. Once Qwen reliably performs representative routine work, optimization should stop and controlled comparison begin. Persistent failure after a small number of focused repair iterations becomes measured Qwen operational burden rather than justification for open-ended repair.

Qwen must not be intentionally handicapped, and governance or scientific standards must not be weakened merely to make Qwen pass. Failures should be repaired at their actual semantic, packaging, runtime, or contract boundary rather than hidden by deterministic scientific cognition.

### 8.3 Frozen-Sol Sequential Provider Evaluation

Provider evaluation must begin by establishing the independent Sol control **before** Qwen or Terra performs the comparison campaign on the selected ticker. The purpose is to prevent the lower-cost provider's research path, summaries, classifications, omissions, or framing from influencing the scientific reference against which it will be evaluated.

For a selected benchmark ticker and frozen research state, MTS shall first run a **standalone Sol control campaign**. Sol receives the same governed starting evidence, PIT state, prior predictive knowledge available under the benchmark, Nexus starting state, Analysis capabilities, resource constraints, and research objective that will later be supplied to the candidate hybrid provider. Sol must not receive Qwen, Terra, Jev, or candidate-hybrid conclusions or research trajectories from that benchmark. Sol performs the ticker research independently.

When the standalone Sol campaign is complete, its research record shall be **frozen before the candidate-provider campaign begins**. The frozen control should preserve Sol's RPs/hypotheses, Analysis requests, governed Analysis outputs, interpretations, continuations, closures, findings, unresolved questions, Nexus-relevant conclusions, material negative results, and resource/cost record. The frozen control must not be retrospectively changed because of discoveries made by Qwen, Terra, Jev, or later reconciliation. Any later Sol insight belongs to the reconciliation record, not to the original control.

After the Sol control is frozen, the benchmark proceeds sequentially:

1. **Qwen hybrid arm.** Qwen, in its best practically achievable approved configuration, performs the routine RD role against the same frozen starting state and evidence. Analysis and governed escalation may operate as defined by MTS, but the Qwen arm may not inspect the frozen Sol control during its research.
2. **Comparison and Sol reconciliation.** After the Qwen record is frozen, Sol compares the complete Qwen-hybrid record against the already-frozen standalone Sol control. The reconciliation must identify shared findings, Qwen-only findings, Sol-only findings, contradictory findings, materially different conditioning/boundary conclusions, differences in useful Analysis work, missed opportunities, false leads, and total cost/resource differences. Sol must evaluate whether any variance is scientifically or economically meaningful and, where appropriate, identify discriminating follow-up tests rather than merely choosing a preferred narrative.
3. **Stop if Qwen is adequate.** If Qwen preserves the scientifically and economically material capability of the standalone Sol control at materially lower total cost, Terra need not be tested merely for completeness. Qwen may remain the routine provider subject to continued audit and escalation safeguards.
4. **Terra only if meaningful deficiency remains.** If the Qwen comparison shows meaningful scientific or economic loss, Terra receives the **same original frozen starting state and evidence**, not Qwen's resulting state and not Sol's frozen conclusions. Terra performs the same benchmark ticker independently in the candidate routine-provider role. Terra may not inspect either prior arm while conducting its research.
5. **Terra comparison against the same Sol control.** Once Terra's record is frozen, Sol compares Terra against the original frozen standalone Sol control and, where useful, against the frozen Qwen arm. The original Sol control remains unchanged. The purpose is to determine whether Terra materially recovers capability Qwen lost and whether that recovery justifies Terra's metered cost.

The frozen Sol control is a **reference scientific trajectory, not infallible ground truth**. Qwen or Terra may identify valid findings Sol missed. Reconciliation must therefore evaluate variance symmetrically rather than automatically treating disagreement with Sol as candidate-provider error. Where arms disagree materially, underlying governed evidence and discriminating Analysis should determine the scientific disposition.

The benchmark should evaluate scientific validity and hypothesis quality; preservation of known and novel opportunities; evidence interpretation; RP lineage and continuation semantics; contract compliance and repair burden; false rejection or premature abandonment; unnecessary Analysis work; boundary-condition and contradiction detection; useful follow-ups; escalation frequency; latency; operational reliability; material trading implications; and total end-to-end cost including model/API, GPU/runtime, retries, repair calls, engineering burden, and downstream computation.

Generic public benchmarks may inform expectations but may not decide MTS provider choice. MTS-specific controlled evidence is authoritative. Because Qwen may have near-zero marginal inference cost, modest superiority by a metered provider is not sufficient to replace a scientifically adequate Qwen. A metered provider must demonstrate a material end-to-end MTS advantage after cost is included. Workload-specific routing is permitted when justified by evidence. Scientific standards must not be lowered if no routine provider is sufficiently reliable.

### 8.4 Batching and Escalation

AI scientific autonomy does not require one model call per scientific micro-decision. Where scientifically appropriate, RD should formulate and evaluate coherent batches so context and reasoning are reused efficiently.

Escalation should preserve the scientific record and provide the stronger provider enough context to make an informed decision without needless reconstruction.

### 8.5 Independent Evidentiary Access and Adversarial Review

No lower-capability or lower-cost AI provider may become an information bottleneck for a stronger provider's scientific review. Qwen, Terra, Jev, or any future intermediate provider may summarize, classify, prioritize, or interpret evidence for efficiency, but its output must not define the complete evidentiary universe available to Sol or another stronger provider when independent review is scientifically warranted.

When work escalates for scientific review, the stronger provider must have access to sufficient underlying governed evidence, Analysis outputs, RP state and lineage, relevant Nexus context, available source/provenance context, prior AI reasoning, contract failures, and unresolved questions to independently evaluate the scientific issue. Lower-tier summaries, classifications, confidence judgments, and recommendations are supplemental context; they may not substitute for underlying material evidence when doing so could constrain independent reasoning.

**Lossy compression must not become scientific censorship.** Cost and context optimization may remove objectively redundant representation, but must not remove scientifically material observations, negative results, contradictory evidence, alternative-condition results, or lineage merely because a cheaper provider judged them irrelevant or unpromising.

Jev or another bounded-judgment system may advise that evidence is irrelevant, weak, contradictory, redundant, or low-confidence, but that judgment may not by itself permanently discard the evidence or prevent it from reaching a stronger scientific reviewer when escalation or audit requires it. Likewise, a routine generative provider may recommend closure or abandonment, but must not irreversibly suppress the governed evidence underlying that recommendation.

For scientifically consequential findings, closures, contradictions, or potentially novel relationships, MTS may use **blind or partially blind independent review**. In such review, Sol or another stronger provider may first receive the underlying evidence and Analysis outputs without the lower-tier provider's scientific conclusion, form an independent interpretation and proposed next action, and only then receive the prior provider's interpretation for adversarial comparison and reconciliation. This mechanism is intended to reduce anchoring, confirmation bias, and multi-model echo-chamber effects.

Sol's escalation role therefore includes **independent scientific challenge**, not merely error repair or approval of lower-tier conclusions. Sol may challenge Qwen/Terra interpretations, Jev judgments, Analysis choices requested by prior AI reasoning, Nexus assumptions, and prior Sol conclusions when the governed evidence warrants reconsideration.

Batching and cost optimization should reduce unnecessary model calls and redundant representation, not reduce the scientific information available to the reasoning authority that needs it. Fewer, richer Sol reviews are preferable to many micro-calls, but richer review must preserve the material evidence needed for genuine adversarial reasoning.

The AI Research Director may revise its own requests when objective execution feedback identifies a contract defect.

## 9. Analysis Engine

Analysis executes scientific and mathematical operations requested by the AI Research Director. It may expose governed methods and objective execution contracts but must not become a second scientific authority.

Analysis should support scientifically coherent batching where requested meaning is preserved and unnecessary AI round trips are reduced. It may calculate exact statistics, transformations, comparisons, matrices, and other reproducible outputs in bulk when requested by RD; this does not transfer scientific authority to Analysis.

Analysis returns governed results with sufficient metadata and lineage for RD interpretation and durable promotion when appropriate.

## 10. Research Nexus

The Research Nexus is durable research memory, not a reproducible-data warehouse. Its primary contents are subject metadata; significant RD-promoted findings; durable hypotheses or research-state records; provenance and lineage; relationships among findings, subjects, hypotheses, and prior research; unresolved scientific issues; and compact context necessary for future RD reasoning.

Nexus shall not be the durable repository for raw or otherwise reproducible market datasets. Nexus should preserve what MTS learned, not warehouse the data from which it learned it.

Known external strategies or theories should be distinguishable from findings empirically established by MTS so prior knowledge is not silently promoted into validated MTS knowledge without evidence.

Not every Analysis result belongs in Nexus. RD determines scientific significance. Deterministic code may validate promoted-record schema, lineage, integrity, and provenance but may not decide scientific importance.

## 11. B-Series Status

The prior RD-B series is abandoned as an architecture for v4. B-series code may be mined only as a parts source and enters v4 only if independently justified under the v4 authority model.

Deterministic scientific-cognition mechanisms such as deterministic hypothesis generation, candidate-question generation, scientific-value scoring, question selection, scientific critics, convergence evaluators, method-suitability ranking, scientific specification resolution, and deterministic scientific continuation must not be transplanted as scientific authority.

Reusable mechanical code may be retained where appropriate, including hashing, canonicalization, persistence mechanics, objective validation, lineage, orchestration, cache management, provider infrastructure, and other non-scientific capabilities.

## 12. Reconstruction Rule

MTS v4 is built by positive admission, not subtraction. Do not copy modern v2 wholesale and remove undesirable behavior afterward.

For each candidate component from v2 or the B-series, ask:

> Would we design this component today under the rule that AI owns scientific reasoning?

If yes, it may be kept or adapted. If it exists primarily to imitate scientific intelligence deterministically, leave it behind. The old v2 tree remains useful as a forensic reference and comparison control.

## 13. Scientific Exploration and Validation

During exploratory learning, look-ahead may be used where explicitly appropriate to discover candidate zones, relationships, or hypotheses.

Exploration includes both evaluation/refinement of known predictive strategies or theories and search for previously unidentified predictive relationships. MTS need not consume resources recreating established knowledge merely to claim internal discovery. Where credible prior predictive knowledge exists, RD may begin from that knowledge and investigate whether it survives, how it should be conditioned, where it fails, how it interacts with other evidence, and whether it is practically exploitable.

Neither known nor novel predictive structure receives an inherent scientific preference because of its origin. RD retains authority to pursue established strategies, anomalies, unexplained residuals, cross-evidence interactions, contradictory observations, and novel hypotheses according to scientific and practical merit.
