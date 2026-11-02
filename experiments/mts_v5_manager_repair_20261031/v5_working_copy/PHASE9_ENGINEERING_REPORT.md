# Phase 9 engineering report

2026-10-28; branch `codex/first-year-manager`; starting commit `228a4bc`.

**BLOCKED / NOT FOUR-FAMILY LAUNCH READY. Native external-order and endogenous
parity remain BLOCKED.** This phase executes selected original GA7 accounting
statements in a workspace research adapter and observes actual ordered fills in
the unchanged native replay. Neither the adapter nor fixture agreement is labeled
an authentic native fixed-order engine. All earlier launch blockers remain.

## Exact native semantics and smallest workspace seam

Read `FIRST_YEAR_AGENT_REPORT.md`, Phase 2–8 reports and `FIXED_SHARE_CONTRACT.md`;
inspected the actual read-only GA7 replay, account, proposal, priority and outcome
ledger sources. `ga7_native_kernels.py` pins SHA256 for all five sources. Replay
SHA256 is `efc9fa9d2ea39d2e3f5d247b402cdc1ebadf40b9954830568c910b1a3e5bc375`;
account SHA256 is `26038bc3db8345e10c4c263b0b7a3030677cde2752540fb6b0bfedc7549de757`.
The evidence JSON retains all five digests. Unknown source bytes fail closed.

Native `replay_requests` initializes empty ticker-keyed positions/receivables,
generates its own close proposals, and internally sorts and sizes next-open fills.
Priority is action, descending uncalibrated utility, confidence, ticker and owner.
EXIT sells all; REDUCE sells `max(1, shares//2)`; INCREASE spends an incremental
request subject to cash, 30% name exposure and stop budget. ENTER uses settled
cash plus opening holdings as sizing equity (excluding receivables), integer
rounding, genome capacity, three positions per sector and a 2% stop-risk budget.
Buy fees enter cost; sells create net T+1 receivables; interest precedes settlement.
Native adjusted-price/ex-date-dividend, close peak/low and terminal close-sale
conventions are distinct from fixed-shares-v1. Native buy gating checks both
current and previous defense flags; this diagnostic has both false, and does not
certify general defense publication causality.

`ga7_native_kernels.load()` compiles unchanged AST statement slices from the
hash-verified source, preserving native float arithmetic and `TradeAccount`:

- EXIT: original replay lines 100–103, including native `account.finish`.
- REDUCE: lines 110 and 112–120, including native cost allocation and
  `account.sell`; line 111's endogenous half sizing is excluded.
- ADD: lines 136–142, including cash, shares, cost, `account.buy` and raw entry.
- ENTER: lines 149–154, including native Position and TradeAccount construction.

No reference executor is imported or called. No native file/function/frame local
is patched. This is extracted native arithmetic, **not the entire native replay**.
`ga7_native_share_adapter.execute(Tape)` supplies explicit integer quantities,
nonempty opening cash/positions/receivables, owner/ticker keys, all-or-none cash
and share capacity checks, T+1 release, open marks, v1 age/peak and event formatting.
Full sales use the EXIT kernel rather than native's one-share REDUCE completion
branch. Native policy sizing, niche counts, completion metrics, outcome-ledger
settlement and terminal liquidation are deliberately not claimed by this adapter.

Imported native accounts start from remaining fee basis, using a research .02
stop solely to make native account arithmetic executable. They cannot recover
prior cumulative investment, realized P&L or risk capital from v1 opening state;
no historical return/R metric is exposed or certified. Original replay remains
untouched and retains its endogenous behavior. An approved native API extension
and richer accounting-state/numeric contract are still required for exact parity.

A concrete numeric blocker is retained as a regression: three shares at Decimal
0.1 with cash 0.3 fill in both exact v1 consumers, but native float cost exceeds
float cash and the adapter rejects. Underflow/overflow input ranges fail closed.
No Decimal rounding, reference-account substitution or weakened v1 tolerance
conceals this discrepancy. The contract documentation now states this limitation.

## Hand-calculated and independent fixture evidence

