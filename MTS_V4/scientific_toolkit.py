from __future__ import annotations

import importlib
import inspect
import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodSpec, ParameterContract


TOOLKIT_METHOD_ID = "analysis.toolkit.scientific_function"
_TOOLKIT_NAMESPACES = (
    "scipy.stats",
    "scipy.signal",
    "scipy.special",
    "scipy.fft",
    "scipy.spatial.distance",
)

# Mechanical execution-safety exclusions only. These names create arbitrarily
# large synthetic sequences or require user-supplied Python callables rather
# than operating directly on supplied evidence values.
_BLOCKED_TOOL_NAMES = {
    "max_len_seq",
    "unit_impulse",
    "vectorstrength",
}


class ScientificToolkitError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ScientificTool:
    tool_id: str
    namespace: str
    name: str
    signature: str
    summary: str
    callable_object: Any

    def capability_string(self) -> str:
        signature = self.signature.replace("\n", " ")[:220]
        summary = self.summary.replace("\n", " ")[:140]
        return f"{self.tool_id}{signature} :: {summary}"


def _public_calculation_tools() -> tuple[ScientificTool, ...]:
    try:
        import numpy as np
    except ImportError as exc:
        raise ScientificToolkitError("numpy is required for the scientific calculation toolkit") from exc

    tools: list[ScientificTool] = []
    for namespace in _TOOLKIT_NAMESPACES:
        try:
            module = importlib.import_module(namespace)
        except ImportError as exc:
            raise ScientificToolkitError(
                f"{namespace} is required for the scientific calculation toolkit"
            ) from exc

        for name in sorted(dir(module)):
            if name.startswith("_") or name in _BLOCKED_TOOL_NAMES:
                continue
            obj = getattr(module, name)
            if not (inspect.isfunction(obj) or isinstance(obj, np.ufunc)):
                continue
            try:
                signature = str(inspect.signature(obj))
            except (TypeError, ValueError):
                if isinstance(obj, np.ufunc):
                    signature = f"(<{obj.nin} positional inputs>)"
                else:
                    continue
            doc = inspect.getdoc(obj) or ""
            summary = doc.splitlines()[0].strip() if doc else "Public numerical calculation function."
            tools.append(
                ScientificTool(
                    tool_id=f"{namespace}.{name}",
                    namespace=namespace,
                    name=name,
                    signature=signature,
                    summary=summary,
                    callable_object=obj,
                )
            )

    # Stable deterministic order is representation/execution behavior only.
    return tuple(sorted(tools, key=lambda item: item.tool_id))


def scientific_tool_index() -> tuple[str, ...]:
    """Compact capability index supplied to RD.

    Each entry is a real installed calculation function. Presence in this index
    is not a recommendation and carries no scientific ranking or significance.
    """

    return tuple(tool.capability_string() for tool in _public_calculation_tools())


def scientific_tool_count() -> int:
    return len(_public_calculation_tools())


def scientific_toolkit_method_spec() -> MethodSpec:
    tools = _public_calculation_tools()
    tool_ids = tuple(tool.tool_id for tool in tools)
    return MethodSpec(
        method_id=TOOLKIT_METHOD_ID,
        artifact_types=("NORMALIZED_DATASET",),
        description=(
            "Invoke one exact public numerical function from the installed scientific toolkit. "
            "RD selects the function and supplies every scientifically meaningful argument."
        ),
        parameters=(
            ParameterContract(
                "tool_id",
                True,
                (str,),
                allowed_values=tool_ids,
                meaning="exact calculation function selected by RD from metadata.tool_index",
            ),
            ParameterContract(
                "args",
                True,
                (list, tuple),
                minimum_length=0,
                meaning=(
                    "ordered function arguments authored by RD; use {\"column\": \"field\"} "
                    "to bind a complete evidence column, otherwise supply a literal value"
                ),
            ),
            ParameterContract(
                "kwargs",
                False,
                (dict,),
                meaning=(
                    "named function arguments authored by RD; values may contain "
                    "{\"column\": \"field\"} bindings or literal values"
                ),
            ),
        ),
        minimum_sample=1,
        metadata={
            "tool_count": len(tools),
            "tool_index": [tool.capability_string() for tool in tools],
            "argument_contract": {
                "column_binding": {"column": "exact schema field name"},
                "literal_values": "passed exactly as authored by RD",
                "args": "resolved then passed positionally in RD-authored order",
                "kwargs": "resolved then passed by RD-authored key",
                "missing_value_policy": (
                    "No rows are silently dropped or imputed. The selected library function receives "
                    "the supplied column values as represented; RD must explicitly choose preprocessing "
                    "or function nan-policy parameters when scientifically relevant."
                ),
            },
            "scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY",
            "deterministic_ranking": False,
            "execution_safety": (
                "Only public numerical functions from the listed installed namespaces are exposed; "
                "functions requiring arbitrary user Python callbacks or unbounded synthetic-sequence "
                "generation may be excluded mechanically."
            ),
        },
    )


