from datetime import datetime, timezone

import pytest

from Engines.Analysis.temporal import (
    FutureInformationLeakageError,
    HoldoutConflictError,
    InformationClass,
    TemporalIntegrityService,
    TimeInterval,
)


def ts(day: int):
    return datetime(2026, 1, day, tzinfo=timezone.utc)


def test_retrospective_outcome_cannot_be_predictor():
    service = TemporalIntegrityService()
    with pytest.raises(FutureInformationLeakageError, match="retrospective predictors"):
        service.validate_feature_roles(
            information_classes={
                "sma_20": InformationClass.CONTEMPORANEOUS,
                "forward_return_5d": InformationClass.RETROSPECTIVE_OUTCOME,
            },
            predictor_columns=("sma_20", "forward_return_5d"),
        )


def test_retrospective_outcome_cannot_select_sample_when_claimed_contemporaneous():
    service = TemporalIntegrityService()
    with pytest.raises(FutureInformationLeakageError, match="retrospective selection"):
        service.validate_feature_roles(
            information_classes={"mfe_10d": "RETROSPECTIVE_OUTCOME"},
            selection_columns=("mfe_10d",),
        )


def test_discovery_cannot_use_holdout_observations():
    service = TemporalIntegrityService()
    with pytest.raises(HoldoutConflictError, match="protected observation"):
        service.validate_protected_usage(
            [ts(2), ts(9)],
            usage="DISCOVERY",
            discovery_interval=TimeInterval(ts(1), ts(5), "discovery"),
            holdout_interval=TimeInterval(ts(8), ts(10), "holdout"),
        )


def test_validation_cannot_use_holdout():
    service = TemporalIntegrityService()
    with pytest.raises(HoldoutConflictError):
        service.validate_protected_usage(
            [ts(9)],
            usage="VALIDATION",
            holdout_interval=TimeInterval(ts(8), ts(10), "holdout"),
        )


def test_retrospective_outcome_is_valid_when_not_used_as_predictor_or_selection():
    report = TemporalIntegrityService().validate_feature_roles(
        information_classes={
            "close": "CONTEMPORANEOUS",
            "future_return_5d": "RETROSPECTIVE_OUTCOME",
        },
        predictor_columns=("close",),
        selection_columns=("close",),
    )
    assert report.state == "PASSED"
    assert report.retrospective_columns == ("future_return_5d",)
