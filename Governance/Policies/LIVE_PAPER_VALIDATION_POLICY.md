# Momentum Trading System — Live Paper Validation Policy

**Status:** Canonical
**Authority:** Subordinate to `CHARTER.md`, canonical Architecture, and Governance Standards

---

## 1. Requirement

Real-money execution must remain disabled during development until MTS has
completed the required Live Paper Validation campaign and passed the applicable
objective live-eligibility criteria.

---

## 2. Preconditions

A qualifying Live Paper Validation campaign may begin only after:

1. Decision behavior has been evaluated across a broad universe or sufficiently
   large and representative sample of trade opportunities;
2. both successful and failed trade outcomes have been evaluated;
3. material findings have passed applicable governance;
4. critical known Decision/execution defects that would invalidate the campaign
   are resolved;
5. the validation configuration and evaluation criteria are frozen/versioned.

---

## 3. Initial Development Account

The initial qualifying development profile uses:

```text
starting_equity = 10000 USD
execution_mode = PAPER
```

The account must be finite and stateful.

---

## 4. No Cherry-Picking

Qualifying paper trades must arise from the governed live candidate and Decision
process.

Trades may not be selected, removed, relabeled, or excluded because their
subsequent outcome is inconvenient.

Any legitimate exclusion rule must be defined before outcome evaluation.

---

## 5. Causality

Only information available at the relevant time may influence a paper Decision
or simulated execution.

Forward-looking contamination invalidates the affected evidence and may
invalidate the campaign.

---

## 6. Economic Realism

Performance evaluation must include realistic implementation assumptions or
broker-provided paper fills where suitable.

Known systematic optimism in paper fills must be identified and, where
practical, corrected or conservatively modeled.

---

## 7. Portfolio Constraint

The Decision Engine must operate against current paper-account state.

It may not size every opportunity as though the full $10,000 remains available.

Open positions, reserved capital, losses, gains, concentration, and buying power
must affect subsequent eligible Decisions as they would in the governed live
design.

---

## 8. Campaign Integrity

Material changes to Decision, risk, execution, knowledge, or validation logic
during a qualifying campaign must create a new identifiable version/phase.

Governance determines whether accumulated results remain comparable or whether
the qualifying campaign must restart.

---

## 9. Evaluation of Outcomes

Evaluation must include winning and losing trades and must distinguish:

- Decision quality;
- execution quality;
- risk behavior;
- portfolio behavior;
- market outcome.

Profit alone is not sufficient evidence of correctness.

Loss alone is not sufficient evidence of defect.

---

## 10. Objective Criteria

Qualifying criteria must be defined before final evaluation.

They must include objective measures for sample sufficiency, economic
performance, drawdown/risk behavior, execution/reconciliation integrity,
portfolio behavior, critical defects, and audit completeness.

The criteria may be refined between campaigns through governance.

They must not be retrospectively weakened to convert a failed campaign into a
pass.

---

## 11. Promotion Result

The campaign result must be one of:

```text
PASS
FAIL
INVALID
INSUFFICIENT_SAMPLE
```

`PASS` means eligible for the separately governed live-authorization process.

It does not mean live execution is automatically enabled.

---

## 12. Real-Money Safety Boundary

Paper and live destinations must be technically and operationally separable.

During paper validation, absence or corruption of execution-mode configuration
must fail closed rather than default to live execution.

---

## 13. Evidence Preservation

Campaign evidence sufficient to reproduce and audit the qualification result
must be retained under applicable artifact/storage governance.

---

## 14. Closing Principle

> **MTS earns eligibility to expose real capital only after its integrated
> behavior has been tested prospectively under live market conditions using a
> finite simulated portfolio and predeclared objective criteria.**
