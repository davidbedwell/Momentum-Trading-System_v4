# Batched AI Research Director Execution Architecture

## Purpose

This document records the approved MTS v4 execution redesign that separates AI scientific authority from deterministic execution plumbing and allows the AI Research Director to operate at the research-program level rather than the individual executor-call level.

The governing authority remains `ChatGPT.md`. Nothing in this design permits deterministic code to invent, rank, prefer, or substitute scientific questions, hypotheses, methods, variables, horizons, thresholds, transformations, or interpretations.

## Approved Operating Model

The AI Research Director may author multiple Research Packages in one scientific decision cycle. Each Research Package may contain multiple Analysis Specifications. Analysis Specifications may be independent or may form an explicitly AI-authored dependency graph.

The runtime executes the complete authorized batch before returning to the AI Research Director except when a genuine scientific ambiguity prevents a branch from being compiled or executed safely. Mechanical failures in one branch do not invalidate independent branches.

The high-level loop is:

AI Research Director
→ one or more AI-authored Research Packages
→ one or more AI-authored Analysis Specifications per RP
→ deterministic scientific-specification compiler
→ exact low-level AnalysisRequests
→ Analysis Engine execution
→ consolidated Batch Research Result
→ AI Research Director interpretation
→ findings, closures, revised hypotheses, follow-up Research Packages, or another batch
→ repeat as scientifically necessary.

## Unbounded Scientific Breadth and Batch Symmetry

At each Research Director decision point, Sol may create or continue as many Research Packages as it judges scientifically relevant to the research objective. It should include all scientifically justified lines of inquiry that can be specified from the evidence currently available. Deterministic code must not impose a scientific limit, ranking, quota, preferred number, or favored ordering of Research Packages.

All Research Packages and Analysis Specifications authorized by one Sol decision are delivered to Analysis as one batch. The batch boundary is scientific: it contains all presently justified work that does not require an unknown intermediate scientific result before its justification can be established.

Similarly, Sol shall receive all Analysis results for all Research Packages sent in that batch together in one consolidated return after all mechanically executable work in the batch has completed. Deterministic code must not selectively return, rank, suppress, prioritize, or withhold completed Analysis results based on scientific merit.

A genuine scientific dependency may create a decision boundary. Sol should not pre-author contingent follow-up science whose justification depends on an unknown result. Once the consolidated batch is returned, Sol may interpret the results across all RPs, close or continue any RP, create new RPs, promote findings, or authorize another complete batch.

There is no architectural target for the number of Research Packages or Analysis Specifications in a batch. Zero, one, or many may be scientifically appropriate. The number is a Sol scientific judgment constrained only by available evidence, executable capability, genuine scientific dependencies, and objective execution safety—not by a deterministic quota or preferred batch size.

## Scientific Authority

The AI Research Director owns:

- scientific questions;
- hypotheses and hypothesis revisions;
- predictors, outcomes, conditioning variables, regimes, interactions, and representations;
- scientific transformations such as ratios, differences, normalization, interactions, and event definitions;
- scientific method selection;
- scientifically meaningful parameters, including horizons, windows, thresholds, directions, and trial design;
- which evidence or prior derived scientific object should be used;
- whether two objects should be aligned or compared scientifically;
- interpretation, significance, uncertainty, contradiction, novelty, and relevance;
- how many Research Packages are scientifically relevant at a decision point;
- how many Analysis Specifications are scientifically justified within each RP;
- whether a Research Package is complete;
- whether the subject warrants additional Research Packages;
- where a genuine scientific decision boundary exists;
- whether to promote findings or predictive hypotheses;
- whether to continue, pivot, defer, or close research.

## Deterministic Compiler Authority

The compiler owns mechanics that have no scientific alternative once the AI has supplied a complete scientific instruction. Examples include:

- runtime request IDs;
- generated result IDs;
- exact nested output paths;
- internal input aliases;
- ensuring aliases are unique;
- mapping logical input roles to exact executor bindings;
- resolving an AI-selected prior Analysis Specification to its runtime result;
- resolving an explicitly named reusable dataset to its advertised output path;
- resolving an unnamed reusable dataset only when exactly one reusable dataset exists;
- topologically ordering an AI-authored dependency graph;
- safe internal representation of symbolic dependencies;
- objective type/shape/identity/lineage checks;
- semantics-preserving missing-value exclusion when the selected Analysis method already defines that behavior;
- retrying or repairing purely mechanical representation defects when exactly one semantics-preserving repair exists.

