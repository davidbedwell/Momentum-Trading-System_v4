# Momentum Trading System — Decision Execution Policy

**Status:** Canonical
**Authority:** Subordinate to `CHARTER.md`, canonical Architecture, and Governance Standards

---

## 1. Purpose

This policy governs the transition from a governed investment Decision to market
execution.

Decision determines investment intent. Execution implements that intent within
explicitly delegated bounds.

Execution must not become a second Decision Engine.

---

## 2. Authority Boundary

The Decision Engine owns governed investment intent within its granted authority.

Execution capability may implement an authorized Decision but may not
independently change:

- instrument;
- long/short direction;
- maximum authorized exposure;
- thesis;
- risk boundary;
- entry thesis;
- exit thesis;
- portfolio objective.

Task Manager coordinates authorized execution work. It does not originate or
reinterpret investment Decisions.

Accountability research gates do not approve individual trades.

Risk authority may block, constrain, reduce, or terminate exposure within its
granted authority. Risk authority must not originate a new speculative position.

---

## 3. Execution Eligibility

An execution task may be released only when all required conditions are valid,
including:

- a current governed Decision;
- required risk authorization/constraints;
- required automation authority;
- valid market/instrument state;
- valid account state;
- valid execution destination;
- applicable freshness window;
- required buying power or position availability;
- no governing suspension, cancellation, or safety block.

A technically executable order is not necessarily an authorized order.

---

## 4. Decision Freshness

Every executable Decision must have explicit freshness or validity semantics.

Execution must revalidate the Decision before order submission when material
time or market movement has occurred.

A stale Decision must be returned for reevaluation or expire according to its
contract. Execution must not silently reinterpret a stale Decision.

---

## 5. Bounded Execution Discretion

A Decision may delegate bounded implementation choices to execution, including
where explicitly authorized:

- limit-price selection within a permitted range;
- order type;
- order slicing;
- timing within an authorized window;
- venue selection;
- partial-fill handling;
- passive/aggressive placement;
- cancellation/replacement mechanics.

Every delegated choice must be machine-readable, bounded, observable, and
subordinate to the governing Decision and risk constraints.

---

## 6. Market Movement Between Decision and Order

Execution must detect material changes between Decision formation and order
submission.

If price, spread, liquidity, volatility, account state, or another governed
condition moves outside authorized execution bounds, execution must not improvise
a new investment thesis.

The task must be blocked, cancelled, resized where explicitly permitted, or
returned for Decision reevaluation.

---

## 7. Order Identity and Duplicate Prevention

Every order intent must have stable correlation/idempotency identity.

Retries, worker recovery, network interruption, or Task Manager restart must not
silently create duplicate market exposure.

Before replaying an uncertain order, MTS must reconcile venue/broker state.

---

## 8. Submission Is Not Execution

Sending an order does not establish that a trade occurred.

MTS must distinguish at least:

```text
AUTHORIZED
SUBMISSION_PENDING
SUBMITTED
ACKNOWLEDGED
PARTIALLY_FILLED
FILLED
CANCEL_PENDING
CANCELLED
REJECTED
EXPIRED
RECONCILIATION_REQUIRED
```

The exact schema may extend these states.

---

## 9. Partial Fills

Partial fills must update actual position, cash, exposure, and remaining order
state.

Execution may continue, cancel, or replace the remainder only within the
Decision's delegated bounds.

A partial fill must not be represented as a full position.

---

## 10. Rejections

Order rejection must be explicit and classified.

Execution must not repeatedly resubmit a rejected order without a permitted
recovery path.

Rejection does not automatically invalidate the underlying investment thesis.

---

## 11. Cancellation and Replacement

Cancellation/replacement must preserve lineage from the original Decision
through every order attempt.

Replacement orders must not increase authorized exposure unless the governing
Decision explicitly permits it.

---

## 12. Broker/Venue Reconciliation

Broker or execution-venue state is authoritative for what actually executed.

MTS internal intent is authoritative for what was authorized.

These states must be reconciled.

On disagreement, MTS must enter reconciliation/safety handling rather than
assuming either that an intended order filled or that a missing acknowledgement
means no fill occurred.

---

## 13. Position and Cash State

Execution results must update governed account state, including as applicable:

- cash;
- buying power;
- open positions;
- average cost;
- realized P&L;
- unrealized P&L;
- pending orders;
- reserved capital;
- portfolio exposure.

Decision evaluation must use reconciled account state.

---

## 14. Costs and Slippage

Execution evaluation must account for material implementation costs, including
where applicable:

- spread;
- commissions/fees;
- slippage;
- market impact;
- borrow cost;
- option-specific execution costs.

Research or Decision performance must not be represented as executable economic
performance when material execution costs are omitted.

---

## 15. Live Paper Validation Boundary

Before MTS becomes eligible for real-money execution, it must complete the
governed Live Paper Validation stage defined by the Live Paper Validation
Architecture and applicable validation policy.

Paper execution must use the same Decision, risk, task, account-state, and
execution contracts intended for live operation wherever technically possible.

The execution destination is changed; the Decision standard is not relaxed.

---

## 16. Paper and Live Isolation

Paper and real-money destinations must be explicitly identified and isolated.

A paper-trading task must never be routable to a live brokerage destination by
implicit default, filename, environment accident, or missing configuration.

Live execution must require affirmative governed enablement.

---

## 17. Real-Money Enablement

Successful paper trading does not automatically grant live-trading authority.

Transition to real-money execution requires the separate objective validation
criteria and authority defined by governance.

Failure to meet those criteria leaves live execution disabled.

---

## 18. Emergency Risk Intervention

Authorized risk/safety controls may prevent submission, cancel pending exposure,
reduce exposure, or close exposure within their granted authority.

Emergency intervention must be recorded and reconciled.

Emergency authority must not be used to originate unrelated speculative
positions.

---

## 19. Human Intervention

Authorized human intervention may pause, cancel, or constrain execution within
governed authority.

Manual intervention must preserve audit lineage.

A graphical interface does not create authority merely because it exposes an
execution control.

---

## 20. Observability and Audit

MTS must be able to reconstruct:

```text
Decision
→ risk/automation authority
→ execution task
→ execution worker
→ order intent
→ broker/venue acknowledgement
→ fills/rejections/cancellations
→ reconciled account state
→ resulting Decision state
```

Material execution events must be machine-readable and auditable.

---

## 21. Failure Safety

When execution state is uncertain, MTS must prefer reconciliation over blind
replay.

When authority is uncertain, MTS must not initiate new exposure.

When account state is uncertain, MTS must not assume buying power or position
availability.

---

## 22. Closing Principle

> **Decision determines what MTS intends to do. Execution determines how an
> authorized Decision is implemented within explicit bounds. Actual broker/venue
> state determines what occurred.**
