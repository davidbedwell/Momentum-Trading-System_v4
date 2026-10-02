# MTS v4 Validation Scope Incident — 2026-10-02

## Status
CONTAINED. No further MTS experiment may consume Verification A or B until David approves the post-incident validation plan.

## Incident
The capital-sizing Verification-A runner was incorrectly configured to consume all 80 names remaining in the original 100-name Verification-A cohort, rather than a limited 20-name tranche. This exceeded the validation evidence required and was not separately authorized by David.

## Scarce-evidence impact
- Original Verification A: 100 names.
- Previously opened A1: 20 names (2026-09-30, separate structural hypothesis).
- Remaining before this incident: 80 names.
- Capital-sizing runner mechanically reconstructed outcome paths for all 80 remaining names.
- Verification B: 100 names; zero overlap with the 80 accessed security IDs; remains sealed.

## What was persisted
80 per-ticker checkpoint files were written under `/home/ubuntu/mts-v4-validation-a-capital-checkpoints/`.
All 80 have format `MTS_V4_CAPITAL_VERIFICATION_A_TARGET_V1`.
Total transported trade rows across checkpoints: 2,374,304.
These checkpoints contain outcome/path information and therefore constitute machine-level access to all 80 names.

## What was NOT exposed to the research decision process
The first complete 80-name calculation reached result construction but failed at JSON serialization because NumPy booleans in `criteria` were not serializable.
The runner's statement order attempts `json.dumps(out)` BEFORE printing BASE, SIZED, EXPOSURE_MATCHED, BREADTH, CRITERIA, or CONCLUSION.
Therefore the serialization exception occurred before any aggregate validation metrics or conclusion were printed.
Desktop Commander process history confirms the surfaced post-computation output was the traceback; repeated prior polling showed no result metrics.
No `MTS_V4_CAPITAL_SIZING_VERIFICATION_A_20261002.json` result file exists.
Neither David nor the AI Research Director observed the aggregate 80-name capital-sizing performance, criteria values, or conclusion.
No hypothesis, sizing rule, threshold, genome definition, or candidate was adapted from an observed 80-name result.

## Second run
A serialization-only fix was committed and a checkpoint-reusing rerun was started. David stopped the experiment after recognizing that 80 names were unnecessary. The rerun was terminated before a result was surfaced. No aggregate result file exists.

## Contamination classification
### Verification B — CLEAN / SEALED
The frozen 80 security IDs overlap Verification A 80/80 and Verification B 0/100. Verification B was not accessed by this experiment.

### Verification A remaining 80 — MACHINE-ACCESSED, RESEARCHER-BLINDED
All 80 have persisted outcome checkpoints, so they cannot truthfully be described as machine-untouched. However, aggregate validation outcomes were not surfaced to David or the AI Research Director, and no adaptation occurred from their performance.

This is materially different from researcher unblinding. The 60 names not ultimately assigned to the first post-incident tranche can be retained only under a sealed-evaluator model: their checkpoint contents and any aggregate/ticker-level performance must remain unavailable to the research decision process until prospectively assigned to a future frozen tranche. They must be labeled MACHINE-ACCESSED / RESEARCHER-BLINDED, never pristine or untouched.

### Previously opened A1 20 — OPENED
Already non-pristine before this incident for a separate frozen structural hypothesis.

## Governance failure
The AI Research Director incorrectly equated “80 remaining” with “use all 80 now.” This violated validation-set stewardship and consumed machine access to scarce out-of-sample evidence beyond what was necessary. It also caused avoidable compute, time, user attention, and token expenditure.

## Additional containment finding
Six orphan worker processes from the first aborted run remained alive after the parent was terminated. They were discovered and terminated during this audit. No additional result artifact was produced by them.

## Salvage rule
Do not delete the 80 checkpoints merely to relabel the data untouched; deletion cannot undo access and would destroy the audit trail.
Do not inspect checkpoint contents for comparative performance.
Do not calculate the 80-name aggregate result.
Do not choose a 20-name tranche using any outcome-derived property.
If David elects to continue using Verification A, prospectively freeze an outcome-blind 20-name tranche using only pre-existing metadata/partition order or a deterministic salted selection rule fixed before evaluation. Keep the other 60 sealed from the research decision process and label them MACHINE-ACCESSED / RESEARCHER-BLINDED.

## Required future control
Every validation protocol must specify and enforce an explicit maximum evidence budget (cohort + tranche count) before any outcome access. Runner must abort if requested targets exceed the frozen tranche manifest. “Remaining available” may never be interpreted as authorization to consume the entire remainder.

## Post-incident A2 disposition
David approved a prospectively frozen 20-name A2 tranche from the machine-accessed/researcher-blinded 80. A2 used the first 20 records of the pre-existing frozen 80-target manifest, an outcome-blind selection rule. The other 60 remained sequestered. A2 completed with frozen conclusion `VERIFICATION_A2_FAILED`; Verification B remained sealed. See `Research/Reports/MTS_V4_CAPITAL_SIZING_VERIFICATION_A2_20261002.md`.
