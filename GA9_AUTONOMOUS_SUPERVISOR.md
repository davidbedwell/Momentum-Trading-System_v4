# GA9 exploratory supervisor — active development mode, 2026-10-29

The user explicitly authorized a **development-only** override of missing research
certification. This supersedes the prior research STOP only for the separate
`ga9.exploratory` adapter. Final validation, promotion and production remain
blocked. All outputs say `EXPLORATORY_UNCERTIFIED_DEVELOPMENT_ONLY`; none is certified.
The historical audit and its blockers below are retained as evidence, not the
current mode. No GA8 source, process or configuration was changed by this work.

Implementation: `ga9/exploratory.py`, explicit supervisor `--mode exploratory`.
Default CLI mode remains `audit`. The existing archive's
`require_replay_inputs()` still unconditionally rejects certified replay; the
new adapter does not manufacture PIT credentials or rewrite certification flags.
No final-evaluation or promotion path exists in this adapter.

Observed host `ubuntu-32gb-hel1-1` (Hetzner), service enabled/active. Initial new PID
829749; verified post-restart PID **830227**, active/enabled, one task and ~7.5 MB
current memory. **31 tests passed**. Restart preserved exactly two completed
experiment reservations and 44/28 evaluation rows; neither experiment reran.
Final verification: `activation_verification.json`. It executed both experiments and now remains alive in
`EXPLORATORY_HALTED`, intentionally doing no recurring work after stagnation.

## Actual first run

| Dataset | Evaluations | Generations observed | Attempts | Evaluations trading | Outcome |
|---|---:|---:|---:|---:|---|
| Synthetic | 44 | 11 | 3 | 33 | Repair budget exhausted after stagnation; benchmarks missing; no success |
| Available real historical | 28 | 7 | 3 | 7 | Repair budget exhausted after stagnation; cash selected; failed both benchmark comparisons |

Synthetic best fold net CAGR: 7.760% / 4.019%; MDD: 0.432% / 0.700%.
Real best fold net CAGR: 0% / 0%, MDD: 0% / 0%, fills: 0 / 0.
Real matched SPY price-return CAGR: 24.844% / 16.150%; QQQ: 28.086% / 19.747%.
These are reused **development** folds, not independent out-of-sample claims.
Trading real-data candidates existed (up to 978 fills in a fold); cash won the
risk-adjusted worst-fold selection score. This is a negative research outcome,
not successful profitability or certified validation.

Best-model precursor/failed-lookalike training counts, first/second fold:
synthetic 0/786 and 42/1252; real 189/1406 and 240/2341. The first synthetic fold
had no positive precursor labels, an explicit support limitation.

Real cohort: first 16 alphabetic archive symbols outside existing protected
identities, complete positive execution marks only. This is a bounded functional
cohort with survivorship/selection bias, not the full historical universe.
Development dates 2022-01-03 through 2024-12-31; selection folds begin 2023-07-05
and 2024-04-03. Source parquet files are read then filtered before features/labels;
this is logical exclusion, not access-controlled sealed-data custody.
Synthetic uses only indices [0,756); its existing forward [756,1260) is excluded.
No 2025/2026 real rows enter features, fitting, selection or replay.

Trailing features use current/past closes only. Fixed precursor definition:
prior 20-session move between -10% and +8%, subsequent 20/40/60-session peak at
least +20% and positive terminal net return. Failed lookalikes use the same
causal feature bins and early condition with terminal net return <=0; all other
nonwinners remain training controls. Labels mature strictly before each training
cutoff. Bin means, precursor probabilities and failure probabilities determine
net forecast edges; evolving family, horizon and manager choices feed the GA9-B
funded next-open portfolio replay. Overlapping labels are not independent samples;
probabilities are descriptive training frequencies, not calibrated confidence.

Benchmark discovery reuses the existing SPY comparator and cached raw Alpaca QQQ
responses, with provenance hashes; missing dates/marks report missing and cannot
pass. No new API calls. Comparisons use identical replay dates, first executable
open and fixed entry costs, final closing marks. All are **price returns**, with
zero distributions assumed, unreconciled corporate actions and no total-return
certification. Fixed costs: 5bp slippage plus 1bp fees per transaction side;
uninvested cash earns zero; engine T+2 settlement, funded caps and next-open exits.
Open terminal positions are marked rather than forcibly liquidated. MDD <8% and
net CAGR > max(SPY, QQQ) +20 percentage points remain strict target requirements.
They are not guaranteed across price gaps, and neither experiment passed.

## Bounds, repair and persistence

