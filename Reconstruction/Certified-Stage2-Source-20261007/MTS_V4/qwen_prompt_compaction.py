from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from statistics import fmean, pstdev
from typing import Any, Callable, Mapping, Sequence


class QwenPromptCompactionError(RuntimeError):
    """Raised when a governed Qwen prompt cannot be represented inside its budget."""


@dataclass(frozen=True, slots=True)
class CompactedQwenPrompt:
    messages: tuple[Mapping[str, str], ...]
    input_tokens: int
    source_sha256: str
    compacted_sha256: str
    manifest: tuple[Mapping[str, Any], ...]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _manifest_entry(path: str, action: str, value: Any, **details: Any) -> Mapping[str, Any]:
    return {
        "path": path,
        "action": action,
        "source_sha256": _sha(value),
        **details,
    }


def _identity_projection(item: Mapping[str, Any]) -> Mapping[str, Any]:
    identity_keys = (
        "analysis_id",
        "result_id",
        "request_id",
        "rp_id",
        "question_id",
        "subject_id",
        "security_id",
        "method_id",
        "evidence_id",
        "dataset_name",
        "status",
        "ticker",
        "date",
        "horizon",
        "cohort",
        "bucket",
    )
    return {key: item[key] for key in identity_keys if key in item}


def _leaf_rows(value: Any, prefix: str = "") -> list[tuple[str, Any, Mapping[str, Any]]]:
    rows: list[tuple[str, Any, Mapping[str, Any]]] = []

    def walk(node: Any, path: str, identity: Mapping[str, Any]) -> None:
        if isinstance(node, Mapping):
            next_identity = {**identity, **_identity_projection(node)}
            values = list(node.values())
            homogeneous_mapping_values = bool(values) and (
                all(not isinstance(item, (Mapping, list, tuple)) for item in values)
                or (
                    all(isinstance(item, Mapping) for item in values)
                    and len({tuple(sorted(map(str, item.keys()))) for item in values}) <= 3
                )
            )
            keys = [str(key) for key in node]
            temporal_mapping_keys = len(keys) >= 4 and all(
                (len(key) == 4 and key.isdigit())
                or (len(key) >= 10 and key[4:5] == "-" and key[7:8] == "-")
                for key in keys
            )
            if homogeneous_mapping_values and (len(node) > 32 or temporal_mapping_keys):
                for key in sorted(node, key=str):
                    walk(
                        node[key],
                        f"{path}.{{dynamic_value}}" if path else "{dynamic_value}",
                        {**next_identity, "dynamic_mapping_key": str(key)},
                    )
                return
            for key in sorted(node, key=str):
                walk(node[key], f"{path}.{key}" if path else str(key), next_identity)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item, f"{path}[]", identity)
        else:
            rows.append((path, node, identity))

    walk(value, prefix, {})
    return rows


