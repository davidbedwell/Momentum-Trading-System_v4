from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


PRIMARY_OPERATIONS = frozenset(
    {"BEGIN_BATCH_RESEARCH", "INTERPRET_BATCH_RESULTS", "REPAIR_BATCH_PLAN"}
)


@dataclass(frozen=True, slots=True)
class BlindedQwenCapabilityCase:
    case_id: str
    control_id: str
    operation: str
    prompt_sha256: str
    messages: tuple[Mapping[str, str], ...]
    independence_class: str

    def to_mapping(self) -> Mapping[str, object]:
        return asdict(self)


def _context_control_id(state_dir: Path) -> str:
    path = state_dir / "universe_scientific_context.json"
    if not path.is_file():
        return state_dir.name
    raw = json.loads(path.read_text(encoding="utf-8"))
    value = raw.get("calibration_control_id") if isinstance(raw, Mapping) else None
    return str(value).strip() if isinstance(value, str) and value.strip() else state_dir.name


def discover_control_state_dirs(
    *,
    campaign_roots: Iterable[str | Path] = (),
    state_dirs: Iterable[str | Path] = (),
    excluded_control_ids: Iterable[str] = (),
) -> tuple[Path, ...]:
    excluded = {value.strip() for value in excluded_control_ids if value.strip()}
    candidates: list[tuple[Path, bool]] = [
        (Path(value).expanduser().resolve(), True) for value in state_dirs
    ]
    for raw_root in campaign_roots:
        root = Path(raw_root).expanduser().resolve()
        if not root.is_dir():
            raise RuntimeError(f"Qwen capability campaign root is missing: {root}")
        candidates.extend(
            (path.parent, False)
            for path in sorted(root.glob("*/universe_scientific_context.json"))
        )

    selected: dict[str, Path] = {}
    for state_dir, explicitly_selected in candidates:
        if not state_dir.is_dir():
            raise RuntimeError(f"Qwen capability state directory is missing: {state_dir}")
        control_id = _context_control_id(state_dir)
        if control_id in excluded and not explicitly_selected:
            continue
        prior = selected.get(control_id)
        if prior is not None and prior != state_dir:
            raise RuntimeError(
                f"duplicate Qwen capability control state: {control_id}: {prior} and {state_dir}"
            )
        selected[control_id] = state_dir
    if not selected:
        raise RuntimeError("Qwen capability test selected no control states")
    return tuple(selected[key] for key in sorted(selected))


def blinded_cases_from_state_dirs(
    state_dirs: Iterable[str | Path],
) -> tuple[BlindedQwenCapabilityCase, ...]:
    cases: list[BlindedQwenCapabilityCase] = []
    for raw_state_dir in state_dirs:
        state_dir = Path(raw_state_dir).expanduser().resolve()
        control_id = _context_control_id(state_dir)
        replay_paths = tuple(
            path
            for path in (
                state_dir / "sol_replay_envelopes.jsonl",
                state_dir / "resume_sol_replay_envelopes.jsonl",
            )
            if path.is_file()
        )
        if not replay_paths:
            raise RuntimeError(f"control has no exact Sol replay envelopes: {state_dir}")
        case_sequence = 0
        for replay_path in replay_paths:
            for line_number, line in enumerate(
                replay_path.read_text(encoding="utf-8").splitlines(),
                start=1,
            ):
                if not line.strip():
                    continue
                raw = json.loads(line)
                operation = str(raw.get("operation", ""))
                if operation not in PRIMARY_OPERATIONS:
                    continue
                messages = raw.get("messages")
                if not isinstance(messages, list) or not messages:
                    raise RuntimeError(
                        f"replay envelope lacks exact messages: {replay_path}:{line_number}"
                    )
                clean_messages = tuple(
                    {"role": str(item["role"]), "content": str(item["content"])}
                    for item in messages
                    if isinstance(item, Mapping)
                    and "role" in item
                    and "content" in item
                )
                if len(clean_messages) != len(messages):
                    raise RuntimeError(
                        f"replay envelope contains invalid message: {replay_path}:{line_number}"
                    )
                case_sequence += 1
                encoded = json.dumps(
                    clean_messages,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                cases.append(
                    BlindedQwenCapabilityCase(
                        case_id=f"{control_id}:case:{case_sequence}",
                        control_id=control_id,
                        operation=operation,
                        prompt_sha256=hashlib.sha256(encoded).hexdigest(),
                        messages=clean_messages,
                        independence_class=(
                            "INDEPENDENT_INITIAL_PLANNING"
                            if operation == "BEGIN_BATCH_RESEARCH"
                            else "ISOLATED_STEP_REPLAY_WITH_SOL_AUTHORED_PRIOR_CONTEXT"
                        ),
                    )
                )
    return tuple(cases)


def mechanical_capability_report(
    observations: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    cases = len(observations)
    planning = sum(item.get("operation") == "BEGIN_BATCH_RESEARCH" for item in observations)
    interpretation = sum(
        item.get("operation") == "INTERPRET_BATCH_RESULTS" for item in observations
    )
    transport_failures = sum(not bool(item.get("transport_success")) for item in observations)
    decode_failures = sum(not bool(item.get("decision_decoded")) for item in observations)
    contract_failures = sum(
        bool(item.get("decision_decoded"))
        and not bool(item.get("objective_contract_valid"))
        for item in observations
    )
    if cases == 0:
        status = "NO_CASES"
    elif transport_failures:
        status = "QWEN_TRANSPORT_NOT_READY"
    elif decode_failures or contract_failures:
        status = "QWEN_REPRESENTATION_NOT_READY"
    elif planning == 0 or interpretation == 0:
        status = "QWEN_CAPABILITY_COVERAGE_INCOMPLETE"
    else:
        status = "READY_FOR_INDEPENDENT_SCIENTIFIC_REVIEW"
    return {
        "format": "MTS_V4_QWEN_CURRENT_CAPABILITY_REPORT_V1",
        "cases": cases,
        "independent_initial_planning_cases": planning,
        "isolated_interpretation_cases": interpretation,
        "transport_failures": transport_failures,
        "decode_failures": decode_failures,
        "objective_contract_failures": contract_failures,
        "analysis_operations_proposed": sum(
            int(item.get("analysis_operations_proposed", 0) or 0)
            for item in observations
        ),
        "mechanical_status": status,
        "scientific_grade": "AWAITING_INDEPENDENT_REVIEW",
        "end_to_end_qwen_autonomy_tested": False,
        "sol_fallback_allowed": False,
        "hidden_control_answers_supplied_to_qwen": False,
        "sol_responses_supplied_to_qwen": False,
        "authority": (
            "Mechanical replay readiness only. Scientific usefulness and end-to-end autonomy "
            "require separate blinded assessment and a fresh Qwen-only campaign."
        ),
    }
