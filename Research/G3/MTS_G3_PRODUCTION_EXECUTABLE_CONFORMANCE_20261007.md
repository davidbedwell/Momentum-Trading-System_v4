# MTS G3 Production Executable Conformance — 2026-10-07

Status: PRE-LAUNCH. This manifest maps launch-critical frozen protocol controls to executable enforcement. Production execution remains blocked unless the SHA-256 execution freeze validates.

| Frozen control | Executable enforcement |
|---|---|
| 8 islands x 256, max 200 | production runner CLI/default architecture guard |
| all active islands one 60-worker queue | flattened `tasks` list across active island IDs + one ProcessPoolExecutor |
| frozen islands zero evaluations | only `active` island IDs enter task queue |
| 55/30/15 variation | `next_population` frozen branching |
| migration every 20, active islands only | generation `%20`; donor and receiver restricted to active IDs; genome only transferred and fully re-evaluated next generation |
| 2-8 modules; no ticker/company/portfolio genes | `Genome` validation and `FORBIDDEN_GENES`; no portfolio objective in runner |
| Pareto reward/downside/duration | `pareto_rank`; contender bounds from deterministic cluster bootstrap |
| generation-10 >90% rank-1 pressure rule | executable rank fraction + uncertainty/novelty ordering |
| conservative overlapping-event clusters | `event_clusters` transitive time overlap across all tickers |
| 2,000 cluster bootstrap | `bootstrap_axes(...,2000)` |
| 10/15 LCB + 20-bps point screen | Real archive requires 10-bps LCB; 15-bps LCB; 20-bps positive mean |
| OAT +/-10% perturbation, >=75% positive median | `perturb_genomes` / `perturb_positive_fraction` |
| 20/60/20 chronological partition + 60-session embargo | `load_data`; exact rows emitted to partition manifest |
| 2-of-3 discovery temporal thirds | `temporal_thirds_positive` |
| final confirmation frozen/no repair | confirmation occurs only after evolution completes; failures separated as confirmation_failed |
| survivorship claim boundary | every contender record carries `DESIGN_PANEL_SURVIVORSHIP_EXPOSED` |
| deterministic QD scaling/projection/CVT on dev20 | `qd_fit`; seed 20261007; 256 centroids; dev-only descriptors |
| <=4 per QD cell / <=1024 | `qd_insert`; 256 x 4 bound |
| behavioral duplicate merge | scaled descriptor distance <=.01 + fired-event Jaccard >=.95; lower uncertainty retained/logged |
| novelty/museum evidence | museum retained independently from promoted QD |
| plateau | only non-overlapping generation 40 boundaries; <0.5% HV improvement + zero new cells; two consecutive freezes island |
| fixed HV normalization | dev20-derived point-axis min/max frozen before discovery |
| per-organism timeout | SIGALRM 120s -> worst axes |
| checkpoint SHA-256 | sidecar hash verified before resume |
| checkpoint retention | every 10th plus rolling last 3 |
| reachability | separate non-outcome 2-island x 20-generation smoke; <15%/256 occupancy fail-stop |
| exact benchmark | dev20; 8x256; perturbation path; CPU utilization reported |
| CPU utilization | controller requires >=80% or STOP_PARALLEL_UTILIZATION_FAILED |
| checkpoint storage | projected retained checkpoint bytes <=500 GiB |
| total compute | benchmark projects Real + one Null; >14 days STOP_COMPUTE_INFEASIBLE |
| Amendment C | exactly one Real and one matched stationary-block-bootstrap Null arm |
| null max-stat | max 10-bps LCB among Null contenders; Real final must strictly exceed |
| formal V3 authority | diagnostic V3 cannot authorize/veto; conforming V3 alone gates production |
| immutable executable | controller verifies every SHA-256 entry in execution-freeze manifest before reachability/benchmark/production |

Scope note: first production run uses the broad predetermined DEV80 design panel only; it does not perform post-hoc narrower scope generation. Therefore scope-bin optimization is not exercised in this run, and no candidate may claim a narrower discovered scope without a new prospectively versioned hypothesis.
