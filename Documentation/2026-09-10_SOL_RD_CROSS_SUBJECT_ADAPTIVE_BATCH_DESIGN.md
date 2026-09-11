# Sol RD Cross-Subject Adaptive Batch Design

Status: Approved design direction, 2026-09-10

## Purpose

Extend MTS v4 so an AI Research Director using Sol can accumulate durable scientific experience across equity subjects, choose scientifically useful unseen subjects within human-governed eligibility constraints, and operate in bounded autonomous batches of three subjects followed by mandatory human review.

This design does not change the MTS mission, scientific-authority model, raw-data retention boundary, or human governance authority. Deterministic code may expose memory, enforce objective eligibility/representation constraints, and report what occurred. It may not choose scientific questions, hypotheses, subject relevance, generalization, interpretation, or scientific adequacy.

## Scientific Memory Scopes

### Subject Memory

Durable subject-specific scientific state: research packages, findings, predictive hypotheses, validation state, unresolved issues, negative results, resource limitations, and closure assessments. Existing subject-scoped Nexus and RP behavior remains intact.

### Cross-Subject Scientific Memory

Compact durable records exposing scientifically relevant prior-subject experience to later subjects without copying raw datasets or reusable Analysis payloads into Nexus. Cross-subject memory may contain:

- promoted findings;
- tentative predictive hypotheses and validation status;
- meaningful negative results;
- RP closure assessments;
- unresolved contradictions;
- resource/data limitations that affected scientific interpretation;
- methodological lessons whose scientific meaning was authored by RD;
- source subject, RP, finding/result/hypothesis provenance.

Prior-subject records are context, not a mandatory research agenda. RD may test, challenge, reformulate, condition, defer, or ignore them.

### Research Frontier

RD-authored durable working scientific memory across subjects. The Frontier records what RD currently believes is scientifically worth investigating next, including possible generalizations, contradictions requiring discrimination, unresolved cross-subject questions, deprioritized relationships, and missing capabilities/resources. Deterministic code persists and exposes the Frontier but does not author or rank its scientific content.

## Adaptive Subject Selection

Subjects are selected sequentially, not as a preselected twenty-name list. RD chooses each next unseen ticker after considering accumulated cross-subject memory and the current Research Frontier.

Human governance defines only the eligibility envelope. Initial approved envelope:

- equity subject;
- previously unseen within the current adaptive research program;
- data sources required for a scientifically useful run are objectively available;
- no duplicate subject;
- subject selection should collectively provide scientifically useful variation for testing whether accumulated relationships generalize, reverse, weaken, or depend on subject characteristics;
- avoid repeatedly selecting subjects whose similarity contributes little discriminating information.

RD must author a durable subject-selection rationale explaining why the selected subject is scientifically useful given current knowledge. Deterministic code validates only objective eligibility and uniqueness. It must not select or rank subjects scientifically.

## Three-Subject Autonomous Batch Boundary

Maximum autonomous batch size is three newly selected unseen subjects. After the third subject, the controller must stop regardless of RD preference and require review before another batch begins. This is a governance/resource checkpoint, not a scientific conclusion.

A batch consists of:

1. RD selects eligible unseen subject 1, researches it, and updates durable scientific memory.
2. RD selects subject 2 using knowledge from subject 1 plus prior memory, researches it, and updates memory.
3. RD selects subject 3 using accumulated knowledge from subjects 1-2 plus prior memory, researches it, and updates memory.
4. Batch stops.
5. Deterministic Batch Ledger is produced.
6. Sol authors a Batch Scientific Synthesis.
7. Human/ChatGPT audit occurs before continuation authorization.

## Batch Ledger

The deterministic ledger reports objective facts only, including per subject:

- selected ticker and selection rationale identifier;
- decisions;
- Analyses executed;
- research packages;
- hypotheses created;
- validation trials/outcomes;
- findings promoted;
- contract/representation repairs;
- source/data failures;
- termination/closure representation;
- API calls/tokens/cost when available;
- elapsed runtime when available.

It must not interpret scientific meaning.

## Batch Scientific Synthesis

After each three-subject batch, Sol receives the Batch Ledger plus compact durable scientific memory and authors a synthesis addressing:

- relationships replicated across subjects;
- relationships contradicted;
- relationships not tested and why;
- possible conditional or regime-dependent effects;
- new cross-subject candidate generalizations;
- subject-specific anomalies;
- changes to the Research Frontier;
- whether the selected subjects provided useful scientific discrimination;
- recommended next scientific subject-selection direction.

### Mandatory Zero-Finding Diagnosis

If a subject or batch has no promoted findings, the synthesis must explain why. It must distinguish among, at minimum:

- no relationship survived exploration;
- candidate effect too weak or inconsistent;
- conflicting evidence prevented promotion;
- insufficient sample/history;
- source fields unusable or data quality inadequate;
- required Analysis capability unavailable;
- a tentative hypothesis existed but was correctly not promoted as a Finding;
- blind validation requires future observations;
- scientific progression failed or stalled;
- representation/system failure prevented completion.

Zero findings are not mechanically classified as failure or success.

## Cross-Subject Generalization

Generalization is itself a falsifiable scientific proposition owned by RD. Repetition across a few subjects must not mechanically become a verified generalized finding.

The architecture should support distinct generalization state conceptually equivalent to:

- SUBJECT_TENTATIVE;
- CROSS_SUBJECT_CANDIDATE;
- CROSS_SUBJECT_VALIDATING;
- CROSS_SUBJECT_VERIFIED;
- CROSS_SUBJECT_NOT_VERIFIED.

Exact schema names may differ, but deterministic code must not infer or assign scientific generalization status except where human governance defines an objective validation calculation from RD-authored frozen criteria.

A later cross-subject interpretation must never overwrite earlier subject findings. It references supporting and contradictory provenance and creates new durable scientific state.

## Negative Knowledge

Scientifically meaningful negative results may enter cross-subject memory when RD judges them useful. Repeated weak or failed relationships may be marked as deprioritized by RD, but deterministic code must not suppress future investigation. RD may revisit a deprioritized avenue when new subject/regime/evidence conditions justify it.

## Exploration and Validation

Prior-subject hypotheses may motivate exploration in new subjects but do not force replication. New subjects may be used for replication/discrimination, independent exploration, or both.

Historical look-ahead remains allowed during EXPLORATION. Once RD freezes a predictive proposition for blind VALIDATION, future information remains prohibited from the prediction stage under existing MTS governance.

## Objective Representation Guardrails

Two guardrails identified in the AAPL Terra/Sol audit should be implemented without transferring scientific authority to deterministic code:

1. A decision with `continue_research=false` must include a nonblank `close_reason`. The code requires explicit representation of RD's reason; it does not author the reason.
2. Analysis contracts should expose incompatible row/key identity spaces where they are mechanically knowable, so an invalid join cannot silently treat row position, source identity, and composed anchor identity as equivalent. The code reports the exact identity defect; RD chooses the scientific repair.

## Intended Initial Program

Do not commit in advance to a fixed twenty-subject cohort. Run adaptive batches of three with review checkpoints at 3, 6, 9, 12, and 15 subjects. Continue toward approximately twenty only if accumulated evidence and review justify doing so.

The purpose of the initial program is not maximizing Finding count. It is testing whether Sol + MTS can autonomously accumulate prior-subject knowledge, use it intelligently, discover contradictions, form increasingly general hypotheses, preserve falsifiability, and recognize when evidence does not justify a conclusion.
