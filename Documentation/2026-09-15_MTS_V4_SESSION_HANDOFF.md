# MTS v4 Session Handoff — 2026-09-15

## Authority boundary

The governing rule remains unchanged:

> Deterministic code may reject invalid execution contracts. It may not reject valid scientific judgment.

The research model retains scientific authority over questions, hypotheses, methods, parameters, thresholds, horizons, interactions, interpretation, findings, and research direction. Deterministic code owns mechanical computation, validation, lineage, transport, persistence, reproducibility, spend enforcement, and execution-contract enforcement.

Source, filing, acquisition, schema, identity, persistence, and other mechanical failures should stop and return to the human/code-repair path. They should not consume a research-model call. Scientific uncertainty may be escalated to Sol under the approved supervisory policy.

## Executive status

MTS v4 has a materially stronger execution and research-governance architecture, but it has not yet demonstrated a validated tradable edge or portfolio performance. Eleven ticker studies spanning roughly 220 ticker-years have not produced a validated finding. This is evidence that the current discovery surface, data substrate, validation design, or research unit may be incomplete; it is not evidence that MTS outperforms marketed products.

The strategic response is now encoded in the repository: stop paying for unrestricted ticker-by-ticker discovery until the system demonstrates that it can recover blinded, established market-structure controls from independently prepared data.

The one exception is XOM: it is an already-started campaign with a durable, accepted continuation decision. Completing it does not authorize a new open-ended campaign.

## Current Git topology

| Role | Branch | Head |
|---|---|---|
| Active control-readiness work | `mts-v4-control-readiness-20260915` | `21d953fc27d306d69aee362a709a522777a2be26` before this handoff |
| Aggregate integration line | `mts-v4-generalization-qwen-controls-20260914` | `a6c227aa826f72e0c1e78732b73c862bcc0f4f7c` |
| Open draft review | PR #12 | Active branch into aggregate line |
| Mac current subset branch | `mts-v4-future-cohort-waiting-lifecycle-20260914` | `ef685136d581ae82f543d715e7f9a0e85da4ee1c` |
| Mac safety branch | `mac-local-before-update-20260915` | Preserves pre-update local state |

PR: https://github.com/davidbedwell/Momentum-Trading-System_v4/pull/12

The future-cohort branch is a subset, not the aggregate development line. Do not merge unrelated feature branches into it merely because it is currently checked out on the Mac.

## Control-readiness work completed

The active branch contains these commits, in order:

- `a0de10b` — Add skipped-month momentum control features
- `0495c33` — Test skipped-month momentum semantics
- `3d01eb7` — Add zero-SOL scientific control readiness gate
- `c0b320d` — Add zero-cost scientific control preflight CLI
- `2530caf` — Require zero-SOL readiness before paid controls
- `379ac54` — Expose per-control readiness enforcement
- `12d179d` — Gate paid universe discovery on scientific controls
- `f6d2e27` — Regress scientific control readiness and spend gates
- `98743dd` — Simplify control readiness test fixtures
- `2f643a7` — Document mandatory zero-SOL control readiness gate
- `4613ecb` — Gate new paid single-subject discovery on controls
- `21d953f` — Regress single-subject discovery spend gate

The latest verified GitHub Actions result before this handoff was 228 passing MTS v4 core tests.

### What the gate now requires

Five blinded controls define the calibration campaign:

1. Cross-sectional medium-term momentum
2. Trend persistence
3. Short-horizon reversal or continuation
4. Post-earnings-announcement drift
5. Deterministic negative control

The hidden answer key binds expected formulation, direction, horizons, robustness expectations, independent benchmark artifact hash, and exact dataset fingerprint. It is not sent to the research model.

The zero-SOL preflight checks:

- no unresolved placeholders;
- point-in-time universe membership;
- required features and outcomes;
- date and security coverage;
- complete numeric rows;
- duplicate observations;
- exact dataset fingerprint;
- independently supplied mechanical adequacy thresholds.

New paid universe discovery and new paid single-subject discovery require an independently assessed `CALIBRATION_PASS`. Dry runs remain available. `resume_fresh_subject.py` was deliberately not blocked because existing accepted campaigns, especially XOM, must remain resumable.

## What is still missing before paid discovery

The implementation is ready for integration review, not live scientific acceptance. The following are still required:

1. An authoritative point-in-time historical universe-membership and security-identity source.
2. A populated, real derived-market store.
3. Real-data arithmetic, adjustment, missingness, delisting, and identity validation.
4. A validated point-in-time historical earnings source for the PEAD control.
5. Independent benchmark artifacts and a frozen answer key.
6. Execution and independent grading of all five controls.
7. Qwen launch, replay, shadow evaluation, and explicit human approval.

A green unit-test gate proves code behavior. It does not prove the data, controls, or edge.

## XOM recovery state

Campaign root:

`/home/ubuntu/mts-v4-20y-revisit-batch-20260914_140944/XOM`

Campaign ID:

`mts-v4-sol-batched-xom-20260914_182805`

Durable state before Thunder became unavailable:

- 3 reconstructed decisions
- 3 reconstructed batches
- 86 recovered Analysis results
- latest report with 25 records
- counted subject spend: `$3.584056`
- accepted continuation sequence: 4
- 4 Research Packages
- 45 authorized analyses
- no prior Analysis re-execution allowed
- durable decision: `resume_interpretation_decision.json`

The continuation encountered evidence identity failures. Code repairs added explicit evidence-refresh authorization and then restored source-acquisition parity. The most recent intended action was to retry exact evidence reproduction without refresh authorization. No successful final XOM completion output was received before the Thunder instance disappeared.

