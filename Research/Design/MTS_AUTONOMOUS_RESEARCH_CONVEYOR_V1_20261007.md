# MTS Autonomous Research Conveyor — Design v1
Date: 2026-10-07
Status: DESIGN FREEZE CANDIDATE
Applies to: layered contextual evolution rebuild

## Objective
Allow MTS research to proceed for long unattended periods without requiring chat prompts and without requiring an external monitor to decide what to do next.

The controller is deterministic orchestration, not an AI scientist. It may execute only preregistered work, evaluate explicit gates, persist evidence, and advance on PASS. It may never reinterpret a failed experiment, change scientific parameters, open protected data, or invent a repair.

## Controller state machine
Each stage/run has exactly one state:
PLANNED -> PREFLIGHT -> RUNNING -> EVALUATING -> PASS | FAIL | AMBIGUOUS | ERROR
PASS -> FREEZING -> DURABILITY_VERIFY -> NEXT_STAGE
FAIL -> DURABILITY_VERIFY -> STOPPED_SCIENTIFIC
AMBIGUOUS -> DURABILITY_VERIFY -> STOPPED_REVIEW
ERROR -> RECOVERY_ATTEMPT -> RUNNING or DURABILITY_VERIFY -> STOPPED_ENGINEERING

Only PASS may advance automatically.

A stage is not FROZEN merely because its process exited successfully. FROZEN requires:
1. required artifacts exist;
2. required tests pass;
3. gate evaluator emits PASS with machine-readable reasons;
4. artifact manifest is complete;
5. Git remote commit is verified;
6. non-Git backup manifest/checksums are verified where applicable.

## Parallel start
Stage 0 Archaeology and Stage 1 Context Map are independent and MAY run concurrently.
Stage 2 is blocked until BOTH Stage 0 and Stage 1 are FROZEN.

No other scientific stages run concurrently with a downstream dependent stage. Independent validation folds/replicates inside a stage may run in parallel.

## Standard stage directory
Research/Runs/layered/<run_id>/
  run_manifest.json
  preregistration.json
  status.json
  heartbeat.json
  stdout.log
  stderr.log
  metrics.json
  gate.json
  artifact_manifest.json
  provenance.json
  failure.json (only if applicable)
  handoff.md

## Required run manifest
Must include:
- run_id and stage;
- code commit SHA and dirty-tree status;
- data manifest/hash;
- exact protected-bank permissions;
- seeds;
- scientific parameters;
- compute-only parameters;
- expected outputs;
- gate version;
- parent frozen artifact IDs;
- start time and host identity.

Scientific and compute parameters are separate namespaces. Worker count, CPU affinity and batching may change without changing science only when tests prove equivalence.

## Preflight — every run
Controller refuses to start if any fails:
- code commit is known;
- working tree modifications are captured in provenance;
- required parent stages are frozen;
- requested dataset is allowed by governance;
- DEV50 and BLIND17 are inaccessible unless explicitly authorized;
- PIT/leakage tests pass where applicable;
- data/schema hashes match preregistration;
- disk space and memory floor are adequate;
- output directory is unique;
- restart checkpoint semantics are defined;
- stage objective is allowed by architecture contract;
- no forbidden downstream metric is being optimized.

## Stage 0 — Archaeology automation
Inputs: mounted snapshot/filesystem, Git history, preserved bundles/backups.
Automated work:
1. inventory filesystem without deleting/modifying evidence;
2. record repo(s), refs, dirty/untracked files, timestamps, sizes and hashes;
3. search code/reports/logs for GA/Genome/chromosome/family/mutation/crossover/CAGR/MDD/frontier/finalist terms;
4. extract candidate evidence into ledger;
5. provenance-link every claim;
6. identify unique/non-Git artifacts;
7. back up unique evidence before development changes;
8. produce recovered gene registry and unresolved ledger.

Automatic PASS only if a predefined minimum evidence contract is met. Missing exact GA0 elements does NOT authorize fabrication. If exact recovery is incomplete, gate=AMBIGUOUS and stop for explicit decision between evidence-supported reconstruction and new vocabulary.