No total-generation limit: generations continue while meaningful fitness improves
and resource budgets remain. Each dataset gets <=48 candidate evaluations,
<=120 seconds inside the child, <=3 attempts and two stagnant generations per
attempt. Meaningful improvement is >0.00001 in worst-fold net benchmark excess
minus twice MDD (10-point infeasibility penalty). Missing benchmarks use absolute
net return solely for engineering selection, never target success.
A stagnant attempt stops and records diagnosis, changes label horizon and reseeds
families/mutates the best manager. No unbounded self-rewriting. At most one clean
process retry after a child failure, 150-second parent timeout per reservation;
interrupted/indeterminate work never automatically repeats. Maximum four child
reservations, <=600 seconds including child timeouts, plus bounded setup/teardown.
Existing one CPU/1 GiB/32-task/file limits remain. No model/API invocation path:
Codex/LLM spend $0. Artifact count is bounded by evaluation budgets; no disk-quota
claim. Durable steps survive restart and prevent repeating completed experiments.

Evidence under `ga9/artifacts/autonomous_supervisor/`:
`activation_outcomes.json`, `state.json`, `audit.jsonl`, and each
`exploratory_{synthetic,real}_v1_retry0/{inputs,progress,best,report}.json` plus
`evaluations.jsonl`. Best files include trained models, full fills and NAV replays;
every candidate has metrics and comparisons in the append journal. Prior audit
and remediation reservations remain preserved.

## Commands executed

```bash
/opt/mts/.venv/bin/python -B -m unittest ga9.test_exploratory ga9.test_supervisor ga9.test_execution ga9.test_opportunity ga9.test_benchmarks ga9.test_nasdaq_archive
install -m 0644 ga9/supervision/ga9-research-supervisor.service /etc/systemd/system/ga9-research-supervisor.service
systemctl daemon-reload
systemctl restart ga9-research-supervisor.service
# Initial restart hit a historical systemd start-limit counter. Diagnosed in journal;
# cleared once, without deleting or resetting research state:
journalctl -u ga9-research-supervisor.service --no-pager -n 25
systemctl reset-failed ga9-research-supervisor.service
systemctl start ga9-research-supervisor.service
systemctl show ga9-research-supervisor.service -p MainPID -p ActiveState -p UnitFileState
# Restart verification preserves all completed reservations:
systemctl restart ga9-research-supervisor.service
```

Operational inspection: read `state.json`, experiment reports and
`activation_outcomes.json`; `journalctl -u ga9-research-supervisor.service`.
Stopping: `systemctl stop ga9-research-supervisor.service`.
Restarting does not allocate fresh research budgets. A new experiment protocol
needs an explicit new durable reservation/version; do not delete evidence.

---

## Historical audit-only activation (superseded mode; retained evidence)

# GA9 autonomous supervisor — 2026-10-29

**Activated: persistent systemd audit/engineering supervisor. Research: BLOCKED.**
Observed PID: **828774** (changes on restart). Unit:
`ga9-research-supervisor.service`, enabled at boot, active/running. No evolution,
portfolio replay, final-holdout evaluation, autonomous Codex call or profitability
claim. The GA9A_ITERATIVE_RESEARCH.md STOP remains in force.

Implementation: `ga9/supervisor.py`; deployment unit:
`ga9/supervision/ga9-research-supervisor.service`. Host unit installed at
`/etc/systemd/system/ga9-research-supervisor.service`.

## Actual evidence

Evidence root: `ga9/artifacts/autonomous_supervisor/` (ignored runtime artifacts).

- `state.json`: current PID, steps, exit codes, blockers and next action.
- `audit.jsonl`: fsynced append-only operational journal; not a tamper-proof external ledger.
- `archive_audit/coverage.json`: fresh read-only archive audit returns
  BLOCKED_NOT_PIT_CERTIFIED; replay_executed=false, long_GA_executed=false.
- `alpaca_remediation/report.json`: **two** configured Alpaca SIP requests,
  six raw gap records recovered, **zero certified**, zero accepted raw rows,
  5,500 diagnostic raw gaps remaining. Downloads are quarantined diagnostics,
  never integrated into research inputs. Exit 2 denotes the continuing gate.
- `engineering_regression_v2.log`: **27 tests passed inside the hardened service**,
  covering supervisor lock/resume/timeout/strict target boundaries, Alpaca repair,
  archive rejection and identity lineage. Synthetic tests establish engineering
  behavior only. Initial `engineering_regression.log` retains its failed attempt:
  read-only filesystem prevented temporary files. Fixed by placing temporary files
  inside the service's writable state directory; retained prior evidence.
- Service was restarted after activation. Completed audit/acquisition reservations
  survived, and neither download nor archive audit repeated. No real reboot or
  power-loss test was performed. Restart/boot support comes from systemd enablement
  and on-disk checkpoints, not a claim of an observed reboot.

## Safety and bounds

One exclusive nonblocking flock per state directory; a duplicate exits 73.
The installed service has one fixed state directory. Each step is durably reserved
before execution; atomic JSON replacement and file/directory fsync checkpoint it.
A crash during a reserved step leaves an indeterminate RUNNING record: restart
**does not retry it**. Inspect its evidence manually before any new work. Corrupt
state fails closed; no automatic reset or deletion of evidence.