def _single_rows(evidence_payloads: Mapping[str, object]) -> tuple[Mapping[str, Any], ...]:
    if len(evidence_payloads) != 1:
        raise ScientificToolkitError("scientific toolkit invocation requires exactly one evidence payload")
    payload = next(iter(evidence_payloads.values()))
    rows = tuple(payload)  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ScientificToolkitError("evidence payload must be an iterable of row mappings")
    return rows


def _resolve(value: Any, rows: Sequence[Mapping[str, Any]]) -> Any:
    if isinstance(value, Mapping):
        if set(value) == {"column"}:
            column = str(value["column"])
            if any(column not in row for row in rows):
                raise ScientificToolkitError(f"requested column does not exist in every row: {column}")
            try:
                import numpy as np
            except ImportError as exc:
                raise ScientificToolkitError("numpy is required for column bindings") from exc
            return np.asarray([row[column] for row in rows])
        return {str(key): _resolve(item, rows) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve(item, rows) for item in value]
    if isinstance(value, tuple):
        return tuple(_resolve(item, rows) for item in value)
    return value


def _json_safe(value: Any, *, depth: int = 0) -> Any:
    if depth > 12:
        return repr(value)
    try:
        import numpy as np
    except ImportError:
        np = None  # type: ignore[assignment]

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if np is not None:
        if isinstance(value, np.generic):
            return _json_safe(value.item(), depth=depth + 1)
        if isinstance(value, np.ndarray):
            if value.size > 100_000:
                raise ScientificToolkitError(
                    f"tool output has {value.size} elements; hard execution limit is 100000"
                )
            return _json_safe(value.tolist(), depth=depth + 1)
    if hasattr(value, "_asdict"):
        return _json_safe(value._asdict(), depth=depth + 1)
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v, depth=depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        if len(value) > 100_000:
            raise ScientificToolkitError(
                f"tool output has {len(value)} elements; hard execution limit is 100000"
            )
        return [_json_safe(item, depth=depth + 1) for item in value]
    if hasattr(value, "tolist"):
        return _json_safe(value.tolist(), depth=depth + 1)
    return repr(value)


def execute_scientific_toolkit(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    rows = _single_rows(evidence_payloads)
    tool_id = str(parameters["tool_id"])
    registry = {tool.tool_id: tool for tool in _public_calculation_tools()}
    try:
        tool = registry[tool_id]
    except KeyError as exc:
        raise ScientificToolkitError(f"tool_id is not available: {tool_id}") from exc

    args = _resolve(list(parameters["args"]), rows)
    kwargs = _resolve(dict(parameters.get("kwargs", {})), rows)
    try:
        result = tool.callable_object(*args, **kwargs)
    except Exception as exc:
        raise ScientificToolkitError(
            f"{tool_id} rejected the RD-authored invocation: {type(exc).__name__}: {exc}"
        ) from exc

    return {
        "tool_id": tool_id,
        "signature": tool.signature,
        "result": _json_safe(result),
        "interpretation_boundary": "CALCULATION_ONLY_RD_INTERPRETS",
    }


def scientific_toolkit_analysis_method() -> RegisteredAnalysisMethod:
    return RegisteredAnalysisMethod(TOOLKIT_METHOD_ID, execute_scientific_toolkit)
