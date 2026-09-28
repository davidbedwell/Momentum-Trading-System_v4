from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Mapping, Protocol, Sequence


class SearchGovernanceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Gene:
    gene_id: str
    values: tuple[Any, ...]
    feature_column: str | None = None
    meaning: str = ""

    def __post_init__(self) -> None:
        if not self.gene_id.strip() or not self.values:
            raise ValueError("gene requires nonblank id and at least one value")


@dataclass(frozen=True, slots=True)
class SearchSpace:
    search_space_id: str
    version: str
    family_id: str
    genes: tuple[Gene, ...]
    maximum_active_predicates: int = 4
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def canonical_payload(self) -> Mapping[str, Any]:
        return {
            "search_space_id": self.search_space_id,
            "version": self.version,
            "family_id": self.family_id,
            "genes": [asdict(g) for g in self.genes],
            "maximum_active_predicates": self.maximum_active_predicates,
            "attributes": dict(self.attributes),
        }

    @property
    def content_hash(self) -> str:
        raw = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    family_id: str
    genome: Mapping[str, Any]
    parent_ids: tuple[str, ...] = ()
    proposal_source: str = "UNKNOWN"

    @staticmethod
    def from_genome(*, family_id: str, genome: Mapping[str, Any], parent_ids: Sequence[str] = (), proposal_source: str) -> "Candidate":
        payload = {"family_id": family_id, "genome": dict(genome)}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        return Candidate(f"candidate:{digest}", family_id, dict(genome), tuple(parent_ids), proposal_source)


@dataclass(frozen=True, slots=True)
class Evaluation:
    candidate_id: str
    evidence_identity: str
    analysis_contract_version: str
    metrics: Mapping[str, Any]
    analysis_refs: tuple[str, ...] = ()

    @property
    def semantic_key(self) -> str:
        payload = {
            "candidate_id": self.candidate_id,
            "evidence_identity": self.evidence_identity,
            "analysis_contract_version": self.analysis_contract_version,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class EvaluationCache:
    def __init__(self) -> None:
        self._items: dict[str, Evaluation] = {}

    @staticmethod
    def key(candidate: Candidate, *, evidence_identity: str, analysis_contract_version: str) -> str:
        payload = {
            "candidate_id": candidate.candidate_id,
            "evidence_identity": evidence_identity,
            "analysis_contract_version": analysis_contract_version,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def get(self, candidate: Candidate, *, evidence_identity: str, analysis_contract_version: str) -> Evaluation | None:
        return self._items.get(self.key(candidate, evidence_identity=evidence_identity, analysis_contract_version=analysis_contract_version))

    def put(self, evaluation: Evaluation) -> None:
        existing = self._items.get(evaluation.semantic_key)
        if existing is not None and existing != evaluation:
            raise SearchGovernanceError("semantic evaluation key collision with different result")
        self._items[evaluation.semantic_key] = evaluation


@dataclass(frozen=True, slots=True)
class SearchLedgerEntry:
    sequence: int
    candidate_id: str
    proposal_source: str
    parent_ids: tuple[str, ...]
    cache_hit: bool
    metrics: Mapping[str, Any]


class SearchLedger:
    def __init__(self) -> None:
        self._entries: list[SearchLedgerEntry] = []

    def append(self, *, candidate: Candidate, cache_hit: bool, metrics: Mapping[str, Any]) -> SearchLedgerEntry:
        entry = SearchLedgerEntry(len(self._entries), candidate.candidate_id, candidate.proposal_source, candidate.parent_ids, cache_hit, dict(metrics))
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> tuple[SearchLedgerEntry, ...]:
        return tuple(self._entries)


class CandidateEvaluator(Protocol):
    analysis_contract_version: str
    def evaluate(self, candidate: Candidate, *, evidence_identity: str) -> Evaluation: ...


@dataclass(frozen=True, slots=True)
class SearchRunRequest:
    run_id: str
    optimizer_id: str
    search_space: SearchSpace
    evidence_identity: str
    scientific_cohort: str
    budget_evaluations: int
    seed: int

    def __post_init__(self) -> None:
        if self.scientific_cohort != "DISCOVERY":
            raise SearchGovernanceError("adaptive computational search is restricted to DISCOVERY")
        if self.budget_evaluations <= 0:
            raise ValueError("budget_evaluations must be positive")


@dataclass(frozen=True, slots=True)
class SearchRunResult:
    run_id: str
    optimizer_id: str
    search_space_hash: str
    proposed_count: int
    unique_count: int
    analysis_evaluation_count: int
    cache_hit_count: int
    ledger: tuple[SearchLedgerEntry, ...]


class SearchOptimizer(Protocol):
    optimizer_id: str
    def run(self, request: SearchRunRequest, evaluator: CandidateEvaluator, cache: EvaluationCache | None = None) -> SearchRunResult: ...


class RandomSearchOptimizer:
    """Reproducible baseline optimizer.

    This is deliberately scientifically stupid: it samples the declared search
    space and delegates every measurement to the evaluator/Analysis boundary.
    It exists as a benchmark against which evolutionary search must earn its
    additional complexity.
    """
    optimizer_id = "search.random.v1"

    def run(self, request: SearchRunRequest, evaluator: CandidateEvaluator, cache: EvaluationCache | None = None) -> SearchRunResult:
        cache = cache or EvaluationCache()
        rng = random.Random(request.seed)
        ledger = SearchLedger()
        seen: set[str] = set()
        analysis_count = 0
        cache_hits = 0
        for _ in range(request.budget_evaluations):
            genome = {gene.gene_id: rng.choice(gene.values) for gene in request.search_space.genes}
            candidate = Candidate.from_genome(family_id=request.search_space.family_id, genome=genome, proposal_source=self.optimizer_id)
            seen.add(candidate.candidate_id)
            evaluation = cache.get(candidate, evidence_identity=request.evidence_identity, analysis_contract_version=evaluator.analysis_contract_version)
            hit = evaluation is not None
            if evaluation is None:
                evaluation = evaluator.evaluate(candidate, evidence_identity=request.evidence_identity)
                cache.put(evaluation)
                analysis_count += 1
            else:
                cache_hits += 1
            ledger.append(candidate=candidate, cache_hit=hit, metrics=evaluation.metrics)
        return SearchRunResult(
            run_id=request.run_id,
            optimizer_id=self.optimizer_id,
            search_space_hash=request.search_space.content_hash,
            proposed_count=request.budget_evaluations,
            unique_count=len(seen),
            analysis_evaluation_count=analysis_count,
            cache_hit_count=cache_hits,
            ledger=ledger.entries,
        )


class CallableAnalysisAdapter:
    """Narrow adapter for existing governed Analysis-backed evaluation.

    The callable must execute the exact pre-authorized Analysis contract. This
    class does not calculate fitness, infer methods, or interpret results.
    """
    def __init__(self, *, analysis_contract_version: str, evaluate_callable: Callable[[Candidate, str], Evaluation]) -> None:
        self.analysis_contract_version = analysis_contract_version
        self._evaluate_callable = evaluate_callable

    def evaluate(self, candidate: Candidate, *, evidence_identity: str) -> Evaluation:
        result = self._evaluate_callable(candidate, evidence_identity)
        if result.candidate_id != candidate.candidate_id or result.evidence_identity != evidence_identity:
            raise SearchGovernanceError("Analysis adapter returned mismatched candidate/evidence identity")
        if result.analysis_contract_version != self.analysis_contract_version:
            raise SearchGovernanceError("Analysis adapter returned mismatched contract version")
        return result
