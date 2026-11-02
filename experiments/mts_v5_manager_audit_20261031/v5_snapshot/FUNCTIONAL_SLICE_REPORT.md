# Bounded first-year manager functionality slice

Implemented `discovery.competitive_ga.functional_niche_manager.run_slice` as an
independent research functionality baseline. Existing certified-input and
calibration gates are unchanged. GA4 is abandoned for trading in this slice:
it is neither required nor funded and remains research-only.

## What works

- A streaming 2–64 session, at most 32 stock / 32 chromosome replay, with no file,
  network, GA, broker or paid-service calls.
- Dated native-classifier observations are accepted without inventing features
  or memberships. Overlaps resolve to the smallest supplied native center
  distance; exact ties resolve by niche identity. Empty matches explicitly mean
  no niche. Stale observations, future/same-day model training, duplicate matches
  and invalid distances fail closed.
- Existing `hierarchical_search.tier` routes niche and non-niche eligibility;
  the caller's native chromosome feature/universe gate must explicitly pass.
  Every routed eligible entry chromosome competes. Existing deterministic
  `synthetic_entry_competition.choose` supplies a cold-start fairness baseline;
  native scores with different units are never compared as expected returns.
- A single funded `Replay` bank reserves settled cash across stocks, charges
  fees, executes only at the following open, and delays sale settlement one
  session. Stock allocation order is deterministic ticker order, not a learned
  opportunity ranking. Entries/adds stay inside the ordinary 10% cap.
- `FillBook` attributes ownership and updates executed average entry, basis,
  shares, peak and realized P&L. Only the filled owner manages an incumbent,
  including after entry eligibility or niche membership disappears. HOLD emits
  no rebalance; native ADD, REDUCE and EXIT become next-open targets. Final-close
  pending orders and unsettled receivables remain visible, without forced fills.
- A six-session explicit synthetic test fixture calls the existing GA7 native
  daily producer: two eligible chromosomes compete, another niche is excluded,
  and a blocked chromosome is excluded. It produces ENTER/HOLD/ADD/REDUCE/EXIT,
  four fills, final NAV **99,700.79156292375**, realized P&L **-299.2084370762391**,
  no final holdings, one pending entry and **3,598.2426534516744** unsettled.
  These are test-fixture results, not measured trading performance.

## Missing dependencies and limits

The native niche classifier/model artifacts, native center-distance observations,
archived eligible chromosomes and causally computed native feature panels are
not bundled in this checkout. This pass does **not** execute that external
classifier or claim to reproduce its distance formula. Its callback consumes
native results; overlap resolution and downstream integration are tested using
clearly marked synthetic fixtures. No fabricated observations, genome lineage,
features or calibration are represented as authentic inputs.

The public callbacks receive today's cutoff and filled state; callers must enforce
that cutoff in source queries. Prefix replay equality is tested, but caller data
provenance is not certified. The GA7 fixture genome is hand-authored test data,
not an archived learned chromosome. GA6/HORIZONS native callbacks are supported
by the boundary but were not exercised end to end. No learned manager utility,
funded shadow learning, evidence-based scaling above 10%, full-year archived replay,
corporate-action certification, aggregate risk/earnings/defense integration,
broker parity or launch certification is claimed. GA4 is not a missing trading
dependency or launch blocker.

## Validation

- `python3 -m unittest discover -s tests -p test_functional_niche_manager.py -v`: 7 passed.
  Covers lifecycle, overlap/ties, gates, prefix causality, funding under 16-stock
  contention, ownership after eligibility loss, invalid chronology, and GA4 exclusion.
- `python3 -m unittest discovery.competitive_ga.test_hierarchical_search discovery.competitive_ga.test_manager_policy_v3 -v`: 6 passed.
- `git diff --check`: passed.

The environment lacks pytest; no packages were installed. An initial unittest
file-discovery invocation of the existing V3 tests failed on relative imports;
rerunning with its package-qualified module succeeded. No `/opt/mts` data, live
trading, sealed 867-session proof or main branch was accessed or changed.

Local commit was attempted on `codex/first-year-manager`, but `git add` failed:
`Unable to create .../.git/index.lock: Read-only file system`. The session explicitly
mounts `.git` read-only and does not permit approval escalation. All three new
files remain untracked for review; no commit, push or merge occurred. Whitespace
checks also ran with `git diff --no-index --check /dev/null <file>` for each new
file so untracked content was covered.
