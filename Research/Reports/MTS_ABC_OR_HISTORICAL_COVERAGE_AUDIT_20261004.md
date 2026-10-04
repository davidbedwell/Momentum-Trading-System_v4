# MTS v4 — A∨B∨C Historical Coverage Audit — 2026-10-04

## Status

**PAUSE / BLOCKING DISCREPANCY IDENTIFIED. DO NOT PROCEED TO R-1 INTEGRATION YET.**

This audit implements the governance requirement that A, B, and C operate concurrently as independent market-wide deterioration detectors:

```
A OR B OR C -> DEFENSIVE
```

A/B/C were motivated/developed from different historical deterioration morphologies. They are not mutually exclusive crash labels and are not assigned to future crashes in advance. All operational detectors must watch the market simultaneously.

If a known destructive reference episode escapes all three detectors early enough to be useful, integrated development pauses and the miss must be explained before recovery/R-1 integration proceeds.

## Evidence boundary

No preserved-50, remaining Discovery, Verification A, or Verification B evidence was accessed for this audit.

Sources are surviving original protocols/reports from the already-consumed crash/deterioration research.

## Reference destructive episodes

The surviving multi-market / slow-bear detector research explicitly uses:
- 2008: peak 2007-10-09, reference trough 2009-03-09
- 2020: peak 2020-02-19, reference trough 2020-03-23
- 2022: peak 2022-01-03, reference trough 2022-10-12

2015 is treated as an elevated/hard control rather than a required systemic-crash positive in the later market-wide classifier work.

## Path definitions

### A — FAST_SHOCK_SYSTEMIC

Intended morphology:
- rapid drawdown / shock velocity
- 1/5-day loss acceleration
- extreme-move clustering
- VIX/VVIX stress
- breadth collapse velocity
- funding/credit/volatility acceleration
- cross-market concurrence

Operational intent: rare, high-specificity declaration with short confirmation.

### B — SLOW_BEAR_DETERIORATION

Intended morphology:
- persistent internal deterioration
- breadth damage/non-recovery
- failed rebounds
- negative-day persistence
- lagged funding/credit deterioration

Operational intent: recognize slower destructive deterioration before conventional MA confirmation.

### C — GRINDING/PERSISTENT DETERIORATION

Frozen Group-C rule:
- negfrac20
- failed30
- negfrac40
- fundingchg30
- all four >= causal rolling historical 90th percentile
- 4/4 confluence
- 3-session confirmation
- OFR Funding lagged two business days

C is explicitly not a general crash detector.

## Historical coverage

| Episode | A evidence | B evidence | C evidence | Earliest supported useful declaration | Audit status |
|---|---|---|---|---|---|
| 2008 | Later fast-A LOCO heldout detection 2008-01-02 (58 sessions in), not the preferred path | Held-out B declaration 2007-11-26, 33 sessions after 2007-10-09 peak | 2008-10-24, explicitly too late | B: 2007-11-26 | COVERED BY OR |
| 2020 | Old DEV50 COVID emergency architecture fired 2020-03-06, before the severe 3/6→3/23 leg; later independent market-wide fast-A LOCO formulation missed held-out 2020 | Slow detector variants recognize only very late in the crash (e.g. 2020-03-20 in later slow/MA work); not adequate substitute for fast A | Not established as useful 2020 path | **Disputed: old A-like signal exists, later market-wide A fails to reproduce it** | **BLOCKING DISCREPANCY** |
| 2022 | Later fast-A LOCO misses held-out 2022 | Held-out B fold declares 2022-01-25, 15 sessions after peak | Frozen C declares 2022-01-25, 15 sessions after peak | B/C: 2022-01-25 | COVERED BY OR |

## Critical interpretation

The 2020 result must not be misrepresented in either direction.

It is incorrect to say:
- “A/B/C missed 2020” without qualification, because the earlier COVID emergency architecture did identify a causal 2020-03-06 emergency condition.

It is also incorrect to say:
- “Path A is validated for 2020,” because that earlier rule was developed in the DEV50 crash-management architecture, while the later independent market-wide fast-A LOCO formulation failed to detect held-out 2020.

Therefore the operational A∨B∨C architecture is **not yet certifiable**.

## Required investigation before progression

Pause R-1 integration and determine why the COVID signal failed to transport from the earlier DEV50 emergency architecture into the later market-wide Path-A formulation.

Required questions:

1. What exact causal features constituted the old 2020 emergency signature?
2. Were those features stock-laboratory aggregates that should have been replaced by full-market analogues?
3. Did the later market-wide A search change the episode start/peak definition (notably 2020-02-19 versus the old crash-management 2020-03-06 reference)?
4. Did leave-crisis-out training force a rule learned from 2008/2022 morphologies that is structurally incapable of recognizing a COVID-style exogenous shock?
5. Did feature availability, VIX/VVIX history, OFR publication lag, current-S&P survivorship qualification, or threshold normalization materially alter the 2020 state?
6. Was the later A objective asking for one portable universal fast-shock rule when the scientific architecture actually permits a sparse high-specificity COVID-like shock mechanism alongside B and C?
7. Can an independently motivated, causally specified market-wide analogue of the old COVID signature be defined without using portfolio return/CAGR/wealth fitness?
8. Does that analogue have an acceptable all-history false-alert burden?
9. Does it detect 2020 while remaining causally valid and without protected evidence?
10. Does it create any new failure in 2008/2022 or ordinary corrections when all three detectors operate concurrently?

## Governance during A investigation

Allowed:
- public/full-market causal history already admitted by the frozen detector protocols
- surviving consumed crash research
- VIX/VVIX/OFR data already assembled under causal publication rules
- deterministic analysis of detector behavior and false-alert burden
- comparison of old DEV50 feature definitions to market-wide analogues for provenance/mechanism understanding

Prohibited:
- portfolio CAGR/terminal wealth optimization
- tuning A to preserved-50 outcomes
- accessing preserved 50 for this investigation
- accessing remaining untouched Discovery
- accessing Verification A/B
- weakening B or C to compensate for A
- using future trough knowledge as an operational feature
- declaring R-1 research complete before this blocking discrepancy is resolved

## Advancement gate

A investigation may advance only when one of the following is scientifically established:

### PASS
A causal market-wide Path-A rule is frozen that detects the 2020 fast-shock deterioration early enough to leave material downside remaining, with a documented and acceptable false-alert burden.

### EXPLAINED LIMITATION
Evidence demonstrates that no defensible pre-crash market-wide A declaration was causally available under the admitted feature set. The architecture may proceed only if the limitation is explicitly accepted and the expected failure mode is documented.

### ARCHITECTURE REVISION REQUIRED
The miss reveals a distinct deterioration mechanism not represented by A/B/C. Pause and preregister the new mechanism before further integrated testing. Do not create a new path merely to fit 2020.

## Current conclusion

2008 and 2022 are covered by the Boolean-OR architecture using surviving causal B/C results.

2020 exposes a provenance/transport discrepancy between an earlier DEV50 COVID emergency signal and the later independent market-wide fast-A detector.

**R-1 integration is paused. Resolve Path A / 2020 first.**
