from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import EvidenceDescriptor, SubjectMetadata
from .cross_subject_memory_store import (
    CrossSubjectMemorySnapshotSelection,
    JsonCrossSubjectScientificMemoryStore,
)
from .nexus_json import JsonResearchNexus
from .research_package_store import JsonResearchPackageStore
from .sol_batch_provider import SolBatchResearchDirector


@dataclass(frozen=True, slots=True)
class SubjectScientificContextBundle:
    """Canonical cross-subject scientific context for any active subject.

    This bundle contains durable scientific interpretation and provenance only.
    It deliberately excludes raw rows and reusable Analysis payloads. Scientific
    ranking, hypothesis choice, and generalization remain AI Research Director
    responsibilities.
    """

    active_subject_id: str
    memory_selection: CrossSubjectMemorySnapshotSelection
    prior_subject_science: Mapping[str, object]
    same_subject_prior_science: Mapping[str, object] | None = None


class SubjectContextSolBatchResearchDirector(SolBatchResearchDirector):
    """Sol batch RD with permanent prior-subject scientific context injection."""

    def __init__(
        self,
        *args,
        prior_subject_scientific_context: Mapping[str, object],
        same_subject_prior_scientific_context: Mapping[str, object] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._prior_subject_scientific_context = dict(prior_subject_scientific_context)
        self._same_subject_prior_scientific_context = (
            dict(same_subject_prior_scientific_context)
            if same_subject_prior_scientific_context is not None
            else None
        )

    def _batch_common_payload(
        self,
        *,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        available_methods: Sequence[Mapping[str, Any]],
        nexus_context: Mapping[str, object],
        continuation: bool = False,
    ) -> dict[str, object]:
        payload = super()._batch_common_payload(
            subject=subject,
            evidence=evidence,
            available_methods=available_methods,
            nexus_context=nexus_context,
            continuation=continuation,
        )
        if continuation:
            payload["prior_science_transport"] = {
                "full_prior_subject_science_sent_on_begin": True,
                "full_same_subject_revisit_science_sent_on_begin": (
                    self._same_subject_prior_scientific_context is not None
                ),
                "later_scientific_continuity_is_ai_authored": True,
            }
        else:
            payload["prior_subject_scientific_context"] = self._prior_subject_scientific_context
            if self._same_subject_prior_scientific_context is not None:
                payload["same_subject_prior_science"] = self._same_subject_prior_scientific_context
        return payload


def _subject_id_from_package(document: Mapping[str, object]) -> str | None:
    value = document.get("subject_id")
    return value if isinstance(value, str) and value.strip() else None


def _unwrap_research_package(raw: Mapping[str, object]) -> Mapping[str, object] | None:
    if raw.get("format") == JsonResearchPackageStore.FORMAT:
        wrapped = raw.get("research_package")
        return wrapped if isinstance(wrapped, Mapping) else None
    return raw


def _compact_scientific_package(
    package: Mapping[str, object],
    *,
    source_path: Path,
) -> Mapping[str, object] | None:
    subject_id = _subject_id_from_package(package)
    if subject_id is None:
        return None

    def list_field(name: str) -> list[object]:
        value = package.get(name, [])
        return value if isinstance(value, list) else []

    return {
        "source_path": str(source_path),
        "subject_id": subject_id,
        "rp_id": package.get("rp_id"),
        "campaign_id": package.get("campaign_id"),
        "parent_rp_id": package.get("parent_rp_id"),
        "status": package.get("status"),
        "originating_question": package.get("originating_question"),
        "originating_rationale": package.get("originating_rationale"),
        "hypotheses": list_field("hypotheses"),
        "predictive_hypotheses": list_field("predictive_hypotheses"),
        "findings": list_field("findings"),
        "unresolved_issues": list_field("unresolved_issues"),
        "close_reason": package.get("close_reason"),
        "final_assessment": package.get("final_assessment"),
    }


def load_prior_subject_science(
    root: str | Path,
    *,
    active_subject_id: str,
) -> Mapping[str, object]:
    """Load compact durable scientific outputs from all other subjects.

    Exact duplicate package documents are exposed once. No deterministic code
    ranks subjects, findings, hypotheses, or packages. Analysis lineage payloads
    and raw market rows are intentionally omitted from this cross-subject view.
    """
    root_path = Path(root)
    packages_by_subject: dict[str, list[Mapping[str, object]]] = {}
    seen: set[str] = set()

    for path in sorted(root_path.glob("mts-v4-*/**/research_packages/*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(raw, Mapping):
            continue
        package = _unwrap_research_package(raw)
        if package is None:
            continue
        compact = _compact_scientific_package(package, source_path=path)
        if compact is None:
            continue
        subject_id = str(compact["subject_id"])
        if subject_id == active_subject_id:
            continue

        fingerprint = json.dumps(
            {key: value for key, value in compact.items() if key != "source_path"},
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        )
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        packages_by_subject.setdefault(subject_id, []).append(compact)

    return {
        "policy": {
            "authority": "EXACT_DURABLE_PRIOR_SUBJECT_SCIENCE",
            "raw_rows_present": False,
            "reusable_analysis_payloads_present": False,
            "deterministic_scientific_ranking": False,
            "mandatory_research_agenda": False,
            "rd_may_test_challenge_reformulate_condition_defer_or_ignore": True,
        },
        "subjects": [
            {
                "subject_id": subject_id,
                "research_packages": packages_by_subject[subject_id],
            }
            for subject_id in sorted(packages_by_subject)
        ],
    }


def load_same_subject_prior_science(
    root: str | Path,
    *,
    active_subject_id: str,
) -> Mapping[str, object]:
    """Load nonbinding durable history for an explicitly designated revisit.

    Research Packages carry the subject's questions and scientific lifecycle.
    Nexus files are also inspected because an RD-promoted finding can be durable
    there without appearing in its package. Nexus findings already represented
    in a package are not repeated. Conflicting reuse of one finding_id fails
    closed instead of allowing deterministic code to choose a scientific record.
    """
    root_path = Path(root)
    research_packages: list[Mapping[str, object]] = []
    seen_packages: set[str] = set()
    package_finding_ids: set[str] = set()

    for path in sorted(root_path.glob("mts-v4-*/**/research_packages/*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(raw, Mapping):
            continue
        package = _unwrap_research_package(raw)
        if package is None:
            continue
        compact = _compact_scientific_package(package, source_path=path)
        if compact is None or compact["subject_id"] != active_subject_id:
            continue
        fingerprint = json.dumps(
            {key: value for key, value in compact.items() if key != "source_path"},
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        )
        if fingerprint in seen_packages:
            continue
        seen_packages.add(fingerprint)
        research_packages.append(compact)
        for finding in compact.get("findings", []):
            if isinstance(finding, Mapping):
                finding_id = finding.get("finding_id")
                if isinstance(finding_id, str) and finding_id.strip():
                    package_finding_ids.add(finding_id)

    nexus_findings: list[Mapping[str, object]] = []
    nexus_by_id: dict[str, tuple[str, Mapping[str, object]]] = {}
    nexus_without_id: set[str] = set()
    for path in sorted(root_path.glob("mts-v4-*/**/research_nexus.json")):
        try:
            nexus = JsonResearchNexus(path)
        except Exception:
            continue
        for finding in nexus.findings_for_subject(active_subject_id):
            compact_finding: Mapping[str, object] = {
                **asdict(finding),
                "status": "ACTIVE",
                "source_path": str(path),
            }
            finding_id = finding.finding_id.strip()
            scientific_content = {
                key: value for key, value in compact_finding.items() if key != "source_path"
            }
            fingerprint = json.dumps(
                scientific_content,
                sort_keys=True,
                default=str,
                separators=(",", ":"),
            )
            if finding_id:
                previous = nexus_by_id.get(finding_id)
                if previous is not None and previous[0] != fingerprint:
                    raise RuntimeError(
                        "conflicting durable Nexus findings reuse finding_id "
                        f"{finding_id!r} for {active_subject_id}"
                    )
                nexus_by_id.setdefault(finding_id, (fingerprint, compact_finding))
                continue
            if fingerprint not in nexus_without_id:
                nexus_without_id.add(fingerprint)
                nexus_findings.append(compact_finding)

    nexus_findings.extend(
        compact
        for finding_id, (_, compact) in sorted(nexus_by_id.items())
        if finding_id not in package_finding_ids
    )

    return {
        "subject_id": active_subject_id,
        "research_packages": research_packages,
        "nexus_only_findings": nexus_findings,
        "policy": {
            "authority": "NONBINDING_SAME_SUBJECT_HISTORICAL_SCIENCE",
            "revisit_only": True,
            "raw_rows_present": False,
            "reusable_analysis_payloads_present": False,
            "deterministic_scientific_ranking": False,
            "mandatory_retest_agenda": False,
            "rd_may_test_challenge_reformulate_condition_defer_ignore_or_reject": True,
        },
    }


def load_subject_scientific_context(
    root: str | Path,
    *,
    active_subject_id: str,
    include_same_subject_prior_science: bool = False,
) -> SubjectScientificContextBundle:
    """Return the permanent scientific-context bundle for any subject-level RD run."""
    memory_selection = JsonCrossSubjectScientificMemoryStore.discover_current(root)
    if memory_selection is None:
        raise RuntimeError("no canonical cross-subject scientific memory snapshot is available")

    return SubjectScientificContextBundle(
        active_subject_id=active_subject_id,
        memory_selection=memory_selection,
        prior_subject_science=load_prior_subject_science(
            root,
            active_subject_id=active_subject_id,
        ),
        same_subject_prior_science=(
            load_same_subject_prior_science(root, active_subject_id=active_subject_id)
            if include_same_subject_prior_science
            else None
        ),
    )


def load_recorded_cross_subject_memory(
    retrospective_context: object,
) -> JsonCrossSubjectScientificMemoryStore:
    """Reload the exact memory snapshot recorded when a subject campaign started.

    Resume/continuation must preserve scientific context across process boundaries.
    If provenance is absent or the recorded snapshot is unavailable, fail closed
    instead of silently substituting a different current memory state.
    """
    if not isinstance(retrospective_context, Mapping):
        raise RuntimeError("retrospective context is not an object")
    provenance = retrospective_context.get("cross_subject_memory_provenance")
    if not isinstance(provenance, Mapping):
        raise RuntimeError(
            "retrospective campaign lacks canonical cross-subject memory provenance; "
            "refusing to resume with changed scientific context"
        )
    source_path = provenance.get("source_path")
    if not isinstance(source_path, str) or not source_path.strip():
        raise RuntimeError("retrospective campaign cross-subject memory provenance lacks source_path")
    path = Path(source_path).expanduser().resolve()
    if not path.is_file():
        raise RuntimeError(f"recorded canonical cross-subject memory snapshot is missing: {path}")
    return JsonCrossSubjectScientificMemoryStore(path)
