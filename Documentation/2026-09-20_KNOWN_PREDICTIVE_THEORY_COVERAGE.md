# Known Predictive Theory Coverage — 2026-09-20

## Human decision

MTS must give Sol scientific knowledge of established predictive theories and empirical relationships relevant to price movement. The theory catalog is prior scientific knowledge, not evidence. The eleven-ticker revisit must test the catalog theories where the required market evidence is available.

For each active ticker, every catalog theory in `MTS_V4/known_predictive_theories.py` requires a terminal disposition before subject closure:

- `TESTED_SUPPORTED`
- `TESTED_UNSUPPORTED`
- `OBJECTIVELY_NOT_TESTABLE`

There is deliberately no `TESTED_MIXED` terminal category. Quantitative heterogeneity, regime dependence, partial success, success rate, expectancy, path behavior, and other nuance remain in the Analysis results. The terminal supported/unsupported disposition is determined under the already-governed MTS success/candidacy schema rather than by inventing a separate qualitative threshold for known theories.

`OBJECTIVELY_NOT_TESTABLE` is permitted only when the necessary market evidence genuinely is unavailable and must identify the missing evidence.

## Theory, test, and evidence boundary

The theory catalog itself is **not evidence**. It makes Sol aware of established hypotheses and proposed predictive relationships so that MTS does not have to rediscover their existence.

Required testing is a research-coverage obligation, not evidence for the theory. Evidence arises from the market data and governed Analysis results produced by testing the theory on the active subject.

Accordingly:

- catalog membership contributes zero support;
- required testing contributes zero support;
- actual governed test results supply the evidence;
- the existing MTS success/candidacy schema determines whether those results warrant `TESTED_SUPPORTED` or `TESTED_UNSUPPORTED`;
- quantitative results remain available regardless of the terminal label.

## Scientific authority

Required coverage is a human research-governance requirement, not a deterministic scientific conclusion.

Sol retains authority over:

- the scientifically appropriate representation;
- method;
- thresholds and horizons except where existing governance already fixes an applicable success/candidacy criterion;
- interactions and conditioners;
- interpretation of the Analysis results;
- significance and durable finding promotion;
- whether additional novel research is warranted.

Appearance in the catalog gives a theory **zero automatic evidentiary weight**. A known theory may fail completely on a ticker. Catalog coverage also does not delimit discovery: Sol remains free to investigate predictive structures outside the catalog.

## Why coverage is required

The human wants MTS to answer both:

1. whether established predictive ideas can identify opportunities that satisfy the already-governed MTS success/candidacy criteria in the eleven revisited tickers, and at what frequency; and
2. whether Sol discovers useful predictive structure outside those established ideas.

Without required coverage, a scientifically autonomous RD could legitimately ignore a known theory and the experiment would be unable to answer the first question.

## Closure enforcement

Deterministic code checks representation completeness. Before subject closure it verifies that every catalog `theory_id` has one terminal disposition. For a tested theory, the record must retain its scientific formulation and references to the actual Analysis results used for disposition. Those result references are evidence from the test; they are not evidence supplied by the theory catalog.

The closure gate must reject `TESTED_MIXED`. It must not create a second deterministic success standard. Supported versus unsupported must follow the existing MTS success/candidacy governance and preserve the underlying quantitative results.

## Transport

The full theory catalog is supplied on the initial Sol call. Continuation calls receive a compact index while Sol's cumulative audit state carries the scientific work forward. This avoids replaying descriptive prose while preserving required coverage identities.
