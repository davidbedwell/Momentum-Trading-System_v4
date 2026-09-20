# Known Predictive Theory Coverage — 2026-09-20

## Human decision

MTS must give Sol scientific knowledge of established predictive theories and empirical relationships relevant to price movement. These theories are not privileged because they are known, but the eleven-ticker revisit must not omit them.

For each active ticker, every catalog theory in `MTS_V4/known_predictive_theories.py` requires a terminal disposition before subject closure:

- `TESTED_SUPPORTED`
- `TESTED_UNSUPPORTED`
- `TESTED_MIXED`
- `OBJECTIVELY_NOT_TESTABLE`

The last status is permitted only when the necessary evidence is genuinely unavailable and must identify the missing evidence.

## Scientific authority

Required coverage is a human research-governance requirement, not a deterministic scientific conclusion.

Sol retains authority over:

- the scientifically appropriate representation;
- method;
- thresholds;
- horizons;
- interactions and conditioners;
- whether canonical direction is appropriate;
- interpretation;
- significance;
- whether a finding or trading candidate should be promoted;
- whether additional novel research is warranted.

Appearance in the catalog gives a theory **zero automatic evidentiary weight**. A known theory may fail completely on a ticker. An omitted theory is not disfavored: Sol's novel-discovery space remains unrestricted.

## Why coverage is required

The human wants MTS to answer both:

1. whether established predictive ideas can identify executable profitable opportunities in the eleven revisited tickers, and at what frequency; and
2. whether Sol discovers useful predictive structure outside those established ideas.

Without required coverage, a scientifically autonomous RD could legitimately ignore a known theory and the experiment would be unable to answer the first question.

## Closure enforcement

Deterministic code checks representation completeness only. Before subject closure it verifies that every catalog `theory_id` has one terminal disposition. For a tested theory, the Sol-authored record must contain a scientific formulation, evidence references, and interpretation. Deterministic code does not judge whether the interpretation is correct.

This is a breadth/completeness gate analogous to other human-authorized scientific coverage requirements; it does not rank theories or require positive findings.

## Transport

The full theory catalog is supplied on the initial Sol call. Continuation calls receive a compact index while Sol's cumulative audit state carries the scientific work forward. This avoids replaying descriptive prose while preserving required coverage identities.
