from __future__ import annotations

from typing import Mapping


# Transport-only compaction.  The underlying AnalysisResult and reusable derived
# datasets remain campaign-local and addressable by logical analysis_id.  This
# function must never rank, select, interpret, or suppress scientific options.
_LARGE_NEUTRAL_KEYS = frozenset({
    "unranked_relationship_measurements",
    "calendar_outcome_summaries",
})


def compact_neutral_substrate_for_ai_transport(
    nexus_context: Mapping[str, object],
) -> dict[str, object]:
    context = dict(nexus_context)
    raw = context.get("neutral_analysis_substrate")
    if not isinstance(raw, (list, tuple)):
        return context

    compacted = []
    for entry in raw:
        if not isinstance(entry, Mapping):
            compacted.append(entry)
            continue
        item = dict(entry)
        outputs = item.get("outputs")
        if isinstance(outputs, Mapping):
            source = dict(outputs)
            omitted = sorted(key for key in _LARGE_NEUTRAL_KEYS if key in source)
            for key in omitted:
                source.pop(key, None)
            if omitted:
                source["ai_transport_compaction"] = {
                    "omitted_precomputed_output_keys": omitted,
                    "underlying_analysis_result_retained": True,
                    "reusable_dataset_access_retained": True,
                    "scientific_selection_or_ranking": False,
                    "authority": (
                        "TRANSPORT_ONLY. AI Research Director retains authority to request, "
                        "recompute, challenge, reformulate, or ignore any relationship."
                    ),
                }
            item["outputs"] = source
        compacted.append(item)

    context["neutral_analysis_substrate"] = compacted
    policy = dict(context.get("neutral_analysis_substrate_policy", {}))
    policy.update(
        {
            "transport_compaction": "LARGE_PRECOMPUTED_TABLES_CATALOGED_NOT_REPLAYED",
            "underlying_analysis_results_retained": True,
            "deterministic_scientific_selection_or_summarization": False,
            "ai_rd_retains_full_scientific_authority": True,
        }
    )
    context["neutral_analysis_substrate_policy"] = policy
    return context