Service cgroup: one CPU, 1 GiB RAM, no swap, 32 tasks, 128 file descriptors,
64 MiB individual file limit. Sequential audit/repair/regression wall limits are
300/90/180 seconds; terminated process groups get five seconds before SIGKILL.
Systemd stop kills the whole cgroup within 15 seconds. SIGTERM/SIGINT checkpoint
safe shutdown. Restart-on-failure waits 30 seconds, limited to three starts per
hour. No periodic API retries. The finite work plan and request budget bound
artifact creation; blocked waiting generates no recurring logs or downloads.
This is not a filesystem-wide disk quota. Journal retention follows host policy.

ProtectSystem=strict and ProtectHome=read-only permit writes only to this GA9
runtime directory; GA8 is explicitly read-only. No GA8 changes, process stops,
commit/reset/stash or pipeline replacement were performed. Existing dirty files
and commits were preserved. PrivateTmp is deliberately disabled so the existing
archive remains visible read-only. Source credentials are consumed by the existing
Alpaca client and never copied into state or logs.

LLM spending cap is **$0**, enforced by having no model invocation path. No child
Codex spawning, API purchases, subscriptions or paid-data expansion. Existing
Alpaca access is used for at most two requests per durable reservation; no claim
is made about the account's preexisting subscription charges.

## Exact limitation and restart prerequisites

This is the requested fallback bounded server experiment/audit supervisor, not a
working autonomous strategy researcher. Its automated work is audit -> bounded
safe acquisition -> engineering checks -> diagnose blockers -> halt research.
It remains alive in BLOCKED so systemd and operators can inspect it. It does not
silently resume upon a user-supplied certification boolean. No real evolutionary
adapter, automatic strategy reengineering or spending-bounded Codex loop is
installed: the current archive adapter rejects replay authorization, and no
independent enforceable Codex dollar-budget mechanism is available. Automatically
rewriting research code under those conditions would bypass the existing STOP.

Actionable blockers:

1. Supply auditable historical eligibility with known_at, stable security IDs,
   complete membership events/starting roster, failed/delisted security outcomes;
   reconcile protected aliases and retain quarantine. Do not substitute DEV79.
2. Reconcile corporate actions and terminal proceeds, independent sessions,
   warmup/exit marks and SPY **and** QQQ total-return provenance/cost policy.
   Raw Alpaca bars alone cannot certify any of these.
3. Establish custody of a truly untouched final period. All previously exposed
   forward intervals remain excluded. No final-period data was opened by this
   supervisor. There is currently no certified replacement holdout.
4. Implement and review a development-only adapter with chronological folds,
   label-maturity purging, frozen costs and identical benchmark periods. An
   independent gate must verify underlying provenance, not just manifest labels.
5. Before any final evaluation freeze code/data hashes, features, chromosome,
   calibration, fold protocol and benchmark policy. Use an external custodian or
   access-controlled evaluator for exactly one final evaluation. Failed final
   results are never optimization feedback for that period.

Required future research state machine (specification, **not currently active**):
evolve on development folds -> measure net results -> if no positive progress,
stop that attempt immediately -> persist diagnosis -> bounded reviewed repair ->
new development attempt. Use per-attempt wall time and stagnation bounds, no
arbitrary total-generation cap. Stop repeated ineffective repairs under an
explicit resource/spending budget rather than recurse indefinitely. Require net
CAGR strictly greater than **max(SPY CAGR, QQQ CAGR) + 0.20** over identical dates
and portfolio MDD **strictly <0.08**; never relax either. `target()` tests these
numeric boundaries but is not a market-performance verification adapter.

## Operations

Run host commands from the repository root (service management requires host
privileges). Restart resumes reservations; it does not start a new research run.
Do not delete state to bypass the certification gate or to repeat acquisition.

```bash
systemctl status ga9-research-supervisor.service
systemctl show ga9-research-supervisor.service -p MainPID -p ActiveState -p UnitFileState
cat ga9/artifacts/autonomous_supervisor/state.json
journalctl -u ga9-research-supervisor.service --no-pager -n 50
systemctl stop ga9-research-supervisor.service
systemctl start ga9-research-supervisor.service
systemctl restart ga9-research-supervisor.service
# Disable persistence if desired:
systemctl disable --now ga9-research-supervisor.service
# Engineering validation, no market replay:
/opt/mts/.venv/bin/python -B -m unittest ga9.test_supervisor ga9.test_alpaca_repair ga9.test_nasdaq_archive ga9.test_ticker_lineage
```

The implementation intentionally offers no `--force`, certification override,
automatic holdout unseal, or research-enable switch. Resolving the blockers
requires a reviewed implementation change and new protocol, not restarting this
blocked service. No success against either benchmark has been established.
