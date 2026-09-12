from __future__ import annotations

from dataclasses import dataclass
import math
import os
from typing import Callable, Mapping


DEFAULT_AUTHORIZED_SOL_SPEND_USD = 20.0
DEFAULT_SOL_INPUT_USD_PER_MILLION = 4.0
DEFAULT_SOL_CACHED_INPUT_USD_PER_MILLION = 0.40
DEFAULT_SOL_OUTPUT_USD_PER_MILLION = 20.0
LONG_CONTEXT_INPUT_TOKEN_THRESHOLD = 272_000
LONG_CONTEXT_INPUT_MULTIPLIER = 2.0
LONG_CONTEXT_OUTPUT_MULTIPLIER = 1.5


@dataclass(frozen=True, slots=True)
class SolResearchProgressEstimate:
    """Sol's scientific estimate of how much of the subject program remains."""

    estimated_percent_complete: float
    estimated_remaining_batches: int
    estimated_remaining_sol_calls: int
    estimate_confidence: str
    estimate_rationale: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.estimated_percent_complete <= 100.0:
            raise ValueError("estimated_percent_complete must be between 0 and 100")
        if self.estimated_remaining_batches < 0:
            raise ValueError("estimated_remaining_batches cannot be negative")
        if self.estimated_remaining_sol_calls < 0:
            raise ValueError("estimated_remaining_sol_calls cannot be negative")
        if not self.estimate_confidence.strip():
            raise ValueError("estimate_confidence cannot be blank")
        if not self.estimate_rationale.strip():
            raise ValueError("estimate_rationale cannot be blank")


@dataclass(frozen=True, slots=True)
class SolSpendAuthorizationSnapshot:
    authorized_spend_usd: float
    actual_spend_usd: float
    completed_sol_calls: int
    average_completed_call_cost_usd: float | None
    estimated_percent_complete: float | None
    estimated_remaining_batches: int | None
    estimated_remaining_sol_calls: int | None
    estimate_confidence: str | None
    estimate_rationale: str | None
    estimated_additional_spend_low_usd: float | None
    estimated_additional_spend_high_usd: float | None
    estimated_total_spend_low_usd: float | None
    estimated_total_spend_high_usd: float | None
    recommended_authorized_ceiling_usd: float | None


class SolSpendAuthorizationRequired(RuntimeError):
    """Raised before another Sol call when the human-authorized spend is insufficient."""

    def __init__(self, snapshot: SolSpendAuthorizationSnapshot) -> None:
        self.snapshot = snapshot
        super().__init__(
            "human Sol-spend authorization required before another premium-model call"
        )


HumanSpendAuthorizationCallback = Callable[[SolSpendAuthorizationSnapshot], float | None]


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    value = float(raw)
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


