# MTS v4 — Momentum Stage-Role Audit Protocol — 2026-10-02

## Question
At what stage of an MTS trade does momentum contain useful information: entry eligibility/selection, continued holding, or exit timing?

## Governance
Development/mechanism audit only. Use already-consumed Discovery research rows. Do not access remaining Discovery, Verification A, or Verification B. Analysis Engine performs calculations only; interpretation remains external. Freeze protocol before results.

## Momentum measurements
All measurements must use information available at the measurement close:
- absolute price returns: 5, 10, 20, 60 sessions
- acceleration: recent 5-session return minus preceding 15-session rate-equivalent return; 10-session minus preceding 20-session rate-equivalent return
- SMA structure: close above SMA20/50; SMA20/50 five-session slope
- distance from rolling 20/60-session high
- volume-confirmed momentum: 20-session return conditional on volume vs trailing 20-session mean
- relative momentum where a causal same-date cross-sectional comparison is available.

No single definition is privileged.

## Stage A — Entry
At the signal/entry decision, measure each momentum variable causally. Compare subsequent frozen MTS trade return, win probability, downside tail, and >=1.5 ATR success across quantiles/states. Test momentum as:
1. eligibility filter,
2. rank/selection information,
3. interaction with existing MTS family/genome.

## Stage B — Hold / confirmation
For trades still alive at +5, +10, and +20 sessions, recompute momentum using only bars known at that checkpoint. From each checkpoint measure remaining return to the original frozen exit and forward 5/10-session path outcomes where available. Compare persistent/rising momentum, flat momentum, and deterioration. This is a conditional survivor analysis; sample counts and horizon availability must be reported.

## Stage C — Exit
At +5, +10, and +20 sessions while a trade remains alive, test whether momentum deterioration predicts worse remaining return/tail risk. Also simulate simple causal early-exit rules triggered by prespecified deterioration states and compare them with the original frozen exit. No rule may use future bars to trigger.

## Controls and robustness
Report results overall and by year/era, family, and ticker breadth where sample permits. Avoid declaring usefulness from pooled mean alone. Require directionally coherent evidence across multiple periods/groups before interpreting a role as supported.

## Interpretation
Possible outcomes include entry-only, hold-only, exit-only, multiple-stage, definition-specific, interaction-only, or no useful momentum role. Do not force momentum into MTS.

## Evidence boundary
No virgin/untouched evidence is opened by this audit. Any mechanism selected for prospective validation must be frozen before sealed evidence is accessed.
