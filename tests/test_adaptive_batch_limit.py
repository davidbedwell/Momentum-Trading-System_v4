from __future__ import annotations

from MTS_V4.adaptive_batch import SubjectRunLedger, ThreeSubjectBatchController


def _row(subject_id: str) -> SubjectRunLedger:
    return SubjectRunLedger(
        subject_id=subject_id,
        selection_rationale="test",
        decisions=1,
        analyses_executed=1,
        findings_promoted=0,
    )


def test_default_batch_boundary_remains_three_subjects() -> None:
    controller = ThreeSubjectBatchController(batch_id="default-three")

    for ticker in ("AAPL", "MSFT", "XOM"):
        subject_id = f"equity:{ticker}"
        controller.accept_selection(subject_id=subject_id, rationale="test")
        controller.record_run(_row(subject_id))

    ledger = controller.ledger()
    assert ledger.batch_limit == 3
    assert ledger.requires_review is True
    assert len(ledger.subjects) == 3


def test_explicit_six_subject_boundary_accepts_six_then_requires_review() -> None:
    controller = ThreeSubjectBatchController(batch_id="authorized-six", batch_limit=6)

    for ticker in ("NVDA", "XOM", "AMD", "META", "JPM", "CAT"):
        subject_id = f"equity:{ticker}"
        assert controller.requires_review is False
        controller.accept_selection(subject_id=subject_id, rationale="test")
        controller.record_run(_row(subject_id))

    ledger = controller.ledger()
    assert ledger.batch_limit == 6
    assert ledger.requires_review is True
    assert controller.requires_review is True
    assert len(ledger.subjects) == 6

    defects = controller.validate_selection(
        subject_id="equity:BA",
        rationale="test",
        previously_seen=(),
    )
    assert defects == ("6-subject autonomous batch limit reached; human review required",)
