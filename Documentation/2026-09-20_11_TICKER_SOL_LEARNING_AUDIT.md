# 11-Ticker Sol Revisit Learning Audit — 2026-09-20

## Human-authorized run

The required revisit sequence remains:

AAPL → AMD → AMZN → BA → GOOGL → JPM → META → MSFT → NVDA → TSLA → XOM

The Sol spend authorization boundary is **$7.00 per ticker**, or **$77.00 maximum across eleven subjects**. This is a hard operational ceiling, not a scientific target. Expected economic performance remains approximately $5–$6 per ticker; Sol must not narrow, rank, suppress, or reshape scientifically justified work to fit either the expectation or ceiling.

## Learning questions to audit

The campaign must preserve enough explicit scientific provenance to answer:

1. Did Sol follow MTS governance and retain scientific autonomy under the cost-efficiency changes?
2. Did Sol deliberately apply prior or otherwise established predictive structures to locate prospective trading opportunities in the active ticker?
3. When exact evidence supports counting, how many unique raw, executable non-overlapping, and positive-net-EV candidate opportunities occurred per observed month?
4. What strategies did Sol judge genuinely novel rather than reducible to prior/established structures?
5. Across the ordered eleven subjects, did Sol begin to generalize transferable market structure, including explicit support, contradictions, regime limitations, and exceptions?

## Authority boundary

Deterministic code may aggregate telemetry and Sol-authored annotations. It may not decide whether a strategy is scientifically known, novel, transferable, important, or valid.

Sol therefore maintains a compact cumulative `research_state.campaign_learning_audit_state` containing:

- prior/established structure applications and provenance;
- exact opportunity-frequency summaries only when supported by completed evidence;
- novel-strategy claims and why Sol judges them distinct;
- cross-subject generalization claims, supporting subjects, contradictory subjects, and evidence references.

When exact opportunity counts or observation-month denominators are unavailable, Sol must record null rather than estimate or invent them.

The audit annotations are observability metadata, not a research agenda. They may not force Sol to reuse prior structures, inhibit novel discovery, or substitute for Research Packages, findings, hypothesis lifecycle controls, validation, or trading-promotion governance.

## Objective post-run report

At campaign terminal state—COMPLETE or STOPPED—the sequential runner invokes `scripts/audit_11_ticker_learning.py`. It writes:

- `MTS_V4_11_TICKER_LEARNING_AUDIT.json`
- `MTS_V4_11_TICKER_LEARNING_AUDIT.txt`

The deterministic report aggregates:

- Sol call counts;
- prompt and completion tokens;
- provider-reported call cost when available;
- Sol-authored known-structure applications;
- exact opportunity-frequency rates when available;
- Sol-authored novel-strategy claims;
- Sol-authored cross-subject generalization claims.

The report explicitly does **not** independently prove novelty or generalization. Those claims require subsequent audit against the durable Research Packages, Nexus, and evidence lineage.

## Scientific continuity

The existing sequential-learning rule remains controlling: each later ticker may receive compact durable science from prior subjects, but prior science is context rather than a mandatory agenda. Local ticker discovery remains independently important. Increasing evidence of generalization should arise from the eleven-subject record, not from deterministic pressure to generalize.
