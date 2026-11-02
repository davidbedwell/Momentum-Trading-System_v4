# Phase 7 engineering report

2026-10-28; branch `codex/first-year-manager`; starting commit `0d5027c`.

**BLOCKED / NOT FOUR-FAMILY LAUNCH READY.** This phase narrows the original
native/shadow discrepancy with observed native daily state and reproducible
ordered event tapes. It does not establish policy equivalence, an endogenous gap
attribution, or a general common-request adapter. No proof observations were
opened, no market evidence invented, and no push, merge, brokerage action, full
GA, paid compute or external-source write occurred.

## Reproduction and first divergence

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m discovery.competitive_ga.phase7_diagnostics
```

`PHASE7_DIAGNOSTICS.json` contains the 32 dated session events on the exact
500-name Phase 5 panel, 2022-11-17–2022-12-30. It verifies Phase 5 source hashes,
uses the unchanged predicate-bounded loader, and records the native implementation
hash. No selection, fitting or proof decoding occurs. Full-file byte hashing
establishes identity only. The existing 393-session permission and 867-session
seal remain intact. Cached features and raw values are filtered through
2022-12-30 before use.

A temporary Python trace hook observes only the selected native replay function,
at its unique pre-NAV source anchor. It copies cash, outstanding receivables and
actual native holdings before final liquidation; it does not modify native code,
requests, fills or locals. Unknown anchors or an existing trace hook fail closed;
the hook is restored in `finally`. This observational contract is version scoped,
not a stable native event API. The separate Phase 6 fixed-request interpreter
matches observed native cash, receivables, share positions and marked NAV on
**all 32 sessions**, maximum dollar residual **0**. This is stronger than terminal
parity but still does not observe every native internal event or certify its
policy. Native ordered opening fills are independently reconstructed by that
interpreter, rather than falsely described as a native fill export.

The shadow path reproduces **601 fills**, terminal marked NAV
**95,856.81920838593**, and independent journal reconstruction across 32
owner-sessions, maximum residual **1.0186340659856796e-10**. Native marked NAV is
98,615.13150068247; shadow minus native is **-$2,758.3122922965413**. Native
terminal liquidation fees remain $8.9496914856; liquidation does not explain it.

| Event | First difference / evidence |
| --- | --- |
| Initial candidates, dated inputs, signal/action | 2022-11-17: both flat, $100,000 settled, 299 ENTER candidates; same shared panel and native signal callback |
| Request priority | 2022-11-17 close: native first `STK_0326`, shadow first `STK_0001` |
| Next-open execution | 2022-11-18: native first buys 11 `STK_0326` at 327.80578422024576, fee 3.6058636264227033; shadow first buys 45.13234471812881 `STK_0001` at 85.7931813702819, fee 3.87204743606851 |
| State after first opening batch | Native 3 holdings, cash 89,004.79158619516; shadow 26 holdings, cash approximately zero. Fees 10.984224189615217 versus 99.9000999000999 |
| Endogenous policy inputs and decisions | 2022-11-18 close: native is flat in `STK_0001` and emits ENTER; shadow owns it and emits EXIT. First candidate-set divergence is this close |

The artifact preserves every dated candidate action, active/zero request amount,
priority inputs, required ranked features, eligibility, sectors, signal boolean,
native position state, shadow pre-open and after-open state, integer/fractional
fills and fees, cash, receivables, capacity conventions and closing NAV. It records
the opening sizing conventions explicitly. Native held entry/age/stop and shadow
held entry/age/weight are separate. After-open holdings precede the next close's
decisions; the previous event provides pre-open native holdings. No terminal
close sale is conflated with a next-open signal fill.

Interpretation: the first discrepancy is execution priority with different
sizing/capacity conventions, before any observed held-state policy disagreement.
The first execution batch then creates different policy inputs. Both use the
same flat signal on the same required features; this does **not** establish equal
held policies (the adapter also guards ADD at the 30% weight cap). Native sizing
uses integers, a stop budget, sequential settled equity and utility priority;
shadow uses fractional shares, alphabetic priority and prior-close weight targets
against opening NAV including receivables. Capacity and sector limits differ.
These are explicit contracts, not a demonstrated native cash-accounting defect.
Priority, capacity and sizing effects interact. No new waterfall is asserted;
Phase 6 fixed-request sensitivities remain fixed-tape, path-dependent measures,
not an attribution of this endogenous gap.

## Common-request boundary and precise blocker

`common_request` exposes only identical-meaning EXIT-to-zero and non-rebalancing
HOLD semantics, conditional on identical opening holdings. It rejects ENTER,
INCREASE/ADD, REDUCE, target-bearing HOLD and malformed EXIT with a precise
share-order-interface error. It is a semantic boundary, **not a completed dual
ledger execution adapter**. No fallback, target-weight rounding trick or native
fill-as-oracle comparison is presented as independent parity.

The native replay internally generates its requests and has no opening-holdings
or external-share-request argument. The independent Phase 6 interpreter accepts
frozen native weight requests but only empty opening holdings. FundedShadow
accepts target weights and fractional shares, without native priority/capacity/
stop-budget semantics. Therefore feeding the actual endogenous tape identically
to both native and funded ledgers is unsupported by the existing interfaces.

Smallest safe next implementation: a versioned request carrying decision date,
execution session, owner, ticker, side and explicit integer share quantity, with
explicit opening cash, shares, raw entry/basis and dated receivables. Both
independent engines must accept it without re-sizing and export ordered fills,
settlements and post-event state. Keep policy sizing upstream and independently
check settled-cash feasibility, position conservation, fees and marks. Alternatively
provide an approved identical sizing/priority policy in both engines; this is a
larger contract change. Reject unsupported corporate actions and incomplete held
coverage before mutation. This work requires a native API extension and remains
unfinished; the safe boundary and tests do not remove that blocker.

## Bounded read-only source investigation

Beyond filename discovery, inspected the actual Arrow schemas and schema metadata
of all three universe-1 source tables, without decoding additional market values:

- Stock prices: Date/Close/Volume/Sector/Ticker/Regime/Open/High/Low.
- Market index: Date/Close/Volatility/Regime/Volume/Open/High/Low/Quarter.
- Fundamentals: Date/Ticker/Sector/Revenue/EBITDA/NetIncome/EPS/Debt/RegimeEnv.
- Only pandas metadata keys were present. These observations establish these
  table schemas, not global absence of source data. EPS observations are not an
  earnings publication or absence-coverage contract. Sector is not a certified
  correlated-stress-group assignment. Regime labels are not used as observations.

Read the lab research protocol's timestamp/publication and sealed-latent-state
requirements and bounded textual references in its batch/source modules. No
simulator parameters or latent states were supplied to the learner. Did not read
external research outcome reports, fit an alternative stress proxy, or run source
scripts. The protocol requires observable dated controls; their existence as a
requirement is not evidence that the supplied panel implements them.

Re-read GA7 `niche_pit_manifest.json`: still
`CHRONOLOGY_VERIFIED_FEATURE_PROVENANCE_PENDING`, with explicit uncertified source
PIT provenance; real-market 2009–2026 coverage does not link those models to
fictional synthetic identities. Re-read authorized GA4 horizon contract and
`gen1_sequential_exit.py` with elevated read-only access after ordinary access was
denied. Horizon observation still does not imply a fixed holding exit; the
counterfactual evaluator still accepts a caller exit policy and forces terminal
horizon liquidation. Neither supplies approved frozen-bank exit linkage.

This was a bounded schema/contract investigation, not an exhaustive archive hunt.
Earlier recovered historical VIX/VVIX/OFR sources remain inventory evidence only;
no new joint synthetic Horizons or publication/normalization contract was found
in the inspected scope. Absence of filename matches is not the conclusion.

## Minimal launch readiness matrix

| Gate | Evidence now | Required source or engineering work |
| --- | --- | --- |
| Permitted feature prefix | Prior 393-session parity preserved; this diagnostic uses 32 sessions/500 names | Approved research chronology and verified model training cutoff per identity |
| Native/funded ledger | Native daily bridge reconciles; original shadow separately reconciles | Explicit common share-order/opening-state API; independent per-event reconciliation under common requests |
| Corporate actions/settlement | Adjusted-price, ex-date dividend and research T+1 assumptions only | Security identity, split/adjustment convention, event/pay-date tape and governed settlement contract |
| Risk/defense/group/gaps | No authenticated dated synthetic input supplied by inspected tables | Dated observable stop/gap estimates, reference prices, group assignments, risk budgets and defense publications; causal open/close timing contract |
| Eligibility/earnings/niches | All-true eligibility is diagnostic; PIT manifest provenance pending | Dated membership, schedule/publication and explicit no-event coverage, native embargo version, synthetic niche mapping/model provenance |
| GA4 held exits | Hook and counterfactual infrastructure only | Approved executable exit policy with immutable frozen-bank linkage and held-state tests |
| Horizons | Historical stress inventory only | Joint synthetic scenario identity, VIX/VVIX/funding/credit trajectory, publication chronology and approved normalization |
| Held scaling/validation | Existing fixture tests and Phase 5 utility probes; zero empirical ADD probes | Independently matured action utility and fold evidence, risk-controlled actual cross-family prefix replay, frozen validation |
| Four-family launch | **BLOCKED** | All above; untouched proof remains sealed pending separate authority |

Priority 4 actual cross-family manager extension was not attempted with fabricated
controls. Existing Phase 6 fixture integration remains fixture evidence only.

## Validation and local delivery

Final required bounded suite:

```bash
PYTHONDONTWRITEBYTECODE=1 /opt/mts/.venv/bin/python -m pytest --import-mode=importlib -q tests discovery/competitive_ga/test_*.py
git diff --check
```

**423 passed in 4.50 seconds**, no skips or failures, using read-only elevated
access for existing native archive imports; diff check passed. Twelve new tests
exercise ordered/payload/missing-event first divergence, strict unsupported
semantics, source-anchor rejection, native observation against a hand-calculated
99-share buy/exit/T+1 dollar oracle, trace restoration, and an actual native versus
funded fixture where higher utility selects B while shadow buys A first. Fixtures
are not market evidence. Development caught and corrected a dict-versus-object
request representation error; the final diagnostic and suite pass. The runtime
skill environment-status tool is unavailable; no network or credential discovery
was performed. The final artifact uses strict JSON (nonfinite values rejected).

Changes and evidence are committed locally on the requested feature branch.
Main and external research sources remain unchanged. No push or merge performed.