`test_phase9_native_adapter.py` adds **28 tests**. Fixtures span 2–8 execution
opens, with preexisting same-ticker positions owned by different chromosomes,
raw/basis/age/peak state, opening receivables, ADD, partial REDUCE, EXIT, inventory,
cash and capacity rejection, binding priority reversal and changing prices/fees.
Every event's identity/order, cash, receivables, shares, basis, age, peak, price,
fee and NAV is compared against **both** independent Phase 8 consumers. Numeric
comparison is explicitly an absolute 1e-10 fixture tolerance, not exact v1 parity.
Existing exact Decimal tests remain unchanged.

One hand oracle starts with cash 20, a due receivable 1, and two owners holding
2 A shares each at an open of 10. ADD costs 10.10; another owner's REDUCE nets
9.90 into T+1. First MARK cash/NAV are 10.90/60.80. At the next open that 9.90
settles; EXIT nets 29.70 still unavailable; buying 2 B costs 20.20 from settled
cash. Second MARK cash/NAV are 0.60/60.30. Aggregate fees are 0.70. A separate
priority fixture proves sale proceeds cannot finance same-open buys and reversing
two otherwise feasible buy priorities reverses the funded owner. Both references
independently reproduce these observations.

A direct native-account oracle begins with cost 16.20, adds 10.10, partially sells
for 11.88, then exits for 17.82: native finish profit is 3.40 on 26.30 invested.
Original-replay fixtures separately observe ENTER 999, INCREASE 275, REDUCE 637
and EXIT 637 shares without changing native results or requests. Tests cover
trace restoration on exceptions and rejection of an existing trace hook.

Missing/incorrect dates, future observation labels, incomplete price/event
coverage and declared corporate actions in a late open reject the **whole** tape
before loading native kernels or constructing state. Source drift is rejected.
Fixture provenance labels remain assertions, not supplied market controls.

