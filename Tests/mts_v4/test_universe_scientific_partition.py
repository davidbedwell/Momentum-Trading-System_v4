from __future__ import annotations

import json

import pytest

from MTS_V4.universe_scientific_partition import (
    ScientificCohort,
    UniverseScientificPartitionError,
    create_frozen_partition,
    create_stratified_frozen_partition,
    load_frozen_partition,
    write_frozen_partition,
    write_campaign_exposure_ledger,
)


def _sizes():
    return {
        ScientificCohort.DISCOVERY: 6,
        ScientificCohort.VERIFICATION_A: 2,
        ScientificCohort.VERIFICATION_B: 2,
    }


def test_partition_is_exact_disjoint_complete_and_reproducible():
    ids = [f"SEC-{number}" for number in range(10)]
    first = create_frozen_partition(universe_id="sp500", security_ids=ids, cohort_sizes=_sizes(), salt="frozen-control-v1")
    second = create_frozen_partition(universe_id="sp500", security_ids=list(reversed(ids)), cohort_sizes=_sizes(), salt="frozen-control-v1")
    assert first == second
    assert len(first.members(ScientificCohort.DISCOVERY)) == 6
    assert len(first.members(ScientificCohort.VERIFICATION_A)) == 2
    assert len(first.members(ScientificCohort.VERIFICATION_B)) == 2
    assert set(first.all_security_ids) == set(ids)
    assert len(first.all_security_ids) == len(set(first.all_security_ids))


def test_partition_has_no_implicit_governance_split():
    with pytest.raises(UniverseScientificPartitionError, match="explicit size"):
        create_frozen_partition(
            universe_id="sp500",
            security_ids=["A", "B"],
            cohort_sizes={ScientificCohort.DISCOVERY: 2},
            salt="x",
        )


def test_partition_rejects_duplicate_security_identity():
    with pytest.raises(UniverseScientificPartitionError, match="unique"):
        create_frozen_partition(
            universe_id="sp500",
            security_ids=["A", "A"],
            cohort_sizes={
                ScientificCohort.DISCOVERY: 1,
                ScientificCohort.VERIFICATION_A: 0,
                ScientificCohort.VERIFICATION_B: 1,
            },
            salt="x",
        )


def test_frozen_partition_round_trip_and_refuses_replacement(tmp_path):
    target = tmp_path / "partition.json"
    partition = create_frozen_partition(
        universe_id="sp500",
        security_ids=[f"SEC-{number}" for number in range(10)],
        cohort_sizes=_sizes(),
        salt="x",
    )
    write_frozen_partition(target, partition)
    assert load_frozen_partition(target) == partition
    altered = create_frozen_partition(
        universe_id="sp500",
        security_ids=[f"SEC-{number}" for number in range(10)],
        cohort_sizes=_sizes(),
        salt="y",
    )
    with pytest.raises(UniverseScientificPartitionError, match="refusing to replace"):
        write_frozen_partition(target, altered)


def test_partition_detects_manifest_tampering(tmp_path):
    target = tmp_path / "partition.json"
    partition = create_frozen_partition(
        universe_id="sp500",
        security_ids=[f"SEC-{number}" for number in range(10)],
        cohort_sizes=_sizes(),
        salt="x",
    )
    write_frozen_partition(target, partition)
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["cohorts"]["DISCOVERY"][0] = "ALTERED"
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(UniverseScientificPartitionError, match="identity"):
        load_frozen_partition(target)


def test_exposure_ledger_distinguishes_context_from_outcome_and_preserves_reserves(tmp_path):
    partition = create_frozen_partition(
        universe_id="sp500",
        security_ids=[f"SEC-{number}" for number in range(10)],
        cohort_sizes=_sizes(),
        salt="x",
    )
    target = tmp_path / "exposure.json"
    write_campaign_exposure_ledger(
        target,
        partition=partition,
        campaign_id="campaign-1",
        context_security_ids=partition.all_security_ids,
        outcome_security_ids=partition.members(ScientificCohort.DISCOVERY),
    )
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert set(payload["exposures"]["CONTEXT_ONLY"]) == set(partition.all_security_ids)
    assert set(payload["exposures"]["DISCOVERY_OUTCOME_EXPOSED"]) == set(partition.members(ScientificCohort.DISCOVERY))
    assert payload["exposures"]["BLIND_VERIFICATION_EXPOSED"] == []
    assert set(payload["reserved_unexposed"]["VERIFICATION_A"]) == set(partition.members(ScientificCohort.VERIFICATION_A))


def test_stratified_partition_is_exact_reproducible_and_balanced() -> None:
    ids = [f"SEC-{number:02d}" for number in range(30)]
    strata = {
        security_id: (f"SECTOR-{index % 2}", f"SIZE-{index % 3}")
        for index, security_id in enumerate(ids)
    }
    sizes = {
        ScientificCohort.DISCOVERY: 18,
        ScientificCohort.VERIFICATION_A: 6,
        ScientificCohort.VERIFICATION_B: 6,
    }
    first, audit = create_stratified_frozen_partition(
        universe_id="sp500", security_ids=ids, cohort_sizes=sizes, strata=strata, salt="x"
    )
    second, _ = create_stratified_frozen_partition(
        universe_id="sp500", security_ids=list(reversed(ids)), cohort_sizes=sizes,
        strata=strata, salt="x"
    )
    assert first == second
    assert len(first.members(ScientificCohort.DISCOVERY)) == 18
    assert len(first.members(ScientificCohort.VERIFICATION_A)) == 6
    assert len(first.members(ScientificCohort.VERIFICATION_B)) == 6
    assert set(first.all_security_ids) == set(ids)
    assert audit["scientific_selection_or_ranking"] is False
    for item in audit["strata"]:
        assert item["cohort_counts"] == {
            "DISCOVERY": 3, "VERIFICATION_A": 1, "VERIFICATION_B": 1
        }


def test_stratified_partition_requires_complete_attributes() -> None:
    with pytest.raises(UniverseScientificPartitionError, match="exactly cover"):
        create_stratified_frozen_partition(
            universe_id="sp500",
            security_ids=["A", "B"],
            cohort_sizes={
                ScientificCohort.DISCOVERY: 1,
                ScientificCohort.VERIFICATION_A: 1,
                ScientificCohort.VERIFICATION_B: 0,
            },
            strata={"A": ("TECH", "UPPER")},
            salt="x",
        )