def _scientific_aggregate(value: Any) -> Mapping[str, Any]:
    """Summarize repetitive output without interpreting or selecting a hypothesis.

    Numeric exceptions are selected by a fixed min/max rule and examples by the
    lowest canonical SHA-256.  Neither rule depends on a desired control answer.
    """
    leaves = _leaf_rows(value)
    by_path: dict[str, list[tuple[Any, Mapping[str, Any]]]] = defaultdict(list)
    for path, leaf, identity in leaves:
        by_path[path].append((leaf, identity))

    summaries: dict[str, Any] = {}
    for path in sorted(by_path):
        observed = by_path[path]
        missing = sum(item is None for item, _ in observed)
        numeric = [
            float(item)
            for item, _ in observed
            if isinstance(item, (int, float))
            and not isinstance(item, bool)
            and math.isfinite(float(item))
        ]
        if numeric:
            minimum = min(numeric)
            maximum = max(numeric)
            min_identity = next(
                identity
                for item, identity in observed
                if isinstance(item, (int, float))
                and not isinstance(item, bool)
                and math.isfinite(float(item))
                and float(item) == minimum
            )
            max_identity = next(
                identity
                for item, identity in observed
                if isinstance(item, (int, float))
                and not isinstance(item, bool)
                and math.isfinite(float(item))
                and float(item) == maximum
            )
            summaries[path] = {
                "kind": "numeric",
                "observed_count": len(numeric),
                "missing_count": missing,
                "minimum": minimum,
                "maximum": maximum,
                "mean": fmean(numeric),
                "population_stddev": pstdev(numeric) if len(numeric) > 1 else 0.0,
                "minimum_identity": min_identity,
                "maximum_identity": max_identity,
            }
            continue

        canonical_values = [
            _canonical(item) for item, _ in observed if item is not None
        ]
        counts = Counter(canonical_values)
        if len(counts) <= 16 and sum(len(key) for key in counts) <= 1024:
            distribution: Any = [
                {"value": json.loads(key), "count": count}
                for key, count in sorted(counts.items())
            ]
        else:
            ordered = sorted(
                ((_sha(json.loads(key)), key, count) for key, count in counts.items()),
                key=lambda item: item[0],
            )
            samples = []
            for _, key, count in ordered[:2]:
                decoded = json.loads(key)
                if isinstance(decoded, str) and len(decoded) > 512:
                    decoded = {
                        "representation": "PREFIX_WITH_FULL_VALUE_SHA256",
                        "character_count": len(decoded),
                        "value_sha256": hashlib.sha256(decoded.encode("utf-8")).hexdigest(),
                        "prefix": decoded[:512],
                    }
                samples.append({"value": decoded, "count": count})
            distribution = {
                "unique_count": len(counts),
                "values_sha256": _sha(sorted(counts.items())),
                "deterministic_hash_samples": samples,
            }
        summaries[path] = {
            "kind": "categorical",
            "observed_count": len(canonical_values),
            "missing_count": missing,
            "distribution": distribution,
        }

    item_count = len(value) if isinstance(value, (list, tuple, Mapping)) else 1
    return {
        "representation": "DETERMINISTIC_SCIENTIFIC_AGGREGATE_V1",
        "source_sha256": _sha(value),
        "item_count": item_count,
        "leaf_count": len(leaves),
        "field_summaries": summaries,
    }


def _compact_catalog_item(item: Any) -> Any:
    if not isinstance(item, Mapping):
        return item
    retain = (
        "analysis_id",
        "result_id",
        "request_id",
        "rp_id",
        "question_id",
        "subject_id",
        "method_id",
        "status",
        "evidence_ids",
        "limitations",
        "dataset_names",
        "derived_datasets",
        "execution_status",
        "future_information",
        "future_outcome_information",
        "future_outcome_access",
        "content_identity",
        "coverage_start",
        "coverage_end",
        "row_count",
        "schema",
    )
    projected = {key: item[key] for key in retain if key in item}
    if not projected:
        projected = dict(_identity_projection(item))
    return projected


def _compact_analysis_catalog(items: Sequence[Any]) -> Mapping[str, Any]:
    schema_registry: dict[str, Any] = {}
    entries = []
    for raw in items:
        item = _compact_catalog_item(raw)
        if not isinstance(item, Mapping):
            entries.append(item)
            continue
        item = dict(item)
        item.pop("request_id", None)
        item.pop("result_id", None)
        future = item.get("future_information")
        if isinstance(future, Mapping):
            item["future_information"] = {
                "contains_future_information": bool(
                    future.get("contains_future_information", False)
                ),
                "method_contract_allows_future_information": bool(
                    future.get("method_contract_allows_future_information", False)
                ),
            }
        datasets = raw.get("reusable_derived_datasets") if isinstance(raw, Mapping) else None
        dataset_refs: dict[str, Any] = {}
        if isinstance(datasets, Mapping):
            for name, metadata in sorted(datasets.items()):
                if isinstance(metadata, Mapping):
                    schema = metadata.get("schema", [])
                    fingerprint = _sha(schema)
                    schema_registry.setdefault(
                        fingerprint,
                        {"column_count": len(schema) if isinstance(schema, list) else None},
                    )
                    dataset_refs[str(name)] = {
                        "schema_ref": fingerprint,
                        "row_count": metadata.get("row_count"),
                    }
                else:
                    dataset_refs[str(name)] = {"metadata_sha256": _sha(metadata)}
        if dataset_refs:
            item["reusable_dataset_metadata_refs"] = dataset_refs
        entries.append(item)
    return {
        "representation": "ANALYSIS_CATALOG_WITH_DEDUPLICATED_DATASET_METADATA_V1",
        "source_sha256": _sha(items),
        "entry_count": len(items),
        "entries": entries,
        "dataset_metadata_registry": schema_registry,
    }


