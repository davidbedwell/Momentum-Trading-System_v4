# Validation-First Then Exploration Rule

Status: Approved, 2026-09-10

An unseen ticker selected by the AI Research Director for blind validation of an existing finding or hypothesis may subsequently become the next subject for unrestricted full exploratory research.

The permitted order is strict:

1. Select the unseen ticker under the approved adaptive subject-selection process.
2. Perform the blind validation trial under the already frozen hypothesis/protocol and no-look-ahead rules.
3. Lock the prediction before outcome information is exposed.
4. Obtain and score the objective outcome under the frozen success definition.
5. Persist the validation outcome and resulting validation state.
6. Only then release the same ticker to EXPLORATION/full analysis.

Exploratory work performed after scoring may not rewrite, reinterpret, or retroactively alter the already-scored blind trial.

For retrospective historical unseen-subject validation, the complete blind trial can be performed against a historical cutoff and scored before exploratory release.

For genuinely prospective/live validation, unrestricted exploratory research on that same ticker must wait until the validation horizon resolves and the outcome is durably recorded. Merely locking a prediction is not sufficient to release the subject to exploratory look-ahead.

The ticker counts once toward the three-subject autonomous batch. Its batch role may record both `VALIDATION_FIRST` and `EXPLORATION_AFTER_VALIDATION`.

Deterministic code may enforce this phase/order invariant and validation state transitions. It may not choose which hypothesis to validate, which eligible ticker is scientifically useful for validation, or what exploratory questions to pursue afterward.