## Stage 1 — Context-map automation
Inputs: authorized development market history only.
Pipeline:
1. build causal SPY Galaxy descriptors;
2. build causal sector Solar-System descriptors;
3. retain continuous values beneath five-state labels;
4. build stock-vs-sector, stock-vs-SPY and sector-vs-SPY relative descriptors;
5. deterministic replay;
6. PIT/leakage audit;
7. coverage and missingness audit;
8. state stability/transition report;
9. simple-control comparison.

No future return may choose today's context state. No trade P&L/CAGR/MDD objective.

PASS only if causal/replay/coverage gates pass. Exact state boundaries must be preregistered or calibrated only on authorized development data using a separately declared calibration procedure.

## Stage 2 — Directional opportunity automation
Blocked until Stage 0 + Stage 1 frozen.
Before real GA:
1. single-gene baseline sweep;
2. planted-signal calibration at multiple effect sizes;
3. null calibration to estimate false-discovery behavior and useful search scale;
4. choose initial search budget/complexity only from calibration, not historical G2 budgets.

GA:
- semantic genes only;
- LONG and SHORT opportunities independently evaluated;
- small chromosomes first;
- add/remove/substitute/parameter/context-interaction mutations;
- semantic crossover;
- no portfolio/lifecycle/sizing genes;
- no CAGR/MDD fitness;
- multi-horizon forward path is measurement, not holding-period gene.

Promotion:
- discovery effect;
- credible net EV;
- uncertainty;
- raw N + effective N;
- recurrence;
- temporal/stock/domain transport as applicable;
- transfer ratio;
- null comparison;
- marginal complexity contribution.

If no candidate passes, STOP_SCIENTIFIC. Do not increase genome grammar/search budget automatically.

## Stage 3 — Context ablation automation
For each frozen Stage-2 chromosome compare:
A Planet only
B Planet + Galaxy
C Planet + Sector
D Planet + Galaxy + Sector
plus preregistered divergence/interactions.

Context is retained only when transported evidence improves. Failure of context to add value does not invalidate the Planet chromosome.

## Stage 4 — Entry/MAE automation
For frozen opportunities:
- characterize immediate-entry forward paths;
- separate eventual winners/failures without look-ahead in decision rule;
- discover causal enter-now vs wait evidence;
- quantify MAE/MFE, avoided failures, lost winners, delay cost and EV effect;
- compare against immediate-entry control.

No fixed wait rule may be promoted merely because it was included as a control.

## Stage 5 — Thesis-failure automation
Discover evidence separating normal adverse excursion from invalidated thesis.
Compare with simple fixed/ATR stop controls.
Outputs thesis-continue/thesis-failed evidence only.
Opposite-direction entry remains independent.

## Stage 6 — Lifecycle automation
Initially run separate substudies for ADD, HOLD/CONTINUE, REDUCE and EXIT.
Only after those transport may a combined action policy be evaluated.
Every decision uses information available at that cutoff and remaining prospective EV.
Duration is observed, never targeted.

## Stage 7 — Capital competition automation
At each cutoff compare incumbent, qualified challengers and SAFE after costs.
Research replacement margin and turnover economics on authorized development data.
No automatic reversal: closing LONG and opening SHORT are independent qualifications.

## Stage 8 — Position-sizing automation
Study sizing from credible EV, uncertainty, tail/MAE, correlation/concentration and contextual support/opposition.
Galaxy/Sector may alter size; they may not become an implicit hard trade gate without explicit scientific evidence and governance change.

## Stage 9 — Portfolio + catastrophe automation
Integrate frozen upstream policies.
Add correlation, sector concentration, liquidity and duplicated-risk controls.
Integrate separately frozen A/B/C catastrophe defense and R-1 recovery.
Catastrophe layer may override for survival.
Do not retune upstream chromosomes against portfolio CAGR/MDD.

## Stage 10 — Report-card automation
Compute final outcomes only:
CAGR, MDD, wealth, CVaR, worst periods, turnover/cost, utilization, recovery, crash behavior, concentration, era stability and transport.
Poor results generate diagnostic attribution and STOP/REPORT. They do not automatically mutate upstream science.

## Gate semantics
Every gate file contains:
{
  "decision": "PASS|FAIL|AMBIGUOUS|ERROR",
  "gate_version": "...",
  "criteria": [...],
  "observed": {...},
  "failed_criteria": [...],
  "next_action": "...",
  "scientific_parameters_changed": false
}

