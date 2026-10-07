"""Governance contracts for the staged MTS contextual-evolution redesign.

This module intentionally contains no trading logic and no guessed GA0 gene list.
It makes stage boundaries machine-readable so downstream code cannot silently
turn the redesign back into a monolithic optimizer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import FrozenSet


class Stage(IntEnum):
    ARCHAEOLOGY = 0
    CONTEXT_MAP = 1
    OPPORTUNITY = 2
    CONTEXT_ABLATION = 3
    ENTRY_MAE = 4
    THESIS_FAILURE = 5
    LIFECYCLE = 6
    CAPITAL_COMPETITION = 7
    POSITION_SIZING = 8
    PORTFOLIO_CATASTROPHE = 9
    REPORT_CARD = 10


class Direction(str):
    LONG = "LONG"
    SHORT = "SHORT"


class ContextState(str):
    STRONG_DOWN = "STRONG_DOWN"
    DOWN = "DOWN"
    FLAT = "FLAT"
    UP = "UP"
    STRONG_UP = "STRONG_UP"


@dataclass(frozen=True)
class StageContract:
    stage: Stage
    question: str
    allowed_outputs: FrozenSet[str]
    forbidden_objectives: FrozenSet[str]
    requires_frozen: FrozenSet[Stage]


CONTRACTS = {
    Stage.ARCHAEOLOGY: StageContract(
        Stage.ARCHAEOLOGY,
        "What exactly did GA0 contain and how did it evolve?",
        frozenset({"evidence_ledger", "gene_registry", "ga0_control_spec", "unresolved_ledger"}),
        frozenset({"invented_ga0_gene", "unproven_ga0_provenance"}),
        frozenset(),
    ),
    Stage.CONTEXT_MAP: StageContract(
        Stage.CONTEXT_MAP,
        "What are the causal Galaxy and Solar-System contexts now?",
        frozenset({"state", "strength", "trajectory", "volatility", "relative_context"}),
        frozenset({"trade_pnl", "cagr", "mdd", "future_return_selected_state"}),
        frozenset(),
    ),
    Stage.OPPORTUNITY: StageContract(
        Stage.OPPORTUNITY,
        "Which small chromosomes identify credible prospective net directional EV?",
        frozenset({"long_candidate", "short_candidate", "ev", "uncertainty", "frequency", "forward_path"}),
        frozenset({"cagr", "mdd", "position_size", "portfolio_fitness", "fixed_holding_period"}),
        frozenset({Stage.ARCHAEOLOGY, Stage.CONTEXT_MAP}),
    ),
    Stage.CONTEXT_ABLATION: StageContract(
        Stage.CONTEXT_ABLATION,
        "Does Galaxy/Solar-System context add transported information beyond the Planet?",
        frozenset({"planet_only", "plus_galaxy", "plus_sector", "full_context", "interaction_effect"}),
        frozenset({"cagr", "mdd", "portfolio_fitness"}),
        frozenset({Stage.OPPORTUNITY}),
    ),
    Stage.ENTRY_MAE: StageContract(
        Stage.ENTRY_MAE,
        "For a frozen opportunity, enter now or wait for causal market confirmation?",
        frozenset({"enter_now", "wait_for_evidence", "mae", "mfe", "delay_cost"}),
        frozenset({"fixed_wait_days", "cagr", "mdd"}),
        frozenset({Stage.OPPORTUNITY, Stage.CONTEXT_ABLATION}),
    ),
    Stage.THESIS_FAILURE: StageContract(
        Stage.THESIS_FAILURE,
        "Which causal observations distinguish normal MAE from a falsified thesis?",
        frozenset({"continue_thesis", "thesis_failed", "simple_stop_control"}),
        frozenset({"automatic_opposite_entry", "cagr", "mdd"}),
        frozenset({Stage.ENTRY_MAE}),
    ),
    Stage.LIFECYCLE: StageContract(
        Stage.LIFECYCLE,
        "What does remaining prospective EV support: ADD, HOLD, REDUCE or EXIT?",
        frozenset({"add", "hold", "reduce", "exit", "remaining_ev"}),
        frozenset({"fixed_exit_days", "fixed_profit_target", "cagr", "mdd"}),
        frozenset({Stage.THESIS_FAILURE}),
    ),
    Stage.CAPITAL_COMPETITION: StageContract(
        Stage.CAPITAL_COMPETITION,
        "Which incumbent, challenger or SAFE alternative best deserves capital now?",
        frozenset({"incumbent", "challenger", "safe", "replacement"}),
        frozenset({"automatic_long_short_flip", "cagr", "mdd"}),
        frozenset({Stage.LIFECYCLE}),
    ),
    Stage.POSITION_SIZING: StageContract(
        Stage.POSITION_SIZING,
        "How much exposure does the opportunity deserve given EV, uncertainty and correlated risk?",
        frozenset({"target_exposure", "context_modifier", "correlation_modifier", "tail_modifier"}),
        frozenset({"hard_context_trade_gate", "cagr_target", "mdd_target"}),
        frozenset({Stage.CAPITAL_COMPETITION}),
    ),
    Stage.PORTFOLIO_CATASTROPHE: StageContract(
        Stage.PORTFOLIO_CATASTROPHE,
        "How are simultaneous positions combined while preserving survival?",
        frozenset({"portfolio", "concentration", "liquidity", "catastrophe_override", "safe"}),
        frozenset({"retune_upstream_on_cagr", "retune_upstream_on_mdd"}),
        frozenset({Stage.POSITION_SIZING}),
    ),
    Stage.REPORT_CARD: StageContract(
        Stage.REPORT_CARD,
        "What did the frozen integrated decision process actually produce?",
        frozenset({"cagr", "mdd", "wealth", "cvar", "turnover", "recovery", "stability"}),
        frozenset({"optimize_report_card_by_mutating_frozen_upstream"}),
        frozenset({Stage.PORTFOLIO_CATASTROPHE}),
    ),
}


def assert_stage_can_run(stage: Stage, frozen_stages: set[Stage]) -> None:
    missing = CONTRACTS[stage].requires_frozen - frozenset(frozen_stages)
    if missing:
        names = ", ".join(s.name for s in sorted(missing))
        raise RuntimeError(f"{stage.name} blocked; prerequisite stages are not frozen: {names}")


def assert_objective_allowed(stage: Stage, objective: str) -> None:
    if objective.lower() in {x.lower() for x in CONTRACTS[stage].forbidden_objectives}:
        raise RuntimeError(f"{objective!r} is forbidden in stage {stage.value} {stage.name}")
