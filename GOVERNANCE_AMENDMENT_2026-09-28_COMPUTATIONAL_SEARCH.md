# MTS v4 Human-Approved Governance Amendment — Computational Search and Multi-Family Discovery

Date: 2026-09-28
Status: HUMAN-APPROVED

This amendment supplements `ChatGPT.md` and the 2026-09-15 Trading-Hypothesis Lifecycle amendment. Where earlier language could be read to prohibit deterministic or evolutionary generation of candidate empirical relationships, this amendment controls.

## 1. Scientific authority remains with the AI Research Director

The approved AI Research Director (RD), including Sol when selected, remains the scientific reasoning authority. The RD may accept, reject, reinterpret, expand, combine, refine, or independently originate hypotheses; direct further searches and analyses; select scientific methods; interpret evidence; and determine scientific significance, validation, and next research direction.

No search algorithm, Analysis component, deterministic filter, fitness function, or ranking mechanism may overrule valid RD scientific judgment.

## 2. Autonomous computational candidate discovery is authorized

Deterministic, stochastic, evolutionary, genetic, optimization, and other computational search methods may autonomously generate, mutate, recombine, rank, eliminate, and retain candidate empirical relationships and executable rule structures within authorized evidence, feature, resource, and temporal boundaries.

These search products are computational candidates. They are not, by themselves:
- scientific findings;
- scientifically validated hypotheses;
- proof of predictive force;
- trading eligibility; or
- substitutes for RD interpretation.

Search may be broad and need not begin from an RD-authored hypothesis. The purpose is to expose empirical structure and candidate relationships that the RD could not efficiently enumerate manually.

## 3. Search–Analysis iteration

A Search Optimizer may iteratively propose candidate specifications to the Analysis Engine, receive deterministic measurements, update its search state, and repeat without an RD call between generations.

Canonical loop:

Search Optimizer -> Analysis -> Search Optimizer -> Analysis -> ... -> governed search report -> RD.

Analysis remains a calculation/execution engine and does not acquire scientific reasoning authority. Search Optimizers may use Analysis outputs as fitness or selection inputs but may not reinterpret Analysis results as scientific conclusions.

## 4. Multi-family discovery

The search framework shall support pluggable strategy/search families rather than one monolithic strategy. Initial and future families may include momentum, breakout, trend, mean reversion, volatility, volume/liquidity, relative/cross-sectional, event/earnings, market structure/regime, and other RD- or human-authorized families.

A common optimizer framework may operate different family-specific genome/search-space definitions. Cross-family search is authorized after constituent features/candidates are available. The architecture must not privilege momentum or any other family as scientifically superior.

The RD remains free to create new families, ignore existing families, or investigate relationships outside every encoded family.

## 5. Optimizer neutrality

MTS shall not equate computational search with a genetic algorithm. The backend shall expose a common governed search contract capable of supporting GA/evolutionary search and alternative optimizers such as random or quasi-random search, grid/local search, Bayesian or other optimization methods where scientifically and computationally appropriate.

Optimizer choice and comparative performance must be measurable. No optimizer receives scientific authority.

## 6. Discovery evidence boundary

Autonomous adaptive search may consume historical outcomes only from evidence authorized for discovery/exploration.

For the frozen 503-member universe partition, adaptive search may use DISCOVERY outcomes and must not consume VERIFICATION_A or VERIFICATION_B outcomes.

Verification outcomes must never be returned as optimizer fitness, mutation guidance, parameter-selection feedback, stopping feedback, family-selection feedback, or any other adaptive search signal.

If reserved outcomes are exposed to adaptive search, affected subjects/evidence lose untouched status and must fail closed for blind-verification use unless separately repaired under approved governance.

## 7. Internal discovery robustness

Because adaptive search can overfit Discovery, the Search/Analysis system should support internal Discovery-only train/evaluation segmentation, walk-forward assessment, temporal stability, cross-security stability, regime stability, parameter-neighborhood stability, path realism, transaction-cost sensitivity, and other RD-authorized robustness measurements.

Internal Discovery robustness is exploratory evidence only. It does not consume or replace untouched scientific verification.

