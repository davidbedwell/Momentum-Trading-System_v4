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


@dataclass(frozen=True, slots=True)
class EvolutionaryConfig:
    population_size: int = 32
    elite_count: int = 6
    tournament_size: int = 3
    mutation_probability: float = 0.20
    crossover_probability: float = 0.80
    fitness_metric: str = "net_expectancy"

    def __post_init__(self) -> None:
        if self.population_size < 2:
            raise ValueError("population_size must be at least 2")
        if not 1 <= self.elite_count < self.population_size:
            raise ValueError("elite_count must be within population")
        if not 1 <= self.tournament_size <= self.population_size:
            raise ValueError("invalid tournament_size")
        if not 0.0 <= self.mutation_probability <= 1.0:
            raise ValueError("invalid mutation_probability")
        if not 0.0 <= self.crossover_probability <= 1.0:
            raise ValueError("invalid crossover_probability")


class EvolutionarySearchOptimizer:
    """Governed evolutionary search over an explicitly declared SearchSpace.

    Selection is mechanical and uses one predeclared numeric metric. It does not
    infer scientific meaning, change objectives mid-run, or inspect evidence
    directly. Every phenotype is measured only through CandidateEvaluator.
    """
    optimizer_id = "search.evolutionary.v1"

    def __init__(self, config: EvolutionaryConfig | None = None) -> None:
        self.config = config or EvolutionaryConfig()

    def _random_candidate(self, space: SearchSpace, rng: random.Random) -> Candidate:
        genome = {g.gene_id: rng.choice(g.values) for g in space.genes}
        return Candidate.from_genome(family_id=space.family_id, genome=genome, proposal_source=self.optimizer_id)

    def _score(self, evaluation: Evaluation) -> float:
        value = evaluation.metrics.get(self.config.fitness_metric)
        if not isinstance(value, (int, float)):
            raise SearchGovernanceError(f"fitness metric {self.config.fitness_metric!r} is missing or nonnumeric")
        return float(value)

    def _breed(self, a: Candidate, b: Candidate, space: SearchSpace, rng: random.Random) -> Candidate:
        child: dict[str, Any] = {}
        for gene in space.genes:
            if rng.random() < self.config.crossover_probability:
                value = rng.choice((a.genome[gene.gene_id], b.genome[gene.gene_id]))
            else:
                value = a.genome[gene.gene_id]
            if rng.random() < self.config.mutation_probability:
                value = rng.choice(gene.values)
            child[gene.gene_id] = value
        return Candidate.from_genome(
            family_id=space.family_id,
            genome=child,
            parent_ids=(a.candidate_id, b.candidate_id),
            proposal_source=self.optimizer_id,
        )

    def run(self, request: SearchRunRequest, evaluator: CandidateEvaluator, cache: EvaluationCache | None = None) -> SearchRunResult:
        cache = cache or EvaluationCache()
        rng = random.Random(request.seed)
        ledger = SearchLedger()
        seen: set[str] = set()
        analysis_count = 0
        cache_hits = 0

        def measure(candidate: Candidate) -> tuple[Candidate, Evaluation]:
            nonlocal analysis_count, cache_hits
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
            return candidate, evaluation

        population = [self._random_candidate(request.search_space, rng) for _ in range(min(self.config.population_size, request.budget_evaluations))]
        evaluated = [measure(c) for c in population]
        proposals = len(evaluated)

        def tournament(items: list[tuple[Candidate, Evaluation]]) -> Candidate:
            contenders = [rng.choice(items) for _ in range(self.config.tournament_size)]
            return max(contenders, key=lambda pair: self._score(pair[1]))[0]

        while proposals < request.budget_evaluations:
            ranked = sorted(evaluated, key=lambda pair: self._score(pair[1]), reverse=True)
            next_candidates = [pair[0] for pair in ranked[: min(self.config.elite_count, len(ranked))]]
            while len(next_candidates) < self.config.population_size and proposals + len(next_candidates) < request.budget_evaluations + len(ranked[: min(self.config.elite_count, len(ranked))]):
                next_candidates.append(self._breed(tournament(evaluated), tournament(evaluated), request.search_space, rng))
            remaining = request.budget_evaluations - proposals
            # Elites are retained state, not new proposals/evaluations.
            children = next_candidates[min(self.config.elite_count, len(next_candidates)) :][:remaining]
            if not children:
                children = [self._breed(tournament(evaluated), tournament(evaluated), request.search_space, rng)]
            evaluated = ranked[: self.config.elite_count] + [measure(c) for c in children]
            proposals += len(children)

        return SearchRunResult(
            run_id=request.run_id,
            optimizer_id=self.optimizer_id,
            search_space_hash=request.search_space.content_hash,
            proposed_count=proposals,
            unique_count=len(seen),
            analysis_evaluation_count=analysis_count,
            cache_hit_count=cache_hits,
            ledger=ledger.entries,
        )


@dataclass(frozen=True, slots=True)
class NullControlResult:
    control_id: str
    seed: int
    search_result: SearchRunResult


class NullControlEvaluator:
    """Wrap an Analysis evaluator with an explicit null-evidence identity.

    Outcome permutation/shuffling itself belongs in the governed Analysis/data
    preparation layer. Search receives only the resulting null evidence identity,
    preventing the optimizer from manipulating outcomes.
    """
    def __init__(self, base: CandidateEvaluator, *, null_evidence_identity: str) -> None:
        if not null_evidence_identity.startswith("null:"):
            raise SearchGovernanceError("null evidence identity must be explicitly namespaced")
        self.base = base
        self.null_evidence_identity = null_evidence_identity
        self.analysis_contract_version = base.analysis_contract_version

    def evaluate(self, candidate: Candidate, *, evidence_identity: str) -> Evaluation:
        if evidence_identity != self.null_evidence_identity:
            raise SearchGovernanceError("null evaluator used with nonmatching evidence identity")
        return self.base.evaluate(candidate, evidence_identity=evidence_identity)


def run_null_search_control(
    *, control_id: str, optimizer: SearchOptimizer, request: SearchRunRequest,
    evaluator: CandidateEvaluator, null_evidence_identity: str,
    cache: EvaluationCache | None = None,
) -> NullControlResult:
    null_request = SearchRunRequest(
        run_id=f"{request.run_id}:null:{control_id}",
        optimizer_id=request.optimizer_id,
        search_space=request.search_space,
        evidence_identity=null_evidence_identity,
        scientific_cohort=request.scientific_cohort,
        budget_evaluations=request.budget_evaluations,
        seed=request.seed,
    )
    wrapped = NullControlEvaluator(evaluator, null_evidence_identity=null_evidence_identity)
    return NullControlResult(control_id, request.seed, optimizer.run(null_request, wrapped, cache))
