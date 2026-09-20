#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from MTS_V4.equivalence_appeal import create_blinded_packet, freeze_hybrid_manifest, run_bounded_sol_appeal
from MTS_V4.equivalence_execution import prepare_identical_start, run_direct_sol_arm, run_gemini_rd_arm
from MTS_V4.openai_compatible_provider import OpenAICompatibleResearchDirector
from MTS_V4.virgin_equivalence import EquivalenceProtocolError, canonical_sha256, qualify_experiment, write_frozen_json


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def usage_cost(usage) -> float:
    if isinstance(usage, dict):
        for key in ("actual_spend_usd", "spent_usd", "cost_usd", "actual_cost_usd"):
            value = usage.get(key)
            if isinstance(value, (int, float)):
                return float(value)
    return 0.0


def direct_cost(manifest) -> float:
    return sum(usage_cost(x) for x in manifest.get("usage", []))


def main() -> int:
    p = argparse.ArgumentParser(description="Run frozen UBER/IBM/RL Direct-Sol vs Gemini+Sol experiment sequentially.")
    p.add_argument("--scientific-root", default="/home/ubuntu")
    p.add_argument("--experiment-root", default="/home/ubuntu/mts-v4-gemini-sol-equivalence-20260920")
    p.add_argument("--gemini-model", default=os.getenv("MTS_GEMINI_EQUIVALENCE_MODEL", "google/gemini-2.5-pro"))
    p.add_argument("--direct-sol-cap", type=float, default=15.0)
    p.add_argument("--gemini-cap", type=float, default=5.0)
    p.add_argument("--gemini-max-calls", type=int, default=30)
    p.add_argument("--appeal-sol-cap", type=float, default=5.0)
    args = p.parse_args()

    scientific_root = Path(args.scientific_root).resolve()
    exp = Path(args.experiment_root).resolve()
    selection_path = exp / "01_VIRGIN_SELECTION.json"
    if not selection_path.is_file():
        raise EquivalenceProtocolError("frozen virgin selection is missing")
    selection = load_json(selection_path)
    tickers = selection.get("selected_subject_ids")
    if tickers != ["UBER", "IBM", "RL"]:
        raise EquivalenceProtocolError(f"unexpected frozen ticker order: {tickers}")

    # A previous attempt may have failed before any arm/model call. Preserve the
    # frozen subject selection but allow that clean pre-spend attempt to resume.
    identity_path = exp / "BLIND_IDENTITY_SECRET.json"
    if identity_path.exists():
        paid_artifacts = list(exp.glob("*/DIRECT_SOL/ARM_MANIFEST.json")) + list(exp.glob("*/GEMINI_RD/GEMINI_USAGE.json"))
        if paid_artifacts:
            raise EquivalenceProtocolError("experiment already has paid-arm artifacts; refusing accidental rerun")
        identity_path.unlink()
    for ticker in tickers:
        start_path = exp / ticker / "START.json"
        if start_path.exists() and not (exp / ticker / "DIRECT_SOL").exists() and not (exp / ticker / "GEMINI_RD").exists():
            start_path.unlink()

    salt = os.urandom(32).hex()
    write_frozen_json(identity_path, {"salt": salt, "selection_sha256": canonical_sha256(selection)})

    comparisons = []
    direct_total = 0.0
    hybrid_total = 0.0

    for ticker in tickers:
        print(f"START {ticker}", flush=True)
        start = prepare_identical_start(root=scientific_root, ticker=ticker, experiment_root=exp)
        direct = run_direct_sol_arm(root=scientific_root, ticker=ticker, experiment_root=exp, start=start, sol_spend_usd=args.direct_sol_cap)
        gemini_root, gemini_usage, _ = run_gemini_rd_arm(root=scientific_root, ticker=ticker, experiment_root=exp, start=start, model=args.gemini_model, max_calls=args.gemini_max_calls, max_spend_usd=args.gemini_cap)

        hybrid_root = exp / ticker / "GEMINI_SOL_HYBRID"
        hybrid_root.mkdir(parents=True, exist_ok=False)
        appeal_provider = OpenAICompatibleResearchDirector(base_url=os.environ["MTS_SOL_BASE_URL"], model=os.environ["MTS_SOL_MODEL"], api_key=os.environ["MTS_SOL_API_KEY"], timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")))
        run_bounded_sol_appeal(start=start, gemini_root=gemini_root, hybrid_root=hybrid_root, sol_provider=appeal_provider, max_sol_calls=1, max_sol_spend_usd=args.appeal_sol_cap)
        appeal_usage = {"authorized_cap_usd": args.appeal_sol_cap, "qualification_cost_usd": args.appeal_sol_cap, "calls": 1}
        hybrid = freeze_hybrid_manifest(ticker=ticker, start=start, gemini_root=gemini_root, hybrid_root=hybrid_root, gemini_usage=gemini_usage, sol_usage=appeal_usage)
        create_blinded_packet(direct_manifest=direct, hybrid_manifest=hybrid, output=exp / ticker / "BLINDED_PAIR.json", salt=salt)

        adjudicator = OpenAICompatibleResearchDirector(base_url=os.environ["MTS_SOL_BASE_URL"], model=os.environ["MTS_SOL_MODEL"], api_key=os.environ["MTS_SOL_API_KEY"], timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")))
        blind = load_json(exp / ticker / "BLINDED_PAIR.json")
        prompt = {"task": "Blindly compare ARM_X and ARM_Y. Evaluate missed research lines, false promotions, findings, direction, horizon, robustness, and trading conclusion. A material finding present in one arm but absent in the other must be explicitly identified. Do not infer model identity. Return strict JSON with materially_equivalent, material_finding_present_in_X_missing_Y, material_finding_present_in_Y_missing_X, disqualifying_false_promotion_X, disqualifying_false_promotion_Y, dimensions, rationale.", "packet": blind}
        raw = adjudicator._chat_completion([{"role":"system","content":"You are a blinded scientific adjudicator. Return JSON only."},{"role":"user","content":json.dumps(prompt,sort_keys=True,separators=(",",":"))}])
        verdict = json.loads(raw)
        write_frozen_json(exp / ticker / "BLIND_VERDICT.json", verdict)
        direct_is_x = blind["ARM_X"].get("freeze_sha256") == direct.get("freeze_sha256")
        missed = bool(verdict.get("material_finding_present_in_X_missing_Y")) if direct_is_x else bool(verdict.get("material_finding_present_in_Y_missing_X"))
        false_hybrid = bool(verdict.get("disqualifying_false_promotion_Y")) if direct_is_x else bool(verdict.get("disqualifying_false_promotion_X"))
        comparison = {"ticker": ticker, "materially_equivalent": bool(verdict.get("materially_equivalent")), "material_direct_sol_finding_missed": missed, "disqualifying_false_hybrid_promotion": false_hybrid, "blind_verdict_sha256": canonical_sha256(verdict)}
        write_frozen_json(exp / ticker / "COMPARISON.json", comparison)
        comparisons.append(comparison)
        dc = direct_cost(direct)
        hc = usage_cost(gemini_usage) + args.appeal_sol_cap
        direct_total += dc
        hybrid_total += hc
        status = "PASS" if comparison["materially_equivalent"] and not missed and not false_hybrid else "FAIL"
        print(f"{ticker} {status} direct=${dc:.2f} hybrid<=${hc:.2f}", flush=True)
        if missed or false_hybrid or not comparison["materially_equivalent"]:
            write_frozen_json(exp / "EARLY_STOP.json", {"ticker": ticker, "comparison": comparison, "direct_cost_usd": direct_total, "hybrid_cost_upper_bound_usd": hybrid_total})
            print("STOP scientific-equivalence failure", flush=True)
            return 2

    qualification = qualify_experiment(comparisons, direct_cost_usd=direct_total, hybrid_cost_usd=hybrid_total)
    write_frozen_json(exp / "FINAL_QUALIFICATION.json", qualification)
    print(f"FINAL qualified={qualification['qualified']} saving={qualification['cost_saving_fraction']:.1%} direct=${direct_total:.2f} hybrid<=${hybrid_total:.2f}", flush=True)
    return 0 if qualification["qualified"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