The compiler may not choose between multiple scientifically meaningful alternatives. If more than one scientific interpretation or execution meaning exists, the affected branch must be returned to the AI Research Director as an ambiguity.

The controlling implementation rule is:

> One semantics-preserving mechanical resolution → deterministic compiler may resolve it.
>
> More than one scientifically meaningful resolution → AI Research Director decides.

## Symbolic Analysis Inputs

The AI Research Director should not be required to know generated `result_id` values, nested `output_path` arrays, or executor alias names.

Instead, each Analysis Specification uses stable logical identifiers and semantic input roles. A prior Analysis Specification may be referenced by its logical `analysis_id`. When a prior result exposes exactly one reusable dataset, the compiler may resolve it automatically. When it exposes multiple reusable datasets, the AI must identify the desired reusable dataset by its advertised dataset name. The compiler then resolves the exact runtime path.

Evidence references remain explicit because choosing evidence is scientific. The compiler may map the selected evidence ID to an internal executor alias without asking the AI to reproduce that alias elsewhere.

## Batch Research Packages

A batch may contain zero, one, or many RPs according to Sol's scientific judgment. Each RP contains:

- `rp_id`;
- optional `parent_rp_id`;
- scientific objective;
- one or more Analysis Specifications;
- an optional AI-authored decision boundary explaining what should be returned before additional contingent science is attempted.

An RP is a scientific unit, not an execution unit. Several RPs may execute in the same batch. Deterministic code may validate representation and execution safety but may not impose a scientific maximum RP count, preferred RP count, ranking, quota, or preferred ordering.

## Batch Completion and Return

The runtime executes all currently authorized and mechanically executable Analysis Specifications in the batch. Independent branches continue even if another branch fails.

The consolidated return to the AI Research Director includes, for every Analysis Specification in every RP in the batch:

- logical `analysis_id`;
- `rp_id`;
- exact compiled request identity for audit;
- execution status;
- Analysis result outputs or objective compiler/execution defect;
- lineage and provenance;
- future-information metadata;
- any compiler-generated internal binding map needed for audit but not for scientific reasoning.

The AI Research Director receives one consolidated batch only after all executable work in the authorized batch has completed. The deterministic layer may not scientifically rank, selectively return, suppress, or prioritize completed results. Branch-local objective failures are included alongside successful results so Sol can interpret the batch as a whole.

## Follow-up Cycle

After reviewing the complete batch, the AI Research Director may:

- promote findings;
- create or update tentative predictive hypotheses under existing governance;
- close one or more RPs;
- continue any number of existing RPs;
- create any number of new child or sibling RPs it judges scientifically relevant;
- issue multiple follow-up Analysis Specifications across those RPs as another single batch;
- re-test an existing scientific proposition using a new AI-chosen method or parameterization;
- defer a contingent branch;
- close the subject when further work is scientifically low-value, redundant, unsupported, or better deferred.

No deterministic component may infer follow-up science merely because a statistical result crosses a threshold or because a predefined decision tree says to continue.

## Failure Semantics

A mechanical failure should not automatically trigger another premium-model call.

If the compiler can correct a representation problem in exactly one semantics-preserving way, it should do so and record the repair.

If an Analysis method already specifies pairwise exclusion of missing/non-numeric values, that exclusion is method execution behavior and does not require AI repair.

If a branch cannot execute because several scientifically meaningful repairs are possible, the branch returns `AMBIGUOUS_SCIENTIFIC_REPAIR_REQUIRED` with the exact defect. Other independent batch branches continue.

## Cost and Intelligence Boundary

Premium AI reasoning should be spent on science, not private runtime bookkeeping. The AI should not be repeatedly called merely to copy generated IDs, reproduce output paths, invent safe aliases, or repair reserved internal names.

This architecture is intended to reduce the near one-AI-call-per-Analysis pattern while improving the AI Research Director's ability to reason across multiple hypotheses and Research Packages simultaneously.

## Compatibility

The existing single-request ResearchDecision path remains a compatibility path until the batched path passes tests and production proof. The batched implementation should compile down to the same governed Analysis Engine rather than duplicating scientific methods.