No free-text parser may decide advancement.

## Automatic failure policy
Engineering/transient failures:
- checkpoint safely;
- retry same exact scientific run up to a preregistered small retry count;
- no seed/parameter changes during retry;
- repeated failure -> ERROR and stop.

Scientific FAIL:
- never retry with new parameters automatically;
- preserve results;
- close out durability;
- stop.

AMBIGUOUS:
- preserve;
- stop for human decision.

## Checkpoint/restart
- atomic checkpoint writes (temporary + fsync/rename where supported);
- checkpoint contains RNG state, generation/iteration, populations/archives if applicable, parent hashes and scientific config hash;
- resume refuses config/hash mismatch;
- restarting from checkpoint must be regression-tested against uninterrupted deterministic miniature run;
- checkpoint frequency is compute engineering, not scientific adaptation.

## Heartbeat without monitoring
Every active worker updates heartbeat.json with:
timestamp, stage, PID, generation/task, completed/total, last_checkpoint, scientific_config_hash.
The controller itself consumes worker exit/status. ChatGPT does not need to poll it.
A local watchdog may restart only crashed processes under exact checkpoint/config identity; it may not make scientific decisions.

## Compute/cost controls
- use all appropriate local cores through tested deterministic parallelism;
- run calibration/minis before expensive search;
- controller records wall time, CPU time and estimated provider cost when available;
- optional hard wall-clock/cost ceiling causes safe checkpoint + STOPPED_ENGINEERING, never scientific parameter reduction;
- no paid GPU/server is required merely because prior generations used one;
- no automatic provisioning of additional paid machines.

## Durability protocol
At stage freeze, scientific stop, engineering stop, and session close:
1. generate artifact manifest;
2. hash critical/non-reconstructable files;
3. commit code/spec/reports appropriate for Git;
4. push to remote;
5. independently fetch/verify remote branch SHA;
6. upload non-Git artifacts to external backup;
7. independently list backup destination;
8. verify expected object set/count/size and critical checksums;
9. write durability_receipt.json containing evidence;
10. write handoff.md with exact durable boundary.

A message saying "backup complete" is NOT evidence.

## Destructive-action interlock
DELETE/DESTROY/OVERWRITE of server, volume, snapshot, unique checkpoint or working directory is prohibited unless a fresh destruction authorization record exists.

Authorization requires:
- remote Git SHA independently verified;
- external backup manifest independently verified;
- critical checksum match;
- list of reconstructable exceptions;
- explicit target identity;
- explicit human authorization AFTER verification.

The controller cannot self-authorize destruction.

## Session-close rule
A session is not COMPLETE until durability verification succeeds.
If verification fails, status is DURABILITY_FAILED and the system preserves the source machine/data.

## Handoff
Every stop/freeze produces handoff.md:
- what was attempted;
- exact commit/config/data;
- what passed/failed;
- artifacts;
- unresolved issues;
- current stage;
- permitted next automatic action;
- prohibited actions;
- Git verification;
- backup verification.

## Automation boundary
The autonomous controller MAY:
- run preregistered experiments;
- parallelize compute equivalently;
- checkpoint/restart identical work;
- calculate gates;
- freeze PASS artifacts;
- advance to the next preregistered stage;
- stop on FAIL/AMBIGUOUS/ERROR;
- produce reports and durability receipts.

It MAY NOT:
- change objectives;
- change protected-data governance;
- tune on DEV50/BLIND17;
- alter thresholds after seeing results;
- enlarge search because results disappointed;
- add analytical families during a run;
- reinterpret a failed gate;
- delete infrastructure/data;
- merge to protected branches;
- provision paid compute;
- use CAGR/MDD to retune upstream layers.

## Build order for the controller
A. state/manifest schemas + architecture-contract integration
B. preflight + protected-data interlock
C. atomic status/checkpoint framework
D. gate engine
E. durability verifier
F. Stage-0 archaeology runner
G. Stage-1 context runner
H. calibration runner
I. Stage-2 GA runner
J. generic stage transition engine
K. Stage 3-10 runners only as their scientific designs become frozen

Stages 3-10 are specified now so the conveyor has a destination, but code for a downstream stage should not be written in a way that prejudges unresolved findings from earlier stages.