Do not restart XOM from scratch. Do not call Sol merely to repair source, filing, acquisition, schema, or evidence-identity problems.

### XOM resume command

Run only after restoring the snapshot and verifying that the external XOM state directory is intact:

```bash
cd /home/ubuntu/Momentum-Trading-System_v4

set -a
source .env
set +a

.venv/bin/python scripts/resume_fresh_subject.py \
  --state-dir /home/ubuntu/mts-v4-20y-revisit-batch-20260914_140944/XOM \
  --total-sol-spend-limit-usd 12 \
  2>&1 | tee /home/ubuntu/MTS_V4_XOM_EXACT_EVIDENCE_CONTINUATION_20260914.txt
```

If it requests more authorization, do not raise the `$12` ceiling automatically. If it fails, stop and diagnose before another invocation.

## Thunder and local recovery

There is currently no active Thunder instance. The repository code is recoverable from GitHub, but campaign state stored outside the repository depends on the server snapshot or other recovered backup.

Before any pull or execution on a restored server, record:

```bash
cd /home/ubuntu/Momentum-Trading-System_v4
git branch --show-current
git rev-parse HEAD
git status --short

find /home/ubuntu/mts-v4-20y-revisit-batch-20260914_140944/XOM \
  -maxdepth 2 -type f -printf '%p %s bytes\n' | sort
```

The Mac repository is:

`/Users/davidbedwell/Documents/Momentum-Trading-System_v4`

A full local repository archive was identified as:

`MTS_V4_FULL_WORKING_BACKUP_20260914_211658.tar.gz`

That archive contains the repository and `.git`, but not the external XOM campaign directory. XOM diagnostic reports in Downloads are evidence and audit aids, not a replacement for the durable campaign state.

## Isolated TradingView pipeline test

If approximately 50 tickers of historical TradingView data are recovered, use them for a strictly non-scientific pipeline test. This can validate engineering without spending Sol tokens or contaminating scientific memory.

Required minimum fields:

- date
- ticker
- open
- high
- low
- close
- volume

Adjusted data and explicit split/dividend metadata are preferred.

The test must be labeled `PIPELINE_TEST_NONSCIENTIFIC` and must use a separate state root and separate Nexus. It must not:

- write to canonical scientific memory;
- promote findings or predictive hypotheses;
- make performance or generalization claims;
- call Sol;
- silently treat a convenience sample as a point-in-time universe.

It may test ingest, stable identity, adjustment handling, derived features and outcomes, cross-sectional ranks, Analysis execution, caching, lineage, checkpointing, persistence, and later Qwen transport. Record selection, survivorship, source, and adjustment limitations in every output.

## Qwen operating plan

Qwen is the next lower-cost research lead, distinct from the earlier AAPL-specific Qwen work.

Authority routing:

- Mechanical/source/filing/schema/identity/persistence errors return to the human and deterministic repair path.
- Scientific judgment remains with the research lead.
- Qwen may appeal genuinely scientific blockers to Sol.
- Sol should perform a full Qwen audit after three genuinely virgin tickers.
- Qwen does not receive autonomy merely because it can complete a run. It must first pass replay/shadow evaluation and explicit human approval.

The TradingView pipeline test can exercise Qwen transport later, but its outputs remain non-scientific and cannot count as virgin-ticker validation.

## Exact continuation order

1. Recover or provision a Thunder-capable instance and attach the saved snapshot.
2. Verify repository branch, head, worktree, environment configuration, and external XOM state before changing anything.
3. Finish XOM from the durable decision; do not create a fresh XOM campaign.
4. Review XOM completion, spend, package closures, promoted findings, evidence refreshes, and checkpoints; download an audit using the actual resolved filename.
5. Review PR #12 and the control-readiness branch. Keep it draft until the integration and scientific-control assumptions are reviewed.
6. If the TradingView dataset is recovered, implement and run the isolated zero-Sol pipeline test.
7. Select and validate the authoritative point-in-time universe and earnings sources.
8. Populate the real derived-market store and verify arithmetic and missingness on real data.
9. Freeze independent benchmark artifacts and the hidden answer key.
10. Pass zero-SOL preflight before any paid control call.
11. Run the bounded blinded-control campaign only with explicit human spend authorization.
12. Run Qwen replay/shadow evaluation; authorize Qwen only after review.
13. Analyze three virgin tickers under Qwen, allowing scientific appeals to Sol.
14. Have Sol audit the full Qwen work product before broader deployment.

## Non-negotiable constraints

- Do not claim the Sol cost target was achieved based on isolated calls.
- Do not weaken campaign, subject, package, question-lineage, evidence-identity, or spend validation.
- Do not re-execute prior Analysis results during resume.
- Do not blend old two-year studies with current twenty-year revisits as one campaign.
- Do not convert scientific judgment into deterministic rules.
- Do not use arbitrary precomputed hypotheses merely to suppress model calls.
- Do not allow pipeline-test results into canonical scientific memory.
- Do not resume paid open-ended discovery until the control gate passes.
- Do not describe infrastructure correctness as evidence of market edge.

## Scientific bottom line

The system has gained meaningful governance, durability, cost control, cross-sectional infrastructure, future-cohort lifecycle support, and now a hard calibration gate. It still has zero validated tradable findings and zero demonstrated live or independently benchmarked portfolio advantage. The next dollar should buy evidence that the research system can recognize known structure—not another unrestricted search over another ticker.
