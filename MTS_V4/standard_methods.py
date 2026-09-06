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
    if len(xs) < 2: return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    dx, dy = [x-mx for x in xs], [y-my for y in ys]
    denominator = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return None if denominator == 0 else sum(x*y for x,y in zip(dx,dy))/denominator


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i]); ranks=[0.0]*len(values); i=0
    while i < len(order):
        j=i
        while j+1 < len(order) and values[order[j+1]] == values[order[i]]: j += 1
        rank=(i+j+2)/2.0
        for k in range(i,j+1): ranks[order[k]]=rank
        i=j+1
    return ranks


def relationship_correlation(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows=_rows(evidence_payloads); left,right=tuple(parameters["columns"]); kind=str(parameters["correlation_type"]).lower()
    xs=[]; ys=[]
    for row in rows:
        x,y=_numeric(row.get(left)),_numeric(row.get(right))
        if x is not None and y is not None: xs.append(x); ys.append(y)
    value=_pearson(_average_ranks(xs),_average_ranks(ys)) if kind=="spearman" else _pearson(xs,ys)
    return {"left":left,"right":right,"n":len(xs),"correlation_type":kind,"correlation":value,"interpretation_boundary":"RELATIONSHIP_NOT_CAUSATION"}


def percent_change_series(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows=_rows(evidence_payloads); column=str(parameters["column"]); lag=int(parameters["lag"]); observations=[]; bad=zero=0
    for index in range(lag,len(rows)):
        current,prior=_numeric(rows[index].get(column)),_numeric(rows[index-lag].get(column))
        if current is None or prior is None: bad+=1; continue
        if prior==0: zero+=1; continue
        observations.append({"index":index,"value":(current-prior)/prior})
    derived = _derived_dataset("percent_change", observations)
    return {"column":column,"lag":lag,"observation_count":len(observations),"excluded_non_numeric":bad,"excluded_zero_base":zero,"observations":observations,**derived,"interpretation_boundary":"MEASUREMENT_ONLY_RD_INTERPRETS"}


def rolling_statistics(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows=_rows(evidence_payloads); column=str(parameters["column"]); window=int(parameters["window"]); statistic=str(parameters["statistic"]); observations=[]; excluded=0
    for index in range(window-1,len(rows)):
        values=[_numeric(rows[j].get(column)) for j in range(index-window+1,index+1)]
        if any(v is None for v in values): excluded+=1; continue
        nums=[float(v) for v in values if v is not None]
        if statistic=="mean": value=statistics.fmean(nums)
        elif statistic=="stddev_sample": value=statistics.stdev(nums) if len(nums)>=2 else None
        elif statistic=="minimum": value=min(nums)
        elif statistic=="maximum": value=max(nums)
        else: value=statistics.median(nums)
        observations.append({"index":index,"value":value})
    derived = _derived_dataset("rolling_statistic", observations)
    return {"column":column,"window":window,"statistic":statistic,"observations":observations,"excluded_windows":excluded,**derived,"interpretation_boundary":"MEASUREMENT_ONLY_RD_INTERPRETS"}


def threshold_event_indices(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows=_rows(evidence_payloads); column=str(parameters["column"]); op=str(parameters["operator"]); threshold=float(parameters["threshold"]); events=[]
    predicates={"GT":lambda x:x>threshold,"GE":lambda x:x>=threshold,"LT":lambda x:x<threshold,"LE":lambda x:x<=threshold}
    predicate=predicates[op]
    for index,row in enumerate(rows):
        value=_numeric(row.get(column))
        if value is not None and predicate(value): events.append({"index":index,"value":value})
    derived = _derived_dataset("threshold_events", events)
    return {"column":column,"operator":op,"threshold":threshold,"event_count":len(events),"events":events,**derived,"interpretation_boundary":"EVENT_SELECTION_EXACTLY_AS_RD_PARAMETERIZED"}


def forward_path_measurement(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows=_rows(evidence_payloads); price_column=str(parameters["price_column"]); horizon=int(parameters["horizon"]); direction=str(parameters["direction"]); factor=1.0 if direction=="LONG" else -1.0
    terminal=[]; favorable=[]; adverse=[]; bars_favorable=[]; bars_adverse=[]; derived_rows=[]; bad=zero=0
    for index in range(0,max(0,len(rows)-horizon)):
        values=[_numeric(rows[index+offset].get(price_column)) for offset in range(0,horizon+1)]
        if any(v is None for v in values): bad+=1; continue
        entry=float(values[0])
        if entry==0: zero+=1; continue
        future=[float(v) for v in values[1:]]
        directional=[factor*((v-entry)/entry) for v in future]
        best=max(directional); worst=min(directional)
        terminal_value=directional[-1]
        bars_favorable_value=float(directional.index(best)+1)
        bars_adverse_value=float(directional.index(worst)+1)
        terminal.append(terminal_value); favorable.append(best); adverse.append(worst)
        bars_favorable.append(bars_favorable_value); bars_adverse.append(bars_adverse_value)
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
        "price_column":price_column,
        "horizon":horizon,
        "direction":direction,
        "eligible_start_count":max(0,len(rows)-horizon),
        "observation_count":len(terminal),
        "excluded_non_numeric":bad,
        "excluded_zero_entry":zero,
        "terminal_directional_return":_numeric_summary(terminal),
        "max_favorable_directional_return":_numeric_summary(favorable),
        "max_adverse_directional_return":_numeric_summary(adverse),
        "bars_to_max_favorable":_numeric_summary(bars_favorable),
        "bars_to_max_adverse":_numeric_summary(bars_adverse),
        "terminal_positive_fraction": (sum(value > 0 for value in terminal) / len(terminal)) if terminal else None,
        **derived,
        "transport_semantics": (
            "Aggregate measurements are transported directly to RD. The exact row-level derived "
            "dataset remains campaign-local and is advertised by derived_dataset_catalog for explicit "
            "RD-authored chaining into later Analysis requests."
        ),
        "interpretation_boundary":"LOOKAHEAD_MEASUREMENT_ONLY_RD_INTERPRETS",
    }


def classification_metrics(evidence_payloads: Mapping[str, object], parameters: Mapping[str, Any]) -> Mapping[str, Any]:
    rows=_rows(evidence_payloads); predicted=str(parameters["predicted_column"]); actual=str(parameters["actual_column"]); positive=parameters["positive_value"]; tp=tn=fp=fn=excluded=0
    for row in rows:
        if predicted not in row or actual not in row: excluded+=1; continue
        p=row[predicted]==positive; a=row[actual]==positive
        if p and a: tp+=1
        elif p and not a: fp+=1
        elif not p and a: fn+=1
        else: tn+=1
    n=tp+tn+fp+fn
    def ratio(a,b): return None if b==0 else a/b
    return {"n":n,"excluded":excluded,"true_positive":tp,"true_negative":tn,"false_positive":fp,"false_negative":fn,"accuracy":ratio(tp+tn,n),"precision":ratio(tp,tp+fp),"recall":ratio(tp,tp+fn),"specificity":ratio(tn,tn+fp),"interpretation_boundary":"PERFORMANCE_MEASUREMENT_ONLY_RD_INTERPRETS"}


def standard_method_catalog() -> MethodCatalog:
    return MethodCatalog([
        MethodSpec("analysis.descriptive.statistics",("NORMALIZED_DATASET",),"Compute descriptive summaries for RD-selected columns.",(ParameterContract("columns",True,(list,tuple),minimum_length=1,meaning="RD-selected numeric columns"),),1),
        MethodSpec("analysis.relationship.correlation",("NORMALIZED_DATASET",),"Measure pairwise Pearson or Spearman association without causal interpretation.",(ParameterContract("columns",True,(list,tuple),exact_length=2,meaning="two RD-selected numeric columns"),ParameterContract("correlation_type",True,(str,),allowed_values=("pearson","spearman"),meaning="statistic selected by RD")),2),
        MethodSpec("analysis.transform.percent_change",("NORMALIZED_DATASET",),"Compute backward-looking percent change for an RD-selected field and lag.",(ParameterContract("column",True,(str,),meaning="RD-selected numeric field"),ParameterContract("lag",True,(int,),minimum_value=1,meaning="RD-selected backward row lag")),2,metadata={"temporal_semantics":"present/prior rows only","reusable_derived_dataset":True}),
        MethodSpec("analysis.rolling.statistics",("NORMALIZED_DATASET",),"Compute a rolling statistic using an RD-selected field, window, and statistic.",(ParameterContract("column",True,(str,),meaning="RD-selected numeric field"),ParameterContract("window",True,(int,),minimum_value=1,meaning="RD-selected window"),ParameterContract("statistic",True,(str,),allowed_values=("mean","median","stddev_sample","minimum","maximum"),meaning="RD-selected statistic")),1,metadata={"reusable_derived_dataset":True}),
        MethodSpec("analysis.events.threshold",("NORMALIZED_DATASET",),"Identify rows satisfying an RD-authored numeric threshold condition.",(ParameterContract("column",True,(str,),meaning="RD-selected field"),ParameterContract("operator",True,(str,),allowed_values=("GT","GE","LT","LE"),meaning="RD-selected comparison"),ParameterContract("threshold",True,(int,float),meaning="RD-selected threshold")),1,metadata={"reusable_derived_dataset":True}),
        MethodSpec("analysis.path.forward_measurement",("NORMALIZED_DATASET",),"Exploration-only look-ahead path measurement over an RD-selected horizon and direction, returning exact aggregate statistics plus a campaign-local reusable derived observation dataset.",(ParameterContract("price_column",True,(str,),meaning="RD-selected price field"),ParameterContract("horizon",True,(int,),minimum_value=1,meaning="RD-selected forward rows"),ParameterContract("direction",True,(str,),allowed_values=("LONG","SHORT"),meaning="RD-selected directional frame")),2,True,False,True,{"scientific_selection":"none","output_shape":"bounded RD transport plus temporary reusable derived dataset","reusable_derived_dataset":True}),
        MethodSpec("analysis.performance.binary_classification",("NORMALIZED_DATASET",),"Measure binary classification performance for RD-selected predicted/actual fields and positive label.",(ParameterContract("predicted_column",True,(str,),meaning="RD-selected prediction field"),ParameterContract("actual_column",True,(str,),meaning="RD-selected outcome field"),ParameterContract("positive_value",True,(str,int,float,bool),meaning="RD-selected positive label")),1),
    ])


def standard_analysis_methods() -> tuple[RegisteredAnalysisMethod,...]:
    return tuple(RegisteredAnalysisMethod(method_id,implementation) for method_id,implementation in (
        ("analysis.descriptive.statistics",descriptive_statistics),("analysis.relationship.correlation",relationship_correlation),("analysis.transform.percent_change",percent_change_series),("analysis.rolling.statistics",rolling_statistics),("analysis.events.threshold",threshold_event_indices),("analysis.path.forward_measurement",forward_path_measurement),("analysis.performance.binary_classification",classification_metrics),
    ))
