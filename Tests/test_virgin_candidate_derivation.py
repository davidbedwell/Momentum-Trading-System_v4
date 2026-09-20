from __future__ import annotations

import json

import pyarrow as pa
import pyarrow.parquet as pq

from MTS_V4.universe_scientific_partition import (
    ScientificCohort,
    create_frozen_partition,
    write_frozen_partition,
)
from MTS_V4.virgin_candidate_derivation import derive_virgin_candidates
from MTS_V4.virgin_equivalence import deterministic_select_virgins


def _fixture(tmp_path):
    security_ids = [f"S{i}" for i in range(1, 7)]
    partition = create_frozen_partition(
        universe_id="u1",
        security_ids=security_ids,
        cohort_sizes={
            ScientificCohort.DISCOVERY: 4,
            ScientificCohort.VERIFICATION_A: 1,
            ScientificCohort.VERIFICATION_B: 1,
        },
        salt="partition-salt",
    )
    partition_path = tmp_path / "partition.json"
    write_frozen_partition(partition_path, partition)

    membership = tmp_path / "membership.csv"
    membership.write_text(
        "security_id,ticker,start_date,end_date,sector_id\n"
        + "".join(f"S{i},T{i},2000-01-01,,SECTOR\n" for i in range(1, 7)),
        encoding="utf-8",
    )

    prior_exposed = partition.members(ScientificCohort.DISCOVERY)[0]
    audit = tmp_path / "prior_sol.json"
    audit.write_text(json.dumps({
        "format": "MTS_V4_UNIVERSE_PARTITION_PRIOR_SOL_EXPOSURE_REPAIR_V1",
        "prior_exposed_security_ids": [prior_exposed],
    }), encoding="utf-8")

    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({
        "format": "MTS_V4_UNIVERSE_SCIENTIFIC_EXPOSURE_V1",
        "exposures": {"SUBJECT_RESEARCHED": []},
    }), encoding="utf-8")

    research_root = tmp_path / "research"
    research_root.mkdir()

    derived = tmp_path / "derived"
    data_dir = derived / "data"
    data_dir.mkdir(parents=True)
    parquet = data_dir / "all.parquet"
    pq.write_table(
        pa.Table.from_pylist([{"security_id": item} for item in security_ids]),
        parquet,
    )
    (derived / "manifest.json").write_text(json.dumps({
        "format": "MTS_V4_DERIVED_MARKET_STORE_V1",
        "streams": {
            "u1|features:v1": {
                "updates": [{"file_name": "data/all.parquet"}],
            }
        },
    }), encoding="utf-8")
    return partition, partition_path, membership, audit, ledger, research_root, derived, prior_exposed


def test_derivation_uses_partition_prior_sol_and_store_availability(tmp_path):
    partition, partition_path, membership, audit, ledger, research_root, derived, prior_exposed = _fixture(tmp_path)
    candidates = derive_virgin_candidates(
        partition_path=partition_path,
        membership_csv=membership,
        prior_sol_audits=[audit],
        exposure_ledgers=[ledger],
        research_roots=[research_root],
        derived_market_root=derived,
    )
    by_ticker = {item.subject_id: item for item in candidates}
    exposed_ticker = f"T{prior_exposed[1:]}"
    assert by_ticker[exposed_ticker].prior_sol_exposure is True
    assert all(item.starting_data_available for item in candidates)
    selected = deterministic_select_virgins(candidates, protocol_seed="test")
    assert len(selected["selected_subject_ids"]) == 3
    assert exposed_ticker not in selected["selected_subject_ids"]


def test_research_package_marks_subject_nonvirgin(tmp_path):
    partition, partition_path, membership, audit, ledger, research_root, derived, _ = _fixture(tmp_path)
    discovery = partition.members(ScientificCohort.DISCOVERY)
    target = discovery[1]
    ticker = f"T{target[1:]}"
    rp_dir = research_root / "mts-v4-old" / "campaign" / "research_packages"
    rp_dir.mkdir(parents=True)
    (rp_dir / "rp.json").write_text(json.dumps({
        "format": "MTS_V4_RESEARCH_PACKAGE_V1",
        "research_package": {"subject_id": ticker},
    }), encoding="utf-8")
    candidates = derive_virgin_candidates(
        partition_path=partition_path,
        membership_csv=membership,
        prior_sol_audits=[audit],
        exposure_ledgers=[ledger],
        research_roots=[research_root],
        derived_market_root=derived,
    )
    by_ticker = {item.subject_id: item for item in candidates}
    assert by_ticker[ticker].prior_campaign_exposure is True
