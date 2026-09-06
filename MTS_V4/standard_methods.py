from __future__ import annotations

import math
import statistics
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodCatalog, MethodSpec, ParameterContract


def _rows(evidence_payloads: Mapping[str, object]) -> tuple[Mapping[str, Any], ...]:
    if len(evidence_payloads) != 1:
        raise ValueError("standard single-dataset methods require exactly one evidence payload")
    payload = next(iter(evidence_payloads.values()))
    rows = tuple(payload)  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("evidence payload must be an iterable of row mappings")
    return rows


def _payload_rows(payload: object, input_name: str) -> tuple[Mapping[str, Any], ...]:
    rows = tuple(payload)  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError(f"input {input_name!r} must be an iterable of row mappings")
    return rows


def _numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    return None


def _finite_numeric(values):
    return [number for value in values if (number := _numeric(value)) is not None]


def _quantile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    weight = pos - lo
    return sorted_values[lo] * (1 - weight) + sorted_values[hi] * weight


def _numeric_summary(values: list[float]) -> Mapping[str, Any]:
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "mean": statistics.fmean(ordered) if ordered else None,
        "median": statistics.median(ordered) if ordered else None,
        "stddev_sample": statistics.stdev(ordered) if len(ordered) >= 2 else None,
        "minimum": min(ordered) if ordered else None,
        "maximum": max(ordered) if ordered else None,
        "q05": _quantile(ordered, .05),
        "q25": _quantile(ordered, .25),
        "q75": _quantile(ordered, .75),
        "q95": _quantile(ordered, .95),
    }


