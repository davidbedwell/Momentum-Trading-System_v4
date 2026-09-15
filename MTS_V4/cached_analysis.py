from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from typing import Mapping
from uuid import uuid4

from .contracts import AnalysisRequest, AnalysisResult
from .lineage_analysis import LineageAwareExactMethodAnalysisExecutor


class CachedLineageAwareAnalysisExecutor(LineageAwareExactMethodAnalysisExecutor):
    """Campaign-local exact-specification result reuse.

    The cache performs no fuzzy matching and no scientific substitution. Only an
    identical subject/method/evidence/parameter/input-lineage specification is a
    hit. A hit receives a fresh result/request identity so orchestrator lineage
    remains correct while deterministic arithmetic is not repeated.
    """

    def __init__(self) -> None:
        super().__init__()
        self._result_cache: dict[str, AnalysisResult] = {}
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _key(request: AnalysisRequest) -> str:
        payload = {
            "subject_id": request.subject_id,
            "method_id": request.method_id,
            "evidence_ids": list(request.evidence_ids),
            "parameters": request.parameters,
            "research_phase": request.research_phase.value,
            "analysis_inputs": [asdict(item) for item in request.analysis_inputs],
        }
        encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def execute(self, request: AnalysisRequest, evidence_payloads: Mapping[str, object]) -> AnalysisResult:
        key = self._key(request)
        prior = self._result_cache.get(key)
        if prior is not None:
            self._hits += 1
            metadata = dict(prior.execution_metadata)
            metadata.update(
                {
                    "deterministic_cache_hit": True,
                    "cached_from_result_id": prior.result_id,
                    "analysis_cache_key": key,
                }
            )
            return replace(
                prior,
                result_id=f"analysis-result:{uuid4().hex}",
                request_id=request.request_id,
                execution_metadata=metadata,
            )
        self._misses += 1
        result = super().execute(request, evidence_payloads)
        metadata = dict(result.execution_metadata)
        metadata.update({"deterministic_cache_hit": False, "analysis_cache_key": key})
        result = replace(result, execution_metadata=metadata)
        if result.execution_metadata.get("execution_status") == "SUCCESS":
            self._result_cache[key] = result
        return result

    def cache_stats(self) -> Mapping[str, int]:
        return {"hits": self._hits, "misses": self._misses, "entries": len(self._result_cache)}