class SolSpendGuard:
    """Human-owned dollar authorization boundary for premium Sol calls.

    Scientific breadth is never limited here. The guard only decides whether a
    further premium-model call is financially authorized. Sol supplies scientific
    progress/remaining-work estimates; deterministic code combines those estimates
    with provider-reported token usage and configured token prices.
    """

    def __init__(
        self,
        *,
        authorized_spend_usd: float = DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        authorization_callback: HumanSpendAuthorizationCallback | None = None,
    ) -> None:
        if authorized_spend_usd <= 0:
            raise ValueError("authorized_spend_usd must be positive")
        self._authorized_spend_usd = float(authorized_spend_usd)
        self._authorization_callback = authorization_callback
        self._call_costs: list[float] = []
        self._progress: SolResearchProgressEstimate | None = None

    @property
    def authorized_spend_usd(self) -> float:
        return self._authorized_spend_usd

    @property
    def actual_spend_usd(self) -> float:
        return sum(self._call_costs)

    @property
    def completed_sol_calls(self) -> int:
        return len(self._call_costs)

    def authorize_through(self, new_ceiling_usd: float) -> None:
        value = float(new_ceiling_usd)
        if value <= self._authorized_spend_usd:
            raise ValueError("new Sol spend authorization must increase the current ceiling")
        if value <= self.actual_spend_usd:
            raise ValueError("new Sol spend authorization must exceed actual spend to date")
        self._authorized_spend_usd = value

    def update_research_progress(self, progress: SolResearchProgressEstimate) -> None:
        self._progress = progress

    @staticmethod
    def _usage_tokens(usage: Mapping[str, object]) -> tuple[int, int, int]:
        input_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
        output_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
        try:
            input_count = int(input_tokens or 0)
            output_count = int(output_tokens or 0)
        except (TypeError, ValueError) as exc:
            raise ValueError("provider usage token counts must be numeric") from exc

        cached_count = 0
        details = usage.get("prompt_tokens_details", usage.get("input_tokens_details"))
        if isinstance(details, Mapping):
            raw_cached = details.get("cached_tokens", 0)
            try:
                cached_count = int(raw_cached or 0)
            except (TypeError, ValueError) as exc:
                raise ValueError("provider cached token count must be numeric") from exc
        cached_count = max(0, min(cached_count, input_count))
        return input_count, cached_count, output_count

    @classmethod
    def estimate_usage_cost_usd(cls, usage: Mapping[str, object]) -> float:
        input_tokens, cached_tokens, output_tokens = cls._usage_tokens(usage)
        uncached_tokens = max(0, input_tokens - cached_tokens)

        input_rate = _env_float(
            "MTS_SOL_INPUT_USD_PER_MILLION",
            DEFAULT_SOL_INPUT_USD_PER_MILLION,
        )
        cached_rate = _env_float(
            "MTS_SOL_CACHED_INPUT_USD_PER_MILLION",
            DEFAULT_SOL_CACHED_INPUT_USD_PER_MILLION,
        )
        output_rate = _env_float(
            "MTS_SOL_OUTPUT_USD_PER_MILLION",
            DEFAULT_SOL_OUTPUT_USD_PER_MILLION,
        )
        input_multiplier = 1.0
        output_multiplier = 1.0
        if input_tokens > LONG_CONTEXT_INPUT_TOKEN_THRESHOLD:
            input_multiplier = LONG_CONTEXT_INPUT_MULTIPLIER
            output_multiplier = LONG_CONTEXT_OUTPUT_MULTIPLIER

        return (
            (uncached_tokens / 1_000_000.0) * input_rate * input_multiplier
            + (cached_tokens / 1_000_000.0) * cached_rate * input_multiplier
            + (output_tokens / 1_000_000.0) * output_rate * output_multiplier
        )

    def record_provider_usage(self, usage: Mapping[str, object] | None) -> float | None:
        if not isinstance(usage, Mapping):
            return None
        cost = self.estimate_usage_cost_usd(usage)
        self._call_costs.append(cost)
        return cost

    def _projection_range(self) -> tuple[float | None, float | None]:
        if not self._call_costs or self._progress is None:
            return None, None

        actual = self.actual_spend_usd
        average_call = actual / len(self._call_costs)
        estimates: list[float] = []

        remaining_calls = self._progress.estimated_remaining_sol_calls
        estimates.append(max(0.0, average_call * remaining_calls))

        pct = self._progress.estimated_percent_complete
        if 0.0 < pct < 100.0:
            progress_based_remaining = max(0.0, actual * ((100.0 - pct) / pct))
            estimates.append(progress_based_remaining)
        elif pct >= 100.0:
            estimates.append(0.0)

        if not estimates:
            return None, None
        return min(estimates), max(estimates)

    def snapshot(self) -> SolSpendAuthorizationSnapshot:
        actual = self.actual_spend_usd
        average = actual / len(self._call_costs) if self._call_costs else None
        additional_low, additional_high = self._projection_range()
        total_low = actual + additional_low if additional_low is not None else None
        total_high = actual + additional_high if additional_high is not None else None
        recommended = None
        if total_high is not None:
            recommended = math.ceil(total_high / 5.0) * 5.0
            recommended = max(recommended, self._authorized_spend_usd + 5.0)

        progress = self._progress
        return SolSpendAuthorizationSnapshot(
            authorized_spend_usd=self._authorized_spend_usd,
            actual_spend_usd=actual,
            completed_sol_calls=len(self._call_costs),
            average_completed_call_cost_usd=average,
            estimated_percent_complete=(
                progress.estimated_percent_complete if progress is not None else None
            ),
            estimated_remaining_batches=(
                progress.estimated_remaining_batches if progress is not None else None
            ),
            estimated_remaining_sol_calls=(
                progress.estimated_remaining_sol_calls if progress is not None else None
            ),
            estimate_confidence=(progress.estimate_confidence if progress is not None else None),
            estimate_rationale=(progress.estimate_rationale if progress is not None else None),
            estimated_additional_spend_low_usd=additional_low,
            estimated_additional_spend_high_usd=additional_high,
            estimated_total_spend_low_usd=total_low,
            estimated_total_spend_high_usd=total_high,
            recommended_authorized_ceiling_usd=recommended,
        )

    def ensure_authorized_before_next_call(self) -> SolSpendAuthorizationSnapshot:
        snapshot = self.snapshot()
        projected_high = snapshot.estimated_total_spend_high_usd

        # The first Sol call is necessarily permitted under the initial human
        # authorization because no scientific progress estimate exists yet.
        if projected_high is None:
            if snapshot.actual_spend_usd < snapshot.authorized_spend_usd:
                return snapshot
        elif projected_high <= snapshot.authorized_spend_usd:
            return snapshot

        if self._authorization_callback is not None:
            new_ceiling = self._authorization_callback(snapshot)
            if new_ceiling is not None:
                self.authorize_through(float(new_ceiling))
                refreshed = self.snapshot()
                # A human may intentionally authorize less than the full projected
                # research need. In that case permit one more call only when its
                # observed average cost still fits; the guard will ask again later.
                estimated_next = refreshed.average_completed_call_cost_usd or 0.0
                if refreshed.actual_spend_usd + estimated_next <= refreshed.authorized_spend_usd:
                    return refreshed

        raise SolSpendAuthorizationRequired(self.snapshot())
