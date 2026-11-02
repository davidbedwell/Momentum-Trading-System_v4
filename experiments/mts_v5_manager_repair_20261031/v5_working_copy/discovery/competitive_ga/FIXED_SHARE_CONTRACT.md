# fixed-shares-v1 (bounded research execution only)

`share_order_contract.Tape` is a frozen, tuple-backed in-memory contract. Money
and prices are finite `Decimal` values; no binary float conversion or cent
rounding occurs. Callers must use a consistent Decimal context. This is not a
wire format, authenticated market-input gate, sizing policy or broker contract.

The calendar is explicit, strictly increasing ISO sessions (3–66). The first
session is the initial decision date; 1–64 consecutive opens follow, with a final
calendar session reserved for T+1. Every order names its immediately prior
calendar decision session, execution session, nonempty owner and ticker, BUY or
SELL, and positive absolute integer shares. Tuple order is binding priority;
there is no sorting within a session, resizing, netting or implicit liquidation.
At most 4,096 orders are accepted. Weekends/holidays are caller-supplied session
calendar responsibilities, not inferred by this executor.

One tape represents one funded cash bank. Owners attribute inventory and
receivables in that bank; the same ticker may have multiple owners. Ownership
keys are exact opaque strings (production callers should encode family and
chromosome). No position has two owners, and orders cannot consume another
owner's shares. Segregated shadow portfolios require separate tapes with their
own explicit funding. Repeated orders are separate instructions, not deduplicated.

Opening positions include integer shares, raw weighted entry, fee-inclusive
per-share basis, completed-open age and peak. BUY adds weighted raw/basis costs,
preserves incumbent age and updates peak. SELL retains these attributes on
remaining shares; full exit removes the position. At each MARK, age increments
once and peak includes that open. This age/peak convention is research state,
not a claim that it matches every native close/held policy. Initial over-cap
holdings may be reduced; capacity only rejects new buys.

All opening receivables due that session settle first, in input order. Every
sale creates a net-of-fee receivable due the next calendar session, unavailable
for that opening batch. Buys debit gross plus proportional fee immediately.
No borrowing, interest, shorting, partial fills, dividends, splits, identity
changes or terminal liquidation are supported. Cash, inventory and a declared
aggregate share-count ceiling are the only execution capacity constraints;
sector, utility, risk and eligibility belong upstream. Insufficient capacity,
cash or owner inventory rejects the entire order and leaves state unchanged.
Later smaller orders can still fill. Structural/input failures reject the entire
tape before either engine creates mutable state.

Each open requires exact price and explicit no-action coverage for every initial
holding and every ticker ordered through that date, including rejected/closed
names. The coverage assertion is the caller's responsibility; it is not source
certification. Any declared corporate action is rejected. Missing coverage,
nonfinite/nonpositive prices, duplicate prices, non-open observation dates,
invalid dates, unsupported operations and malformed state fail closed. Prices
are declared contemporaneous opens: a label cannot prove their provenance.
No future close is consumed. Both executors emit ordered settlements, fills,
rejections and MARK snapshots with cash, dated receivables, owner positions,
price, fee and open-marked NAV. REJECT shares are requested shares, never fills.
The last open can leave receivables outstanding; its reserved settlement tail
is not automatically executed or silently liquidated.

`native_style_share_executor.execute` is an independent native-style integer
reference, not an extension of native replay_requests. `funded_share_executor.execute`
is an independent fixed-share funded-shadow bridge, not the legacy target-weight
FundedShadow policy. They share immutable records, prevalidation and output
formatting only. Inventory, cash, fee, settlement, basis, age/peak and NAV
calculations are separate. Neither calls the other or consumes its output.
Native endogenous replay and strategy equivalence remain BLOCKED.

Phase 9 adds `ga7_native_share_adapter.execute` as a **research-only native-adjacent
experiment**, not a third exact v1 implementation or authentic replay extension.
It compiles hash-locked native fill/account statement slices without replacing
their float arithmetic. Workspace code supplies the external quantity, opening
state, owner isolation, feasibility, settlement and open metadata. Comparisons
against the two Decimal consumers use an explicit absolute 1e-10 fixture tolerance.
A tested cash boundary (three shares at Decimal 0.1 with cash 0.3) fills in v1
but rejects with native floats. Exact v1/native parity therefore remains BLOCKED;
no tolerance or admission rule in this contract has been relaxed. Native replay's
endogenous policy, sizing, outcome ledger and terminal liquidation remain separate.
