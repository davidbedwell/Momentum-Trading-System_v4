# Current GA9 bounded recovery: implemented and exercised

The current `ga9-research-supervisor.service` recovered its existing real-data
zero-fill result automatically on 2026-10-29. Original experiment artifacts,
reservations and research state were preserved. No GA8 files were edited by this
repair (GA8 already had unrelated working-tree changes).

## Root cause and implementation

The saved volume candidate contained positive forecasts, but rank-scale niche
and specialist offsets suppressed all 6,032 positive forecasts across its two
folds. Generic manager mutations also used entry floors/replacement margins
in rank units against absolute net return/session. Diagnosis reproduces these
old offsets from saved evidence and requires unchanged cohort/source hashes,
all positive forecasts blocked, an original zero-fill result, and a successful
counterfactual replay before accepting the known failure class.

`ga9.recovery` is an offline deterministic diagnosis playbook. The supervisor
runs diagnosis, targeted engineering regressions, then a changed experiment with
`--repair edge_units_v2`, without chat or a code-writing agent. The adapter
removes uncalibrated rank offsets and uses explicit return/session floors and
replacement margins. The execution engine exposes `absolute_edges=True` for
opportunity/exploratory forecasts; legacy rank-score callers retain their
existing routing behavior. Slots, cash reserves, risk budgets, correlation,
sector limits, settlement, costs, marks and chronological windows are retained.
Zero-slot/full-cash candidates remain allowed; the repair never forces trades.

## Enforced unattended limits and restart behavior

- No Codex/LLM invocation, network acquisition or runtime source modification.
  Maximum model/API cost per attempt and overall: $0.
- At most two persisted attempts per dataset/playbook, each with a 300-second
  deadline, including kill grace allowance. Maximum recovery allocation: 600s
  per dataset, 1,200s if both synthetic and real datasets need recovery.
- Child phase ceilings: diagnosis 60s, tests 90s, experiment 150s. Experiment
  itself allows at most 120s and 48 evaluations per attempt.
- Interrupted/timed-out offline work can receive one retry with a new artifact
  namespace. Reserved attempts count across restart; a completed failure or
  unknown diagnosis is terminal with an actionable blocker, never an identical
  experiment retry. Successful completed work is restored from its report.
- Single-instance lock, fsynced reservations/checkpoints/journal, process-group
  termination, and ten-second child progress events remain active. Existing
  systemd CPU/memory/task/file restrictions remain in force.
- Repaired experiments retain best active candidate/replay evidence separately
  from the overall fitness winner, which can legitimately remain cash.

## Observed recovery and independent verification

Artifacts under `ga9/artifacts/autonomous_supervisor/`:

- `recovery_real_edge_units_v2_0_diagnosis.json`: EDGE_UNIT_MISMATCH;
  6,032 positive/blocked forecasts; 1,317 counterfactual historical fills.
- `recovery_real_edge_units_v2_0_tests.log`: automatic targeted regressions pass.
- `recovery_real_edge_units_v2_0_experiment/report.json` and
  `evaluations.jsonl`: 32 evaluations; 12 candidates active in both folds;
  17,156 fills summed over evaluations. These are repeated research replays,
  not distinct live executions.
- `recovery_verification.json`: independent replay of evaluation 10, the best
  active candidate, exactly reproduces saved counts and CAGR. First fold:
  322 fills, 180 trade decisions, +0.07144% CAGR, 0.94602% MDD. Second fold:
  247 fills, 168 trade decisions, -0.43104% CAGR, 0.48888% MDD. Contains first
  fills, accounting audits, cohort and quarantine evidence.

All 86 GA9 tests passed using:
`/opt/mts/.venv/bin/python -B -m unittest discover -s ga9 -t .`.

The final code was activated and restart persistence checked. Service active,
PID 830955 at 22:17:16 UTC; state EXPLORATORY_RECOVERED, one persisted attempt,
exactly three completed recovery phases. Restart created no new experiments or
recovery attempts and restored the 17,156-fill report. Planned restarts reached
the existing systemd start-rate limit; only that service's systemd failed/start
counter was cleared before starting it again. Research state/budgets were never
reset.

## Remaining limits

Recovery establishes functioning decisions/execution, not alpha. Cash remains
the overall fitness winner. The +20 percentage points annualized over both SPY
and QQQ target is unmet. The strict target and <8% MDD eligibility test remain
unchanged, and certification, final validation, promotion and production flags
are all false. FB/META and XLNX remain quarantined; the exposed 2022–2024 real
development window and synthetic forward exclusion are unchanged.

After this bounded development cycle reaches stagnation, the service remains
alive and idle with EXPLORATORY_RECOVERED. It does not continuously spend on
identical searches. Only the evidenced unit-mismatch class is repairable
unattended; unsupported forecasts, changed data, unknown allocator failures,
regression failures and exhausted retry budgets halt for engineering review.
No final-certification/PIT/holdout provenance blockers have been resolved.
