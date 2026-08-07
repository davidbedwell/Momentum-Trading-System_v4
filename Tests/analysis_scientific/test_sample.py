import pytest

from Engines.Analysis.sample import SampleConstructor, SampleSpecification
from Engines.Analysis.temporal import FutureInformationLeakageError


def rows():
    return [
        {"ticker": "SMH", "date": "2026-01-01T00:00:00Z", "close": 100.0, "volume": 10},
        {"ticker": "SMH", "date": "2026-01-02T00:00:00Z", "close": 101.0, "volume": None},
        {"ticker": "SMH", "date": "2026-01-03T00:00:00Z", "close": 102.0, "volume": 30},
        {"ticker": "SMH", "date": "2026-01-04T00:00:00Z", "close": 99.0, "volume": 40},
    ]


def test_sample_is_reproducible_and_accounts_for_exclusions():
    spec = SampleSpecification(
        date_range={"start": "2026-01-01T00:00:00Z", "end": "2026-01-03T00:00:00Z"},
        inclusion_rules=({"column": "close", "op": "gte", "value": 100},),
    )
    constructor = SampleConstructor()
    first = constructor.construct(rows(), spec, required_columns=("volume",))
    second = constructor.construct(rows(), spec, required_columns=("volume",))

    assert first.record.sample_fingerprint == second.record.sample_fingerprint
    assert first.record.eligible_count == 4
    assert first.record.included_count == 2
    assert first.record.excluded_count == 2
    assert first.record.exclusion_counts_by_reason == {
        "MISSING_REQUIRED:volume": 1,
        "OUTSIDE_DATE_RANGE": 1,
    }


def test_input_order_does_not_change_sample_identity():
    spec = SampleSpecification()
    constructor = SampleConstructor()
    forward = constructor.construct(rows(), spec)
    reverse = constructor.construct(list(reversed(rows())), spec)
    assert forward.record.sample_fingerprint == reverse.record.sample_fingerprint
    assert forward.record.included_observation_identity == reverse.record.included_observation_identity


def test_comparison_group_membership_is_preserved():
    spec = SampleSpecification(
        comparison_definition={
            "groups": {
                "high_volume": {"column": "volume", "op": "gte", "value": 30},
            }
        },
        missing_data_policy="ALLOW",
    )
    sample = SampleConstructor().construct(rows(), spec)
    assert len(sample.record.group_membership["high_volume"]) == 2


def test_sample_constructor_rejects_future_outcome_selection():
    spec = SampleSpecification()
    enriched = [dict(row, forward_return_5d=0.1) for row in rows()]
    with pytest.raises(FutureInformationLeakageError):
        SampleConstructor().construct(
            enriched,
            spec,
            information_classes={
                "forward_return_5d": "RETROSPECTIVE_OUTCOME",
                "close": "CONTEMPORANEOUS",
            },
            selection_columns=("forward_return_5d",),
        )
