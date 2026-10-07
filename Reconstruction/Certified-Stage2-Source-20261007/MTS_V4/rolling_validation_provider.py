from __future__ import annotations

import json
from typing import Mapping

from .sol_batch_provider import SolBatchResearchDirector


ROLLING_VALIDATION_SYSTEM_INSTRUCTION = (
    "A frozen predictive hypothesis does not terminate research on its subject. Treat hypothesis identity and "
    "validation-trial identity as different objects. The frozen proposition keeps one stable hypothesis_id; repeated "
    "blind tests are trials of that same hypothesis, not new hypotheses. Use stable unique trial identifiers such as "
    "H001-T01, H001-T02, and so on. Never mutate a frozen hypothesis definition in response to validation outcomes. "
    "A materially revised proposition requires a new hypothesis_id. Historical same-subject blind validation is valid "
    "only on evidence that was mechanically sequestered and not exposed to RD or Analysis before the hypothesis was "
    "frozen. Never relabel previously exposed exploratory history as blind. When eligible unexposed same-subject data "
    "are available, freeze the hypothesis, run the predeclared blind trials, record their outcomes, then release those "
    "consumed observations from blind status and resume unrestricted exploration on later eligible data. Validation "
    "therefore pauses the exploration frontier; it does not retire the subject. Only report that validation is awaiting "
    "future data or an external unseen subject when no mechanically eligible unexposed same-subject observations remain. "
    "Every decision must author an explicit rolling_program disposition so deterministic orchestration never guesses "
    "whether you intend continued exploration, blind validation, resumed exploration, waiting for new evidence, or true "
    "subject completion."
)

ROLLING_VALIDATION_USER_INSTRUCTIONS = (
    "When a tentative predictive hypothesis is created, do not create a new hypothesis_id for each replication. Keep "
    "the frozen hypothesis unchanged and accumulate LOCK_VALIDATION_TRIAL / RECORD_VALIDATION_OUTCOME updates under "
    "that hypothesis_id. If mechanically sequestered unexposed evidence is available for the active subject, continue "
    "through validation before declaring the subject scientifically complete. After the predeclared validation tranche "
    "is evaluated, resume EXPLORATION on later data unless you independently judge there is no scientifically useful "
    "work left. Data whose validation outcome has been revealed remain durable audit evidence but are permanently "
    "exposed and may never again count as blind evidence for that hypothesis version. Populate "
    "research_state.rolling_program on every decision with disposition, hypothesis_id when relevant, and rationale. "
    "Allowed dispositions are CONTINUE_EXPLORATION, RUN_BLIND_VALIDATION, RESUME_EXPLORATION, AWAIT_NEW_EVIDENCE, and "
    "SUBJECT_COMPLETE. RUN_BLIND_VALIDATION means the hypothesis is frozen and the next scientific phase is its blind "
    "test; it does not mean the subject is exhausted. AWAIT_NEW_EVIDENCE is appropriate only when required blind work "
    "cannot proceed because no eligible unexposed evidence is currently available. SUBJECT_COMPLETE is reserved for an "
    "actual scientific judgment that no further useful subject work remains, not merely for reaching a validation boundary."
)


class RollingValidationSolBatchResearchDirector(SolBatchResearchDirector):
    """Sol RD prompt contract for rolling discovery -> blind validation -> discovery.

    This class changes instructions only. It does not manufacture hypotheses,
    choose validation windows, or decide scientific continuation. Mechanical data
    sequestration must be provided by the campaign runtime before same-subject
    historical blind validation can occur.
    """

    @classmethod
    def _batch_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> list[Mapping[str, str]]:
        messages = list(
            super()._batch_messages(
                operation=operation,
                mission=mission,
                payload=payload,
            )
        )
        system = dict(messages[0])
        system["content"] = str(system["content"]) + " " + ROLLING_VALIDATION_SYSTEM_INSTRUCTION

        user = dict(messages[1])
        document = json.loads(str(user["content"]))
        instructions = list(document.get("instructions", []))
        instructions.append(ROLLING_VALIDATION_USER_INSTRUCTIONS)
        document["instructions"] = instructions
        schema = document.get("required_batch_decision_schema")
        if isinstance(schema, dict):
            research_state = schema.get("research_state")
            if isinstance(research_state, dict):
                research_state["rolling_program"] = {
                    "disposition": (
                        "CONTINUE_EXPLORATION, RUN_BLIND_VALIDATION, RESUME_EXPLORATION, "
                        "AWAIT_NEW_EVIDENCE, or SUBJECT_COMPLETE"
                    ),
                    "hypothesis_id": "stable hypothesis_id when relevant, otherwise null",
                    "rationale": "AI-authored scientific/lifecycle rationale",
                }
        user["content"] = json.dumps(
            document,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        )
        return [system, user]