def _derived_dataset(name: str, rows: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    schema = tuple(str(key) for key in rows[0]) if rows else ()
    return {
        "derived_dataset_catalog": {
            name: {
                "row_count": len(rows),
                "schema": list(schema),
                "output_path": ["derived_datasets", name],
                "temporary": True,
            }
        },
        "derived_datasets": {name: rows},
    }


def descriptive_statistics(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(evidence_payloads)
    summaries = {}
    for column in tuple(parameters["columns"]):
        raw = [row.get(column) for row in rows]
        values = sorted(_finite_numeric(raw))
        summaries[str(column)] = {
            "count": len(values), "missing_count": sum(value is None for value in raw),
            "mean": statistics.fmean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "stddev_sample": statistics.stdev(values) if len(values) >= 2 else None,
            "minimum": min(values) if values else None, "maximum": max(values) if values else None,
            "q05": _quantile(values, .05), "q25": _quantile(values, .25),
            "q75": _quantile(values, .75), "q95": _quantile(values, .95),
        }
    return {"row_count": len(rows), "columns": summaries, "interpretation_boundary": "DESCRIPTIVE_ONLY"}


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    dx, dy = [x - mx for x in xs], [y - my for y in ys]
    denominator = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return None if denominator == 0 else sum(x * y for x, y in zip(dx, dy)) / denominator


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def relationship_correlation(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(evidence_payloads)
    left, right = tuple(parameters["columns"])
    kind = str(parameters["correlation_type"]).lower()
    xs = []
    ys = []
    for row in rows:
        x, y = _numeric(row.get(left)), _numeric(row.get(right))
        if x is not None and y is not None:
            xs.append(x)
            ys.append(y)
    value = _pearson(_average_ranks(xs), _average_ranks(ys)) if kind == "spearman" else _pearson(xs, ys)
    return {"left": left, "right": right, "n": len(xs), "correlation_type": kind, "correlation": value, "interpretation_boundary": "RELATIONSHIP_NOT_CAUSATION"}


def percent_change_series(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(evidence_payloads)
    column = str(parameters["column"])
    lag = int(parameters["lag"])
    observations = []
    bad = zero = 0
    for index in range(lag, len(rows)):
        current, prior = _numeric(rows[index].get(column)), _numeric(rows[index - lag].get(column))
        if current is None or prior is None:
            bad += 1
            continue
        if prior == 0:
            zero += 1
            continue
        observations.append({"index": index, "value": (current - prior) / prior})
    derived = _derived_dataset("percent_change", observations)
    return {"column": column, "lag": lag, "observation_count": len(observations), "excluded_non_numeric": bad, "excluded_zero_base": zero, "observations": observations, **derived, "interpretation_boundary": "MEASUREMENT_ONLY_RD_INTERPRETS"}


def rolling_statistics(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(evidence_payloads)
    column = str(parameters["column"])
    window = int(parameters["window"])
    statistic = str(parameters["statistic"])
    observations = []
    excluded = 0
    for index in range(window - 1, len(rows)):
        values = [_numeric(rows[j].get(column)) for j in range(index - window + 1, index + 1)]
        if any(v is None for v in values):
            excluded += 1
            continue
        nums = [float(v) for v in values if v is not None]
        if statistic == "mean":
            value = statistics.fmean(nums)
        elif statistic == "stddev_sample":
            value = statistics.stdev(nums) if len(nums) >= 2 else None
        elif statistic == "minimum":
            value = min(nums)
        elif statistic == "maximum":
            value = max(nums)
        else:
            value = statistics.median(nums)
        observations.append({"index": index, "value": value})
    derived = _derived_dataset("rolling_statistic", observations)
    return {"column": column, "window": window, "statistic": statistic, "observations": observations, "excluded_windows": excluded, **derived, "interpretation_boundary": "MEASUREMENT_ONLY_RD_INTERPRETS"}


def threshold_event_indices(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(evidence_payloads)
    column = str(parameters["column"])
    op = str(parameters["operator"])
    threshold = float(parameters["threshold"])
    events = []
    predicates = {"GT": lambda x: x > threshold, "GE": lambda x: x >= threshold, "LT": lambda x: x < threshold, "LE": lambda x: x <= threshold}
    predicate = predicates[op]
    for index, row in enumerate(rows):
        value = _numeric(row.get(column))
        if value is not None and predicate(value):
            events.append({"index": index, "value": value})
    derived = _derived_dataset("threshold_events", events)
    return {"column": column, "operator": op, "threshold": threshold, "event_count": len(events), "events": events, **derived, "interpretation_boundary": "EVENT_SELECTION_EXACTLY_AS_RD_PARAMETERIZED"}


def forward_path_measurement(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(evidence_payloads)
    price_column = str(parameters["price_column"])
    horizon = int(parameters["horizon"])
    direction = str(parameters["direction"])
    factor = 1.0 if direction == "LONG" else -1.0
    terminal = []
    favorable = []
    adverse = []
    bars_favorable = []
    bars_adverse = []
    derived_rows = []
    bad = zero = 0
    for index in range(0, max(0, len(rows) - horizon)):
        values = [_numeric(rows[index + offset].get(price_column)) for offset in range(0, horizon + 1)]
        if any(v is None for v in values):
            bad += 1
            continue
        entry = float(values[0])
        if entry == 0:
            zero += 1
            continue
        future = [float(v) for v in values[1:]]
        directional = [factor * ((v - entry) / entry) for v in future]
        best = max(directional)
        worst = min(directional)
        terminal_value = directional[-1]
        bars_favorable_value = float(directional.index(best) + 1)
        bars_adverse_value = float(directional.index(worst) + 1)
        terminal.append(terminal_value)
        favorable.append(best)
        adverse.append(worst)
        bars_favorable.append(bars_favorable_value)
        bars_adverse.append(bars_adverse_value)
        derived_rows.append({
            "index": index,
            "terminal_directional_return": terminal_value,
            "max_favorable_directional_return": best,
            "max_adverse_directional_return": worst,
            "bars_to_max_favorable": bars_favorable_value,
            "bars_to_max_adverse": bars_adverse_value,
        })
    derived = _derived_dataset("forward_path_observations", derived_rows)
    return {
        "price_column": price_column,
        "horizon": horizon,
        "direction": direction,
        "eligible_start_count": max(0, len(rows) - horizon),
        "observation_count": len(terminal),
        "excluded_non_numeric": bad,
        "excluded_zero_entry": zero,
        "terminal_directional_return": _numeric_summary(terminal),
        "max_favorable_directional_return": _numeric_summary(favorable),
        "max_adverse_directional_return": _numeric_summary(adverse),
        "bars_to_max_favorable": _numeric_summary(bars_favorable),
        "bars_to_max_adverse": _numeric_summary(bars_adverse),
        "terminal_positive_fraction": (sum(value > 0 for value in terminal) / len(terminal)) if terminal else None,
        **derived,
        "transport_semantics": (
            "Aggregate measurements are transported directly to RD. The exact row-level derived "
            "dataset remains campaign-local and is advertised by derived_dataset_catalog for explicit "
            "RD-authored chaining into later Analysis requests."
        ),
        "interpretation_boundary": "LOOKAHEAD_MEASUREMENT_ONLY_RD_INTERPRETS",
    }


def compose_aligned_dataset(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    """Mechanically align RD-selected columns from multiple payloads by an explicit observation key."""
    alignment = parameters["alignment"]
    selections = parameters["selections"]
    join_type = str(parameters["join_type"]).upper()
    if join_type != "INNER":
        raise ValueError("analysis.dataset.compose currently supports join_type INNER only")
    if not isinstance(alignment, (list, tuple)) or len(alignment) < 2:
        raise ValueError("alignment must contain at least two RD-authored input specifications")
    if not isinstance(selections, (list, tuple)) or not selections:
        raise ValueError("selections must contain at least one RD-authored column specification")

    keyed_rows: dict[str, dict[object, Mapping[str, Any]]] = {}
    alignment_metadata: list[Mapping[str, Any]] = []
    for spec in alignment:
        if not isinstance(spec, Mapping):
            raise ValueError("each alignment entry must be a mapping")
        input_name = str(spec.get("input_name", "")).strip()
        if not input_name or input_name not in evidence_payloads:
            raise ValueError(f"alignment input_name is unavailable: {input_name!r}")
        key = spec.get("key")
        if not isinstance(key, Mapping):
            raise ValueError(f"alignment key for {input_name!r} must be a mapping")
        mode = str(key.get("mode", "")).upper()
        rows = _payload_rows(evidence_payloads[input_name], input_name)
        current: dict[object, Mapping[str, Any]] = {}
        if mode == "ROW_POSITION":
            for row_index, row in enumerate(rows):
                current[row_index] = row
            alignment_metadata.append({"input_name": input_name, "key": {"mode": "ROW_POSITION"}})
        elif mode == "COLUMN":
            column = str(key.get("column", "")).strip()
            if not column:
                raise ValueError(f"COLUMN alignment for {input_name!r} requires key.column")
            for row in rows:
                if column not in row:
                    raise ValueError(f"alignment column {column!r} is missing from input {input_name!r}")
                logical_key = row[column]
                if logical_key in current:
                    raise ValueError(f"alignment key {logical_key!r} is duplicated in input {input_name!r}")
                current[logical_key] = row
            alignment_metadata.append({"input_name": input_name, "key": {"mode": "COLUMN", "column": column}})
        else:
            raise ValueError(f"unsupported alignment key mode for {input_name!r}: {mode!r}")
        keyed_rows[input_name] = current

    aligned_input_names = [str(spec["input_name"]) for spec in alignment]
    if len(set(aligned_input_names)) != len(aligned_input_names):
        raise ValueError("alignment input_name values must be unique")
    common_keys = set(keyed_rows[aligned_input_names[0]])
    for input_name in aligned_input_names[1:]:
        common_keys.intersection_update(keyed_rows[input_name])

    normalized_selections: list[tuple[str, str, str]] = []
    output_names: set[str] = {"alignment_key"}
    for spec in selections:
        if not isinstance(spec, Mapping):
            raise ValueError("each selections entry must be a mapping")
        input_name = str(spec.get("input_name", "")).strip()
        column = str(spec.get("column", "")).strip()
        output_name = str(spec.get("output_name", "")).strip()
        if input_name not in keyed_rows:
            raise ValueError(f"selection input_name is not aligned: {input_name!r}")
        if not column or not output_name:
            raise ValueError("each selection requires nonblank column and output_name")
        if output_name in output_names:
            raise ValueError(f"selection output_name is duplicated or reserved: {output_name!r}")
        output_names.add(output_name)
        normalized_selections.append((input_name, column, output_name))

    composed_rows: list[Mapping[str, Any]] = []
    for logical_key in sorted(common_keys, key=lambda value: (type(value).__name__, repr(value))):
        row_out: dict[str, Any] = {"alignment_key": logical_key}
        for input_name, column, output_name in normalized_selections:
            source_row = keyed_rows[input_name][logical_key]
            if column not in source_row:
                raise ValueError(f"selected column {column!r} is missing from input {input_name!r} at alignment key {logical_key!r}")
            row_out[output_name] = source_row[column]
        composed_rows.append(row_out)

    derived = _derived_dataset("composed_dataset", composed_rows)
    return {
        "join_type": join_type,
        "alignment": alignment_metadata,
        "selections": [
            {"input_name": input_name, "column": column, "output_name": output_name}
            for input_name, column, output_name in normalized_selections
        ],
        "input_row_counts": {name: len(rows) for name, rows in keyed_rows.items()},
        "aligned_row_count": len(composed_rows),
        **derived,
        "interpretation_boundary": "MECHANICAL_ALIGNMENT_ONLY_RD_SELECTS_INPUTS_KEYS_COLUMNS_AND_MEANING",
    }


def classification_metrics(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = _rows(evidence_payloads)
    predicted = str(parameters["predicted_column"])
    actual = str(parameters["actual_column"])
    positive = parameters["positive_value"]
    tp = tn = fp = fn = excluded = 0
    for row in rows:
        if predicted not in row or actual not in row:
            excluded += 1
            continue
        p = row[predicted] == positive
        a = row[actual] == positive
        if p and a:
            tp += 1
        elif p and not a:
            fp += 1
        elif not p and a:
            fn += 1
        else:
            tn += 1
    n = tp + tn + fp + fn
    def ratio(a, b):
        return None if b == 0 else a / b
    return {"n": n, "excluded": excluded, "true_positive": tp, "true_negative": tn, "false_positive": fp, "false_negative": fn, "accuracy": ratio(tp + tn, n), "precision": ratio(tp, tp + fp), "recall": ratio(tp, tp + fn), "specificity": ratio(tn, tn + fp), "interpretation_boundary": "PERFORMANCE_MEASUREMENT_ONLY_RD_INTERPRETS"}


def standard_method_catalog() -> MethodCatalog:
    return MethodCatalog([
        MethodSpec("analysis.descriptive.statistics", ("NORMALIZED_DATASET",), "Compute descriptive summaries for RD-selected columns.", (ParameterContract("columns", True, (list, tuple), minimum_length=1, meaning="RD-selected numeric columns"),), 1),
        MethodSpec("analysis.relationship.correlation", ("NORMALIZED_DATASET",), "Measure pairwise Pearson or Spearman association without causal interpretation.", (ParameterContract("columns", True, (list, tuple), exact_length=2, meaning="two RD-selected numeric columns"), ParameterContract("correlation_type", True, (str,), allowed_values=("pearson", "spearman"), meaning="statistic selected by RD")), 2),
        MethodSpec("analysis.transform.percent_change", ("NORMALIZED_DATASET",), "Compute backward-looking percent change for an RD-selected field and lag.", (ParameterContract("column", True, (str,), meaning="RD-selected numeric field"), ParameterContract("lag", True, (int,), minimum_value=1, meaning="RD-selected backward row lag")), 2, metadata={"temporal_semantics": "present/prior rows only", "reusable_derived_dataset": True}),
        MethodSpec("analysis.rolling.statistics", ("NORMALIZED_DATASET",), "Compute a rolling statistic using an RD-selected field, window, and statistic.", (ParameterContract("column", True, (str,), meaning="RD-selected numeric field"), ParameterContract("window", True, (int,), minimum_value=1, meaning="RD-selected window"), ParameterContract("statistic", True, (str,), allowed_values=("mean", "median", "stddev_sample", "minimum", "maximum"), meaning="RD-selected statistic")), 1, metadata={"reusable_derived_dataset": True}),
        MethodSpec("analysis.events.threshold", ("NORMALIZED_DATASET",), "Identify rows satisfying an RD-authored numeric threshold condition.", (ParameterContract("column", True, (str,), meaning="RD-selected field"), ParameterContract("operator", True, (str,), allowed_values=("GT", "GE", "LT", "LE"), meaning="RD-selected comparison"), ParameterContract("threshold", True, (int, float), meaning="RD-selected threshold")), 1, metadata={"reusable_derived_dataset": True}),
        MethodSpec("analysis.path.forward_measurement", ("NORMALIZED_DATASET",), "Exploration-only look-ahead path measurement over an RD-selected horizon and direction, returning exact aggregate statistics plus a campaign-local reusable derived observation dataset.", (ParameterContract("price_column", True, (str,), meaning="RD-selected price field"), ParameterContract("horizon", True, (int,), minimum_value=1, meaning="RD-selected forward rows"), ParameterContract("direction", True, (str,), allowed_values=("LONG", "SHORT"), meaning="RD-selected directional frame")), 2, True, False, True, {"scientific_selection": "none", "output_shape": "bounded RD transport plus temporary reusable derived dataset", "reusable_derived_dataset": True}),
        MethodSpec(
            "analysis.dataset.compose",
            ("NORMALIZED_DATASET",),
            "Mechanically align RD-selected columns from two or more supplied raw and/or derived row datasets by an explicit RD-selected observation key and return a temporary reusable composed dataset. No variables, keys, aliases, or scientific meaning are inferred.",
            (
                ParameterContract("alignment", True, (list, tuple), minimum_length=2, meaning="RD-authored input alignment specifications: each entry is {input_name, key:{mode:'ROW_POSITION'}} or {input_name, key:{mode:'COLUMN', column:'field'}}"),
                ParameterContract("selections", True, (list, tuple), minimum_length=1, meaning="RD-authored output columns: each entry is {input_name, column, output_name}; output_name is the exact column name in the composed dataset"),
                ParameterContract("join_type", True, (str,), allowed_values=("INNER",), meaning="RD-selected alignment join; currently available capability is exact INNER intersection only"),
            ),
            1,
            metadata={
                "scientific_selection": "none",
                "reusable_derived_dataset": True,
                "derived_dataset_name": "composed_dataset",
                "alignment_key_modes": {
                    "ROW_POSITION": "logical key is the zero-based row position of that supplied dataset; useful when a derived dataset's explicit index refers to source row position",
                    "COLUMN": "logical key is the exact value in the RD-selected column",
                },
                "execution_semantics": "Only rows whose explicit logical keys exist in every aligned input are retained for INNER. Analysis does not infer time matching, nearest-neighbor matching, lagging, filling, interpolation, column choice, or aliases.",
            },
        ),
        MethodSpec("analysis.performance.binary_classification", ("NORMALIZED_DATASET",), "Measure binary classification performance for RD-selected predicted/actual fields and positive label.", (ParameterContract("predicted_column", True, (str,), meaning="RD-selected prediction field"), ParameterContract("actual_column", True, (str,), meaning="RD-selected outcome field"), ParameterContract("positive_value", True, (str, int, float, bool), meaning="RD-selected positive label")), 1),
    ])


def standard_analysis_methods() -> tuple[RegisteredAnalysisMethod, ...]:
    return tuple(RegisteredAnalysisMethod(method_id, implementation) for method_id, implementation in (
        ("analysis.descriptive.statistics", descriptive_statistics),
        ("analysis.relationship.correlation", relationship_correlation),
        ("analysis.transform.percent_change", percent_change_series),
        ("analysis.rolling.statistics", rolling_statistics),
        ("analysis.events.threshold", threshold_event_indices),
        ("analysis.path.forward_measurement", forward_path_measurement),
        ("analysis.dataset.compose", compose_aligned_dataset),
        ("analysis.performance.binary_classification", classification_metrics),
    ))