## 8. Search multiplicity and provenance

Every governed search run must preserve sufficient provenance to reconstruct the search burden and candidate lineage, including:
- search-run identity and version;
- optimizer and optimizer version;
- random seed(s);
- family/search-space schema and version;
- features/operators/parameter domains available;
- fitness/objective definition and version;
- population/generation or equivalent budget;
- total proposed and unique candidates;
- Analysis evaluations performed;
- duplicates/cache hits;
- stopping conditions;
- candidate ancestry or equivalent provenance when applicable;
- rejected and surviving candidate counts;
- data/cohort/exposure identities;
- software version;
- cost/compute telemetry when available.

The RD must be able to know whether a result emerged from tens, thousands, or millions of attempted specifications.

## 9. Fitness is search guidance, not scientific truth

Fitness functions may be scalar or multi-objective and may incorporate RD-authorized measurements such as path-executable expectancy, uncertainty, adverse excursion, stability, turnover, costs, complexity, concentration, or opportunity frequency.

A fitness score is not a scientific conclusion. The system must preserve component measurements where practical so an apparently strong aggregate score cannot conceal fragility.

Raw maximum return alone shall not be the default fitness objective.

## 10. Candidate diversity and empirical landscape reporting

The Search layer should not report only the single highest-fitness specification. It should preserve and summarize:
- materially distinct candidate families;
- robust parameter neighborhoods;
- nearby failures;
- sensitivity surfaces;
- duplicate/correlated structures;
- temporal/security/regime concentration;
- Pareto-efficient alternatives when objectives conflict; and
- the search multiplicity that produced them.

The goal is to provide the RD an empirical landscape suitable for scientific reasoning, not a preselected narrative.

## 11. RD iterative authority

After receiving a search report, the RD may:
- reject all candidates;
- accept candidates for further exploratory work;
- request ablation, inversion, negative controls, robustness checks, or alternative outcomes;
- expand or narrow search spaces;
- combine families;
- add new features or contextual evidence;
- originate hypotheses unrelated to optimizer results; or
- freeze a sufficiently specified hypothesis/policy for untouched validation.

The resulting work may re-enter Search <-> Analysis iteration as often as scientifically useful while remaining inside Discovery.

## 12. Freeze and validation boundary

Before untouched validation, the candidate hypothesis and executable policy must be frozen according to the Trading-Hypothesis Lifecycle amendment.

No GA, optimizer, Analysis calculation, RD revision, or human revision may adapt the frozen candidate using the same reserved validation outcomes and then treat those outcomes as untouched evidence.

Material revision creates a new hypothesis identity and requires genuinely untouched evidence.

## 13. Cost and efficiency

Cheap deterministic computation should perform work that does not require expensive AI reasoning. Search and Analysis should cache semantically identical evaluations and parallelize independent deterministic work where safe.

AI calls should be concentrated on scientific reasoning, interpretation, challenge, experimental direction, and decisions that genuinely require RD cognition.

Cost reduction must not lower scientific standards, hide multiplicity, weaken validation, or restrict the RD to optimizer-selected candidates.

## 14. Negative controls and anti-overfitting controls

The architecture should support negative controls, shuffled/permuted outcomes where scientifically appropriate, null search experiments, and optimizer benchmark searches. These controls may estimate how impressive the best apparent result can look when no genuine predictive relationship exists.

Control results must be available to the RD and may not be silently discarded because they weaken an attractive candidate.

## 15. No optimizer bottleneck on RD evidence

The RD may directly request governed Analysis of evidence without passing through Search. Search Optimizers are assistants to scientific reasoning, not an information gate. The RD's access to authorized evidence and Analysis capabilities must not be narrowed to optimizer survivors.

## 16. Relationship to prior deterministic-cognition prohibition

The prior prohibition on deterministic code generating scientific hypotheses remains applicable to deterministic components that purport to replace RD scientific interpretation or authority.

It does not prohibit computational search from generating candidate empirical relationships under this amendment. Candidate generation is authorized; scientific interpretation and authority remain with the RD.
