# Qwen–SOL Supervisory Research Blueprint

Status: APPROVED DESIGN — DEFERRED IMPLEMENTATION

Implementation gate: DO NOT IMPLEMENT, WIRE, ENABLE, OR USE THIS ARCHITECTURE UNTIL THE FIRST 11 SOL-RESEARCHED TICKERS ARE COMPLETE.

This document records an approved future architecture. It does not supersede `ChatGPT.md`, does not change current Research Director authority, and does not authorize implementation before the gate above is satisfied.

## Purpose

Reduce recurring premium-model research cost while preserving SOL-level scientific oversight.

After the first 11 tickers have been researched to completion by SOL, Qwen may become the working Research Director for subsequent subjects using the completed SOL corpus as scientific precedent. Qwen researches every ticker. SOL remains the supervisory scientific authority and periodically audits the complete work of a five-ticker Qwen cohort.

The intended unit is therefore:

1. Qwen researches ticker 1 completely.
2. Qwen researches ticker 2 completely.
3. Qwen researches ticker 3 completely.
4. Qwen researches ticker 4 completely.
5. Qwen researches ticker 5 completely.
6. SOL audits the complete scientific record for all five tickers together and may accept, revise, reject, reopen, or extend any part of the work.

There are no four unaudited tickers. SOL audits all five Qwen subjects in each supervisory cycle.

## Authority Boundary

Existing MTS governance remains controlling.

Deterministic code continues to enforce objective execution and governance constraints only. It does not choose scientifically valuable questions, hypotheses, methods, thresholds, interpretations, or findings.

During Qwen execution, Qwen exercises delegated working Research Director judgment. That delegation is provisional: Qwen-authored scientific conclusions are not treated as equivalent to SOL-reviewed conclusions until the applicable SOL supervisory audit has occurred.

SOL's supervisory role is not limited to reviewing final findings. SOL audits the research program itself: what Qwen asked, what it chose to test, how it represented the question, what Analysis actually returned, what Qwen inferred, what it rejected or deferred, whether it closed too early, and what it chose to investigate next.

SOL may require additional Analysis, revised representations, reopened questions, changed interpretations, withdrawal of findings, or new cross-subject work. SOL does not need to recompute deterministic Analysis that is already valid and reproducible.

## First-11 Reference Corpus

The first 11 completed SOL subjects form the initial reference corpus for Qwen.

The corpus should preserve scientific behavior, not merely final conclusions. At minimum it should expose governed representations of:

- research questions and hypotheses;
- Research Packages and their lineage;
- Analysis Specifications selected by SOL;
- deterministic Analysis results used by SOL;
- SOL interpretations of those results;
- continuation decisions and reasons for pursuing, modifying, combining, deferring, rejecting, or closing branches;
- negative results and abandoned directions;
- representation corrections and methodological repairs;
- cross-subject generalizations and uncertainty;
- final findings with provenance and evidence status.

The corpus is precedent/context, not a deterministic template. Qwen remains free to discover subject-specific relationships that did not occur in the first 11 subjects.

## Required Qwen Trace

Every Qwen subject must preserve enough durable scientific trace for SOL to audit without independently restarting the subject.

Required trace includes:

- questions/hypotheses considered;
- accepted Research Packages;
- requested Analysis Specifications and parameters;
- Analysis result identifiers and reproducible lineage;
- Qwen interpretation for each material result;
- continuation/closure decisions and rationale;
- rejected, deferred, and unresolved branches;
- candidate findings and their evidentiary basis;
- cross-subject context used;
- known data or representation limitations.

A final-summary-only handoff is explicitly insufficient.

## Five-Ticker SOL Supervisory Audit

After Qwen completes each cohort of five subjects, SOL receives the complete governed scientific trace for all five plus relevant Nexus cross-subject memory.

SOL should review the five both individually and comparatively. The audit should be able to identify:

- sound work requiring no change;
- unsupported or overstated conclusions;
- premature closure;
- recurring Qwen blind spots;
- missed interactions or representations;
- inappropriate generalization across subjects;
- underused or misused evidence sources;
- branches that require additional Analysis;
- candidate relationships that become more important only when viewed across the five-subject cohort.

SOL may issue additions/revisions for any or all five. Those follow-ups should reuse existing valid Analysis and durable lineage whenever possible rather than repeating work merely because SOL is now the reviewer.

## Learning Loop

SOL audit corrections should become governed precedent available to later Qwen cohorts. The system should distinguish:

- original Qwen judgment;
- SOL audit judgment;
- any resulting additional Analysis;
- final post-audit scientific state.

This creates an observable Qwen→SOL correction history that can later be measured and, if separately authorized, converted into supervised training/fine-tuning material.

No fine-tuning is authorized by this blueprint.

## Promotion / Safety Criteria

The five-subject supervisory cadence is a target architecture, not an assumption that Qwen is already adequate.

Before relying on the cadence operationally, compare Qwen work against SOL audit outcomes. Useful measurements include:

- proportion of Qwen conclusions accepted unchanged;
- branches reopened by SOL;
- material missed questions/interactions identified by SOL;
- findings withdrawn or materially revised;
- additional Analysis required by SOL;
- premature closures;
- repeated categories of Qwen error;
- premium-model audit cost per five-subject cohort;
- total effective AI cost per ticker.

If Qwen's scientific trace is inadequate for efficient audit, SOL should not be forced to redo entire subjects merely to satisfy a fixed cadence. The deficiency should be treated as evidence that the delegated workflow is not yet ready.

## Scientific and Cost Objective

The objective is not to make Qwen imitate SOL stylistically. It is to make lower-cost working research auditable against a high-quality SOL-established scientific precedent while preserving autonomous discovery.

Success means Qwen can perform the bulk of iterative subject research, Analysis remains deterministic and reproducible, and SOL can supervise five complete Qwen subjects primarily by reviewing their preserved scientific lineage and selectively directing corrections rather than independently repeating each campaign.

## Deferred Implementation Rule

Until the first 11 SOL subjects are complete:

- do not modify production runners to select Qwen for this workflow;
- do not alter current SOL Research Director authority;
- do not add automatic five-ticker supervisory execution;
- do not promote Qwen findings under this design;
- do not fine-tune Qwen from the SOL corpus;
- do not change current production research behavior on the basis of this blueprint.

Design/documentation work may continue. Production implementation requires a separate explicit user authorization after the first 11 SOL subjects are complete.
