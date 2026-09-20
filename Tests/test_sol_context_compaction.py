from MTS_V4.sol_context_compaction import compact_neutral_substrate_for_ai_transport


def test_large_neutral_tables_are_not_replayed_but_catalog_access_is_preserved():
    context = {
        "neutral_analysis_substrate": [
            {
                "analysis_id": "analysis:neutral-standard-ohlcv-substrate:v1",
                "result_id": "result-1",
                "method_id": "analysis.substrate.standard_ohlcv",
                "outputs": {
                    "row_count": 100,
                    "descriptive_measurements": {"x": {"n": 100}},
                    "forward_path_summaries": {"h5": {"n": 95}},
                    "unranked_relationship_measurements": [{"predictor": "x", "outcome": "y"}],
                    "calendar_outcome_summaries": {"month": {"1": {"y": {"n": 9}}}},
                    "derived_dataset_catalog": {
                        "standard_ohlcv_panel": {
                            "row_count": 100,
                            "schema": ["date", "x", "y"],
                            "output_path": ["derived_datasets", "standard_ohlcv_panel"],
                        }
                    },
                },
            }
        ],
        "neutral_analysis_substrate_policy": {
            "ai_rd_retains_interpretation_and_research_direction_authority": True,
        },
        "campaign_analysis_result_catalog": (
            {
                "analysis_id": "analysis:neutral-standard-ohlcv-substrate:v1",
                "reusable_derived_datasets": {"standard_ohlcv_panel": {"row_count": 100}},
            },
        ),
    }

    compact = compact_neutral_substrate_for_ai_transport(context)
    outputs = compact["neutral_analysis_substrate"][0]["outputs"]

    assert "unranked_relationship_measurements" not in outputs
    assert "calendar_outcome_summaries" not in outputs
    assert outputs["descriptive_measurements"] == {"x": {"n": 100}}
    assert "standard_ohlcv_panel" in outputs["derived_dataset_catalog"]
    assert compact["campaign_analysis_result_catalog"] == context["campaign_analysis_result_catalog"]
    assert outputs["ai_transport_compaction"]["scientific_selection_or_ranking"] is False
    assert compact["neutral_analysis_substrate_policy"]["ai_rd_retains_full_scientific_authority"] is True


def test_compaction_does_not_mutate_source_context():
    relationship = [{"predictor": "x", "outcome": "y"}]
    context = {
        "neutral_analysis_substrate": [
            {"analysis_id": "a", "outputs": {"unranked_relationship_measurements": relationship}}
        ]
    }
    compact_neutral_substrate_for_ai_transport(context)
    assert context["neutral_analysis_substrate"][0]["outputs"]["unranked_relationship_measurements"] == relationship
