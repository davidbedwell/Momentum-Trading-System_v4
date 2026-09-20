from __future__ import annotations

import math
import statistics
from typing import Any, Mapping

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract

METHOD_ID = "analysis.transform.rolling_numeric"


def _finite(value: object) -> float | None:
    if isinstance(value, bool): return None
    try: x = float(value)
    except (TypeError, ValueError): return None
    return x if math.isfinite(x) else None


def rolling_numeric(payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    if len(payloads) != 1: raise ValueError("rolling transform requires exactly one resolved row dataset")
    rows = [dict(r) for r in next(iter(payloads.values())) if isinstance(r, Mapping)]
    column = str(parameters["column"]); output_name = str(parameters["output_name"]).strip(); window = int(parameters["window"]); statistic = str(parameters["statistic"]).upper(); lag = int(parameters.get("lag", 0))
    if not output_name or output_name == "index": raise ValueError("output_name must be nonblank and cannot be index")
    if any(output_name in r for r in rows): raise ValueError(f"output_name already exists: {output_name}")
    out = []
    for i, row in enumerate(rows):
        end = i - lag + 1
        start = end - window
        vals = [_finite(r.get(column)) for r in rows[max(0, start):max(0, end)]] if end > 0 else []
        vals = [v for v in vals if v is not None]
        value = None
        if vals:
            if statistic == "MEAN": value = statistics.fmean(vals)
            elif statistic == "SUM": value = sum(vals)
            elif statistic == "MIN": value = min(vals)
            elif statistic == "MAX": value = max(vals)
            elif statistic == "SLOPE":
                if len(vals) >= 2:
                    xs = list(range(len(vals))); mx = statistics.fmean(xs); my = statistics.fmean(vals); den = sum((x-mx)**2 for x in xs); value = None if den == 0 else sum((x-mx)*(y-my) for x,y in zip(xs, vals))/den
            else: raise ValueError(f"unsupported statistic: {statistic}")
        copied = dict(row); copied["index"] = row.get("index", i); copied[output_name] = value
        copied["__observation_lineage"] = {"input_row_anchor": i, "window_start": max(0, start), "window_end_exclusive": max(0, end), "semantics": "MECHANICAL_ROW_WINDOW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION"}
        out.append(copied)
    return {"column": column, "window": window, "lag": lag, "statistic": statistic, "derived_dataset_catalog": {"rolling_numeric_feature": {"row_count": len(out), "schema": list(out[0]) if out else [], "output_path": ["derived_datasets", "rolling_numeric_feature"], "temporary": True}}, "derived_datasets": {"rolling_numeric_feature": out}, "interpretation_boundary": "RD_SELECTED_ROLLING_ARITHMETIC_ONLY_RD_INTERPRETS"}


def method_spec() -> MethodSpec:
    return MethodSpec(METHOD_ID, ("NORMALIZED_DATASET",), "Apply one exact RD-selected rolling numeric calculation while preserving source rows and stable row index; avoids multi-step recomposition solely for rolling arithmetic.", (ParameterContract("column", True, (str,), meaning="RD-selected numeric source column"), ParameterContract("window", True, (int,), minimum_value=2, maximum_value=5040, meaning="RD-selected observation window"), ParameterContract("statistic", True, (str,), allowed_values=("MEAN","SUM","MIN","MAX","SLOPE"), meaning="RD-selected rolling statistic"), ParameterContract("lag", False, (int,), minimum_value=0, maximum_value=5040, meaning="RD-selected number of current/trailing rows excluded before window"), ParameterContract("output_name", True, (str,), meaning="RD-authored output field name")), 2, True, True, False, {"scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY", "deterministic_ranking": False, "source_columns_preserved": True, "stable_index_preserved": True, "reusable_derived_dataset": True, "derived_dataset_name": "rolling_numeric_feature"})


def analysis_method() -> RegisteredAnalysisMethod: return RegisteredAnalysisMethod(METHOD_ID, rolling_numeric)
