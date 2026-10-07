from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Mapping

from .research_package import ResearchAnalysisRecord


ZERO_BOUNDARY_COHORT_METHOD = "analysis.cross_sectional.cohort_effect"

# These are representation semantics, not discovered thresholds.  Each field is
# defined so zero separates the two economically distinct states named by the
# feature (gain/loss, above/below, positive/negative slope or surprise).
_ZERO_BOUNDARY_BASE_COLUMNS = frozenset(
    {
        "return_1",
        "return_3",
        "return_5",
        "return_10",
        "return_20",
        "return_63",
        "return_126",
        "return_252",
        "return_252_skip_20",
        "close_to_sma_20",
        "close_to_sma_50",
        "close_to_sma_200",
        "sma20_slope_5",
        "gap_return",
        "intraday_return",
        "earnings_surprise_pct",
    }
)
_VERSION_SUFFIX = re.compile(r"__v[0-9]+$")


def has_natural_zero_boundary(column: str) -> bool:
    """Return whether zero is part of the column's defined economic semantics."""
    return _VERSION_SUFFIX.sub("", column.strip()) in _ZERO_BOUNDARY_BASE_COLUMNS


@dataclass(frozen=True, slots=True)
class FormulationCompletenessContract:
    """Mechanical minimum coverage required before predictive research closes.

    The contract does not assert that a relationship exists and does not choose
    a discovered threshold.  It requires the AI Research Director to compare
    the two states already defined by a signed feature before concluding that
    the feature has no useful predictive structure.
    """

    subject_id: str
    signed_predictor_columns: tuple[str, ...]
    outcome_columns: tuple[str, ...]

    @classmethod
    def from_columns(
        cls,
        *,
        subject_id: str,
        predictor_columns: Iterable[str],
        outcome_columns: Iterable[str],
    ) -> "FormulationCompletenessContract | None":
        signed = tuple(
            dict.fromkeys(
                column.strip()
                for column in predictor_columns
                if column.strip() and has_natural_zero_boundary(column)
            )
        )
        outcomes = tuple(
            dict.fromkeys(column.strip() for column in outcome_columns if column.strip())
        )
        if not signed or not outcomes:
            return None
        return cls(
            subject_id=subject_id,
            signed_predictor_columns=signed,
            outcome_columns=outcomes,
        )

    @classmethod
    def from_mapping(
        cls,
        raw: Mapping[str, object],
    ) -> "FormulationCompletenessContract":
        subject_id = str(raw.get("subject_id", "")).strip()
        signed = raw.get("signed_predictor_columns")
        outcomes = raw.get("outcome_columns")
        if not subject_id:
            raise ValueError("formulation-completeness subject_id cannot be blank")
        if not isinstance(signed, (list, tuple)) or not isinstance(outcomes, (list, tuple)):
            raise ValueError("formulation-completeness columns must be lists")
        contract = cls.from_columns(
            subject_id=subject_id,
            predictor_columns=(str(value) for value in signed),
            outcome_columns=(str(value) for value in outcomes),
        )
        if contract is None:
            raise ValueError("formulation-completeness contract cannot be empty")
        if tuple(str(value) for value in signed) != contract.signed_predictor_columns:
            raise ValueError("recorded signed predictors violate zero-boundary semantics")
        if tuple(str(value) for value in outcomes) != contract.outcome_columns:
            raise ValueError("recorded outcome columns are invalid")
        return contract

    def to_mapping(self) -> Mapping[str, object]:
        return {
            "subject_id": self.subject_id,
            "required_method_id": ZERO_BOUNDARY_COHORT_METHOD,
            "signed_predictor_columns": list(self.signed_predictor_columns),
            "outcome_columns": list(self.outcome_columns),
            "cohort_boundary": 0.0,
            "accepted_positive_directions": ["GE", "GT"],
            "authority": (
                "Mechanical formulation-completeness requirement only. Zero is already the "
                "defined economic boundary of these signed features. This contract does not "
                "assert direction, magnitude, significance, stability, or trading utility."
            ),
        }

    def closure_defect(
        self,
        analyses: Iterable[ResearchAnalysisRecord],
    ) -> str | None:
        completed: set[tuple[str, str]] = set()
        for analysis in analyses:
            if (
                analysis.execution_status != "SUCCESS"
                or analysis.method_id != ZERO_BOUNDARY_COHORT_METHOD
            ):
                continue
            parameters = analysis.parameters
            try:
                threshold = float(parameters.get("threshold"))
            except (TypeError, ValueError):
                continue
            direction = str(parameters.get("direction", "")).upper()
            predictor = str(parameters.get("cohort_column", "")).strip()
            outcome = str(parameters.get("outcome_column", "")).strip()
            if threshold == 0.0 and direction in {"GE", "GT"}:
                completed.add((predictor, outcome))

        missing = [
            (predictor, outcome)
            for predictor in self.signed_predictor_columns
            for outcome in self.outcome_columns
            if (predictor, outcome) not in completed
        ]
        if not missing:
            return None
        rendered = ", ".join(f"{predictor}->{outcome}" for predictor, outcome in missing)
        return (
            "subject closure is blocked by the signed-feature formulation-completeness "
            "contract. Continue research and complete successful "
            f"{ZERO_BOUNDARY_COHORT_METHOD} analyses at threshold=0 with direction GE or GT "
            f"for these predictor/outcome pairs: {rendered}. Interpret the returned results "
            "scientifically; the gate does not imply that any effect exists."
        )
