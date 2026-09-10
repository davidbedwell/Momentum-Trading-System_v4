from MTS_V4.bootstrap import build_runtime
from MTS_V4.contracts import AnalysisRequest, ResearchPhase
from MTS_V4.group_aggregation import METHOD_ID, group_aggregate


def test_group_aggregate_sums_multiple_rows_per_exact_group_key():
    rows = [
        {"date": "2026-07-31", "price": "300", "dark_pool_volume": 10, "regular_volume": 20},
        {"date": "2026-07-31", "price": "301", "dark_pool_volume": 15, "regular_volume": 25},
        {"date": "2026-08-01", "price": "302", "dark_pool_volume": 7, "regular_volume": 11},
    ]

    outputs = group_aggregate(
        {"evidence:darkpool": rows},
        {
            "group_by": ["date"],
            "aggregations": [
                {"column": "dark_pool_volume", "statistic": "sum", "output_name": "daily_dark_pool_volume"},
                {"column": "regular_volume", "statistic": "sum", "output_name": "daily_regular_volume"},
            ],
        },
    )

    assert outputs["group_count"] == 2
    assert outputs["derived_datasets"]["grouped_dataset"] == [
        {
            "date": "2026-07-31",
            "daily_dark_pool_volume": 25.0,
            "daily_regular_volume": 45.0,
        },
        {
            "date": "2026-08-01",
            "daily_dark_pool_volume": 7.0,
            "daily_regular_volume": 11.0,
        },
    ]
    assert outputs["derived_dataset_catalog"]["grouped_dataset"]["output_path"] == [
        "derived_datasets",
        "grouped_dataset",
    ]


def test_group_aggregate_does_not_infer_time_buckets():
    rows = [
        {"date": "2026-07-31", "value": 2},
        {"date": "2026-08-01", "value": 3},
    ]

    outputs = group_aggregate(
        {"input": rows},
        {
            "group_by": ["date"],
            "aggregations": [
                {"column": "value", "statistic": "sum", "output_name": "value_sum"},
            ],
        },
    )

    assert [row["date"] for row in outputs["derived_datasets"]["grouped_dataset"]] == [
        "2026-07-31",
        "2026-08-01",
    ]


def test_group_aggregate_is_advertised_and_executable_in_runtime():
    runtime = build_runtime(rd=object())
    spec = runtime.catalog.get(METHOD_ID)

    assert spec.metadata["scientific_selection"] == "none"
    assert spec.metadata["derived_dataset_name"] == "grouped_dataset"

    request = AnalysisRequest(
        request_id="req:group",
        subject_id="equity:AAPL",
        question="Aggregate exact date groups",
        method_id=METHOD_ID,
        evidence_ids=("evidence:darkpool",),
        parameters={
            "group_by": ["date"],
            "aggregations": [
                {"column": "dark_pool_volume", "statistic": "sum", "output_name": "daily_dark_pool_volume"},
            ],
        },
        research_phase=ResearchPhase.EXPLORATION,
    )

    result = runtime.analysis.execute(
        request,
        {
            "evidence:darkpool": [
                {"date": "2026-07-31", "dark_pool_volume": 10},
                {"date": "2026-07-31", "dark_pool_volume": 15},
            ]
        },
    )

    assert result.execution_metadata["execution_status"] == "SUCCESS"
    assert result.outputs["derived_datasets"]["grouped_dataset"] == [
        {"date": "2026-07-31", "daily_dark_pool_volume": 25.0}
    ]