## Actual native journal and bounded gap measurements

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m discovery.competitive_ga.phase9_diagnostics
```

`ga7_native_journal.observe` installs a read-only trace on the **original** native
function at proposal boundaries, sizing sites and the pre-close-mark anchor.
Before/after native cash, receivables, inventory and TradeAccount state expose
actual ordered inventory changes, execution prices and associated proportional
fees. Reached native sizing sites expose actual equity and budget. HOLD/PASS and
unfilled requests remain NO_FILL observations, not invented rejection reasons.
The trace is restored in `finally`; existing hooks/unknown versions are refused.
Terminal liquidation remains outside this next-open journal.

`PHASE9_DIAGNOSTICS.json` pins the Phase 7 artifact identity and source hashes,
then reuses the unchanged predicate-bounded loader for exactly **32 sessions,
500 names, 2022-11-17–2022-12-30**, within the authorized 393-session prefix.
No new identity search, model fitting, GA run, forward controls or proof decoding
occurs. The retained Phase 7 shadow journal supplies its previously audited
independent path; it is not regenerated from native fills or used as a policy
oracle. Full-file byte hashes identify sources without decoding proof values.

The new original-native observations contain 15,500 ordered requests, **94 actual
opening fills**, 9,134 unfilled ENTERs, 6,231 PASS and 41 HOLD observations. All
ordered opening fills and all 32 daily cash/receivable/share/NAV observations
match Phase 7's independent reconstruction with **maximum residual 0**. This
advances the earlier evidence from reconstructed fills to actual native execution
observations. It still does not provide an external-order native API.

First-choice evidence is preserved and now observed directly: 299 initial ENTER
candidates; native first `STK_0326`, shadow first `STK_0001`. On 2022-11-18 native
sizes from equity 100,000 and budget 3,872.04743606851, buys 11 at
327.80578422024576, fee 3.6058636264227033. Shadow buys 45.13234471812881 of
STK_0001 at 85.7931813702819, fee 3.87204743606851. The first batch has 3 versus
26 fills. Subsequent held decisions depend on these different holdings; Phase
7's next-close STK_0001 ENTER versus EXIT remains a state-conditioned difference.
Neither observed fill stream is an independent policy oracle for the other.

An independent share/price mark identity decomposes each path's daily NAV change
into prior holdings' close-to-open P&L, after-fill holdings' open-to-close P&L,
and fees. It uses actual native inventory and retained shadow inventory, rather
than either engine's cash computation. Maximum daily accumulated NAV residual
is **7.28e-11**. For shadow minus native:

| Descriptive component | Dollars |
| --- | ---: |
| Close-to-open marked P&L difference on observed held paths | 0.0000000000 |
| Open-to-close marked P&L difference on observed held paths | -1,053.6385421990 |
| Additional shadow fees, subtracted from NAV | 1,704.6737500976 |
| Marked NAV difference | **-2,758.3122922965** |

Native opening fees total 314.1000934363; shadow fees total 2,018.7738435339.
Native settlement credits observed between prior mark and first opening request
total 151,887.7769556207. Shadow settlement reconstructed from its net-sale
journal less remaining receivables totals 947,373.9267583477. Under this zero-yield,
no-dividend diagnostic, settlement transfers receivable to cash and contributes
**zero directly to NAV**, while changing later buying feasibility. Terminal native
liquidation fee 8.9496914856 remains outside the marked comparison.

This is a complete **descriptive accounting identity**, not a causal waterfall.
Separate dollar effects of first-choice selection, utility priority, integer/stop
sizing, capacity, held policy changes and their interactions remain **unmeasured**.
They require independently governed policy interventions with decisions recomputed
on each resulting held path. Changing one convention on a native fixed request
tape is still not that experiment. Certified event, membership/earnings, niche,
lineage, risk and defense controls remain unavailable; the current diagnostic
cannot make those causal experiments authentic or certify their investability.

## Preserved blockers and next bounded step

All earlier launch blockers survive, including:

- Native external-order/opening-state API, numeric convention, complete native
  account/outcome state, native endogenous/held-policy parity and independent
  corporate-action/security/adjustment/pay-date/settlement certification.
- Dated PIT membership, earnings schedule/absence/publication coverage, selected
  native embargo version, synthetic niche mapping and verified model training
  cutoffs; source hashes establish none of these.
- Authentic dated risk/defense/gap/stop/reference/group inputs, incumbent aggregate
  constraints and causal timing. No synthetic controls were invented.
- Approved frozen-bank-linked GA4 held exits; observation horizons and research
  exit evaluators do not supply that policy. GA4 funded enablement remains gated.
- Jointly compatible Horizons stress, publication and normalization contracts;
  historical VIX/VVIX/OFR overlap is still not synthetic joint provenance.
- Independently matured ADD/REDUCE utilities, fold evidence, boundary/long-held
  coverage, genuine four-family fitness and frozen chronological validation.
- The 867-session proof beginning 2023-07-03 stays sealed. No proof evaluation,
  full GA or four-family launch is authorized or reported.

Next bounded step: have the native source owner supply an approved versioned
fixed-order/opening-state API in a separately authorized native version, preserving
`replay_requests` defaults and exposing ordered fill/account/outcome snapshots.
Specify floats versus exact Decimal money and complete opening account history
explicitly. Re-run these small fixtures against that full native path and both
references before extending any permitted-prefix comparison. Until then keep
this extraction research-only. Governing upstream policy/control provenance is
a separate prerequisite for causal sizing/priority interventions or manager runs.

## Validation and local delivery

Required full bounded command:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
git diff --check
```

Final full-suite result recorded after the last fixture additions: **503 passed**,
no failures or skips. Read-only elevated access is needed for existing native
archive imports. The ordinary-sandbox attempt had the same three archive-access
failures and one access-driven skip documented in prior phases; no tests were
weakened or bypassed. The bounded actual-source diagnostic completed and wrote
strict JSON (nonfinite values rejected). Diff check passed.

Cloud runtime skill was read; its environment-status tool is unavailable. No
network, external service or credential discovery was used. All changes are
local on the requested branch. No main modification, push, merge, brokerage
order, paid operation or write to `/opt/mts` sources/archives/data occurred.