def _compact_historical_lineage(items: Sequence[Any]) -> list[Any]:
    compacted = []
    for item in items:
        if not isinstance(item, Mapping):
            compacted.append(item)
            continue
        projected = {
            key: item[key]
            for key in (
                "result_id",
                "request_id",
                "subject_id",
                "method_id",
                "evidence_ids",
            )
            if key in item
        }
        future = item.get("future_information")
        if isinstance(future, Mapping):
            projected["future_information"] = {
                key: future[key]
                for key in (
                    "contains_future_information",
                    "direct_evidence_ids_with_future_information",
                    "inherited_from_result_ids",
                    "method_contract_allows_future_information",
                )
                if key in future
            }
        compacted.append(projected)
    return compacted


def _compact_batch_records(records: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    identities = []
    outputs_by_method: dict[str, list[Any]] = defaultdict(list)
    for record in records:
        analysis_result = record.get("analysis_result")
        method_id = "UNKNOWN"
        if isinstance(analysis_result, Mapping):
            method_id = str(analysis_result.get("method_id", "UNKNOWN"))
            outputs_by_method[method_id].append(analysis_result.get("outputs", {}))
        compiled = record.get("compiled_request_audit")
        if method_id == "UNKNOWN" and isinstance(compiled, Mapping):
            method_id = str(compiled.get("method_id", "UNKNOWN"))
        identity = {
            key: record[key]
            for key in (
                "analysis_id",
                "rp_id",
                "status",
                "objective_defect",
                "mechanical_repairs",
            )
            if key in record
        }
        identity["method_id"] = method_id
        if isinstance(analysis_result, Mapping):
            for key in ("result_id", "limitations"):
                if key in analysis_result:
                    identity[key] = analysis_result[key]
        identities.append(identity)
    return {
        "representation": "DETERMINISTIC_BATCH_REPORT_COMPACTION_V1",
        "source_sha256": _sha(records),
        "record_count": len(records),
        "status_counts": dict(sorted(Counter(str(x.get("status")) for x in records).items())),
        "record_identities_and_exceptions": identities,
        "scientific_outputs_by_method": {
            method: _scientific_aggregate(outputs)
            for method, outputs in sorted(outputs_by_method.items())
        },
    }


def _compact_research_concept(item: Any) -> Any:
    if not isinstance(item, Mapping):
        return item
    return {
        key: item[key]
        for key in ("concept_id", "name", "description", "questions", "source_class")
        if key in item
    }


def _compact_method_contract(item: Any) -> Any:
    if not isinstance(item, Mapping):
        return item
    contract = {
        key: item[key]
        for key in (
            "method_id",
            "description",
            "artifact_types",
            "minimum_sample",
            "exploration_allowed",
            "validation_allowed",
            "allows_future_information",
        )
        if key in item
    }
    parameters = []
    for raw in item.get("parameters", []):
        if not isinstance(raw, Mapping):
            parameters.append(raw)
            continue
        parameter = {
            key: raw[key]
            for key in ("name", "required", "types", "meaning")
            if key in raw and raw[key] not in (None, "", [])
        }
        constraints = {
            key: raw[key]
            for key in (
                "allowed_values",
                "exact_length",
                "maximum_length",
                "maximum_value",
                "minimum_length",
                "minimum_value",
            )
            if key in raw and raw[key] not in (None, [])
        }
        parameter.update(constraints)
        parameters.append(parameter)
    contract["parameters"] = parameters
    if item.get("metadata"):
        contract["metadata"] = item["metadata"]
    return contract


def _compact(
    value: Any,
    *,
    path: str,
    manifest: list[Mapping[str, Any]],
) -> Any:
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for raw_key in sorted(value, key=str):
            key = str(raw_key)
            child_path = f"{path}.{key}" if path else key
            if key == "cache_key" or key.lower() in {
                "acquired_at",
                "acquired_at_utc",
                "fetched_at",
                "fetched_at_utc",
                "retrieved_at",
                "retrieved_at_utc",
            }:
                manifest.append(
                    _manifest_entry(child_path, "OMITTED_OPERATIONAL_ONLY", value[raw_key])
                )
                continue
            child = value[raw_key]
            if key == "historical_finding_support_lineage" and isinstance(child, list):
                result[key] = {
                    "representation": "REDUNDANT_LINEAGE_FINGERPRINT_V1",
                    "record_count": len(child),
                    "source_sha256": _sha(child),
                    "note": "Full lineage remains in source replay; finding support IDs remain in significant_findings.",
                }
                manifest.append(
                    _manifest_entry(
                        child_path,
                        "OMITTED_REDUNDANT_LINEAGE_ALREADY_REFERENCED_BY_FINDINGS",
                        child,
                        item_count=len(child),
                        representation_sha256=_sha(result[key]),
                    )
                )
            elif key == "available_analysis_methods" and isinstance(child, list):
                result[key] = [_compact_method_contract(item) for item in child]
                manifest.append(
                    _manifest_entry(
                        child_path,
                        "COMPACTED_METHOD_CONTRACTS_WITH_ALL_EXECUTABLE_CONSTRAINTS",
                        child,
                        item_count=len(child),
                        representation_sha256=_sha(result[key]),
                    )
                )
            elif key == "security_ids" and isinstance(child, list):
                result[key] = {
                    "representation": "MEMBERSHIP_COUNT_AND_FINGERPRINT_V1",
                    "subject_count": len(child),
                    "sorted_membership_sha256": _sha(sorted(map(str, child))),
                    "deterministic_hash_samples": sorted(
                        map(str, child),
                        key=lambda item: hashlib.sha256(item.encode("utf-8")).hexdigest(),
                    )[:5],
                }
                manifest.append(
                    _manifest_entry(
                        child_path,
                        "REPRESENTED_BY_COUNT_FINGERPRINT_AND_HASH_SAMPLES",
                        child,
                        subject_count=len(child),
                        representation_sha256=_sha(result[key]),
                    )
                )
            elif key == "records" and isinstance(child, list) and child and all(
                isinstance(item, Mapping) for item in child
            ):
                result[key] = _compact_batch_records(child)
                manifest.append(
                    _manifest_entry(
                        child_path,
                        "COMPACTED_PER_METHOD_WITH_ALL_RECORD_IDENTITIES_AND_FIXED_EXCEPTIONS",
                        child,
                        item_count=len(child),
                        representation_sha256=_sha(result[key]),
                    )
                )
            elif key == "research_concepts" and isinstance(child, list):
                result[key] = [_compact_research_concept(item) for item in child]
                manifest.append(
                    _manifest_entry(
                        child_path,
                        "PROJECTED_CONCEPT_ID_NAME_DESCRIPTION_AND_QUESTIONS",
                        child,
                        item_count=len(child),
                        representation_sha256=_sha(result[key]),
                    )
                )
            elif key == "outputs" and len(_canonical(child)) > 8000:
                result[key] = _scientific_aggregate(child)
                manifest.append(
                    _manifest_entry(
                        child_path,
                        "AGGREGATED_NUMERIC_CATEGORICAL_WITH_FIXED_EXCEPTIONS",
                        child,
                        representation_sha256=_sha(result[key]),
                    )
                )
            elif key == "campaign_analysis_result_catalog" and isinstance(child, list):
                result[key] = _compact_analysis_catalog(child)
                manifest.append(
                    _manifest_entry(
                        child_path,
                        "PROJECTED_IDENTITIES_WITH_DEDUPLICATED_DATASET_METADATA",
                        child,
                        item_count=len(child),
                        representation_sha256=_sha(result[key]),
                    )
                )
            else:
                result[key] = _compact(child, path=child_path, manifest=manifest)
        return result
    if isinstance(value, list):
        if len(_canonical(value)) > 32000 and value and all(
            isinstance(item, Mapping) for item in value
        ):
            aggregate = _scientific_aggregate(value)
            manifest.append(
                _manifest_entry(
                    path,
                    "AGGREGATED_REPETITIVE_RECORDS_WITH_FIXED_EXCEPTIONS",
                    value,
                    item_count=len(value),
                    representation_sha256=_sha(aggregate),
                )
            )
            return aggregate
        return [
            _compact(item, path=f"{path}[{index}]", manifest=manifest)
            for index, item in enumerate(value)
        ]
    return value


def compact_qwen_messages(
    messages: Sequence[Mapping[str, str]],
    *,
    token_counter: Callable[[Sequence[Mapping[str, str]]], int],
    input_token_budget: int = 48_000,
) -> CompactedQwenPrompt:
    if input_token_budget <= 0:
        raise ValueError("input_token_budget must be positive")
    source_messages = tuple(
        {"role": str(item["role"]), "content": str(item["content"])}
        for item in messages
    )
    manifest: list[Mapping[str, Any]] = []
    compacted: list[Mapping[str, str]] = []
    for index, message in enumerate(source_messages):
        if message["role"] != "user":
            compacted.append(message)
            manifest.append(
                _manifest_entry(f"messages[{index}]", "INCLUDED_VERBATIM", message)
            )
            continue
        try:
            document = json.loads(message["content"])
        except json.JSONDecodeError as exc:
            raise QwenPromptCompactionError(
                f"user prompt is not governed JSON: messages[{index}]: {exc}"
            ) from exc
        # Cross-subject Sol-authored narrative is neither raw evidence nor an
        # independent Qwen capability input.  Excluding it prevents answer
        # leakage and is recorded explicitly rather than silently truncating it.
        context = document.get("context")
        if isinstance(context, dict):
            if "prior_subject_scientific_context" in context:
                removed = context.pop("prior_subject_scientific_context")
                manifest.append(
                    _manifest_entry(
                        f"messages[{index}].context.prior_subject_scientific_context",
                        "OMITTED_SOL_AUTHORED_CROSS_SUBJECT_CONTEXT_FOR_BLINDING",
                        removed,
                    )
                )
            nexus = context.get("nexus_context")
            if isinstance(nexus, dict) and "cross_subject_scientific_memory" in nexus:
                removed = nexus.pop("cross_subject_scientific_memory")
                manifest.append(
                    _manifest_entry(
                        f"messages[{index}].context.nexus_context.cross_subject_scientific_memory",
                        "OMITTED_SOL_AUTHORED_CROSS_SUBJECT_CONTEXT_FOR_BLINDING",
                        removed,
                    )
                )
        compact_document = _compact(
            document,
            path=f"messages[{index}]",
            manifest=manifest,
        )
        compact_document["qwen_prompt_compaction"] = {
            "format": "MTS_V4_QWEN_PROMPT_COMPACTION_V1",
            "source_prompt_sha256": _sha(source_messages),
            "policy": (
                "Full source evidence remains in the replay envelope. Repetitive outputs are "
                "represented by deterministic field distributions, numeric magnitude and "
                "uncertainty summaries, missingness, and fixed min/max exceptions. No desired "
                "scientific answer influenced selection."
            ),
        }
        compacted.append(
            {
                "role": message["role"],
                "content": _canonical(compact_document),
            }
        )

    input_tokens = token_counter(compacted)
    if not isinstance(input_tokens, int) or input_tokens < 0:
        raise QwenPromptCompactionError("token counter returned an invalid token count")
    if input_tokens > input_token_budget:
        raise QwenPromptCompactionError(
            "required scientific prompt exceeds governed Qwen input budget after deterministic "
            f"compaction: {input_tokens} > {input_token_budget}; model call refused"
        )
    manifest.append(
        {
            "path": "$",
            "action": "TOKEN_BUDGET_VERIFIED_BY_SERVING_MODEL",
            "input_tokens": input_tokens,
            "input_token_budget": input_token_budget,
            "source_sha256": _sha(source_messages),
            "compacted_sha256": _sha(compacted),
        }
    )
    return CompactedQwenPrompt(
        messages=tuple(compacted),
        input_tokens=input_tokens,
        source_sha256=_sha(source_messages),
        compacted_sha256=_sha(compacted),
        manifest=tuple(manifest),
    )
