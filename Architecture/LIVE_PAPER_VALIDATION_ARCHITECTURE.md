# Momentum Trading System — Live Paper Validation Architecture

**Status:** Canonical Architecture

---

## 1. Purpose

Live Paper Validation is the final pre-live validation stage for MTS investment
Decision and execution behavior.

It occurs only after the Decision Engine has already been evaluated across a
broad universe or sufficiently large and representative sample of trade
opportunities and both successful and failed Decisions have been evaluated
through governed learning and validation.

The stage tests whether the integrated system can operate under live market
conditions before real capital is exposed.

---

## 2. Validation Sequence

The intended progression is:

```text
historical / broad-universe research and evaluation
        ↓
Decision evaluation across many trade opportunities
        ↓
evaluation of successful and failed outcomes
        ↓
governed learning / validation
        ↓
Live Paper Validation
        ↓
objective promotion review for live eligibility
        ↓
real-money execution eligibility, if separately authorized
```

Live Paper Validation must not be used as a shortcut around prior scientific,
Decision, learning, or validation work.

---

## 3. Initial Paper Bank

The initial development validation profile shall begin with:

```text
$10,000 simulated starting equity
```

The $10,000 amount defines the initial development validation profile. It is not
a permanent architectural capital requirement and may later be represented as
governed configuration.

The paper account must be treated as a finite portfolio, not as an unlimited
scorekeeping balance.

---

## 4. Live Conditions

Paper validation must operate against current live market conditions using the
same current-state inputs intended to inform real Decisions.

The test must preserve temporal causality: MTS may use only information that
would have been available at the relevant Decision/execution time.

---

## 5. Same Decision Logic

The Decision Engine must not receive easier criteria because the destination is
paper.

Where technically possible, the same governed contracts must drive both paper
and future live operation.

The primary destination difference is:

```text
PAPER EXECUTION DESTINATION
vs.
LIVE EXECUTION DESTINATION
```

not a different investment thesis or relaxed Decision process.

---

## 6. Portfolio State

The paper account must maintain reconciled simulated state for at least:

- starting equity;
- available cash;
- buying power;
- open positions;
- pending orders;
- reserved capital;
- average cost;
- realized P&L;
- unrealized P&L;
- portfolio equity;
- gross/net exposure;
- position concentration.

Decision sizing must respect the paper account's actual simulated state.

---

## 7. Execution Realism

Paper validation should model or obtain realistic execution behavior to the
extent technically practical, including:

- bid/ask spread;
- order type;
- partial fills where supported/modelled;
- slippage;
- commissions and fees where applicable;
- liquidity constraints;
- market session;
- rejected/cancelled orders;
- stale Decision handling;
- execution latency where material.

A perfect fill assumption must not silently inflate validation performance.

---

## 8. Opportunity Selection

The paper account must receive opportunities through the same governed
candidate-ranking and Decision process intended for live operation.

Trades must not be manually cherry-picked after their outcomes are known.

No forward information may influence candidate selection, entry, sizing, hold,
add, reduce, or exit decisions.

---

## 9. Successes and Failures

Winning and losing trades are both validation evidence.

The validation process must evaluate:

- profitable Decisions;
- losing Decisions;
- missed opportunities;
- false positives;
- premature exits;
- late exits;
- sizing errors;
- execution errors;
- no-action Decisions where measurable;
- risk interventions.

A losing trade is not automatically a Decision defect. A profitable trade is
not automatically a valid Decision.

---

## 10. Learning Separation

Paper outcomes may generate learning/research inputs, but the system must not
silently rewrite its rules mid-test in a way that destroys comparability.

Material model, knowledge, Decision, risk, or execution changes during the
validation campaign must be versioned.

Governance must determine whether a material change requires a new validation
campaign or a separately identified validation phase.

---

## 11. Objective Live-Eligibility Gate

Completion of paper trading is not sufficient.

Before real-money eligibility, MTS must satisfy objective criteria defined in
governance.

Criteria should address at least:

- sufficient sample size;
- sufficient opportunity/regime diversity;
- performance after realistic costs;
- drawdown behavior;
- risk-limit adherence;
- portfolio concentration;
- execution correctness;
- reconciliation correctness;
- absence of unresolved critical defects;
- reproducibility/audit completeness;
- stability of Decision behavior;
- evaluation of both successes and failures.

Exact thresholds must be established before the qualifying campaign is judged,
not invented after seeing the results.

---

## 12. No Automatic Promotion to Live

Passing Live Paper Validation makes MTS eligible for the separately governed
live-authorization process.

It does not itself enable live execution.

Live execution remains disabled until affirmative governed authority exists.

---

## 13. Failure

If Live Paper Validation fails its objective criteria:

- live execution remains disabled;
- failure evidence is preserved according to governance;
- defects/questions may initiate governed research or engineering work;
- a subsequent qualifying campaign must be separately identifiable.

MTS must not lower criteria retrospectively merely to pass.

---

## 14. Auditability

The complete campaign must be reconstructable from:

```text
market state
→ candidate ranking
→ Decision
→ paper execution
→ simulated fills
→ portfolio state
→ subsequent Decision changes
→ outcome
→ evaluation
```

The campaign must identify the exact versions of material knowledge,
configuration, Decision logic, risk logic, and execution logic used.

---

## 15. Relationship to Trader Interface

The future trader-facing graphical interface may display the live paper account
exactly as it would display a live account, provided the execution destination
is unmistakably identified as PAPER.

The interface must not obscure or blur the distinction between simulated and
real-money execution.

---

## 16. Closing Principle

> **Live Paper Validation is the final rehearsal with live information and
> simulated capital. MTS must demonstrate that its integrated Decision and
> execution system behaves economically, operationally, and scientifically as
> intended before real capital becomes eligible for exposure.**
