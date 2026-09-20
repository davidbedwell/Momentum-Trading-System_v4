#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil

from MTS_V4.equivalence_appeal import create_blinded_packet, freeze_hybrid_manifest, recover_bounded_sol_appeal, run_bounded_sol_appeal
from MTS_V4.equivalence_execution import freeze_existing_direct_sol_arm, prepare_identical_start, run_direct_sol_arm, run_gemini_rd_arm
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_provider import SolResearchPackageAwareResearchDirector
from MTS_V4.virgin_equivalence import EquivalenceProtocolError, canonical_sha256, qualify_experiment, verify_identical_start, write_frozen_json


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


def recover_openrouter_usage(path: Path) -> dict[str, object]:
    spend = 0.0
    calls = 0
    model = None
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("event") != "OPENROUTER_RD_CALL_COMPLETE":
                continue
            calls += 1
            model = row.get("model") or model
            value = row.get("actual_call_cost_usd")
            if isinstance(value, (int, float)):
                spend += float(value)
    if calls < 1:
        raise EquivalenceProtocolError(f"OpenRouter telemetry has no completed calls: {path}")
    return {"model": model, "completed_calls": calls, "actual_spend_usd": spend, "recovered_from_telemetry": True}


def recover_sol_usage(path: Path) -> dict[str, object]:
    spend = 0.0
    calls = 0
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("event") != "SOL_CALL_COMPLETE":
                continue
            calls += 1
            value = row.get("estimated_call_cost_usd")
            if isinstance(value, (int, float)):
                spend += float(value)
    if calls < 1:
        raise EquivalenceProtocolError(f"Sol telemetry has no completed calls: {path}")
    return {"completed_sol_calls": calls, "actual_spend_usd": spend, "recovered_from_telemetry": True}

def main() -> int:
    p = argparse.ArgumentParser(description="Run frozen UBER/IBM/RL Direct-Sol vs Gemini+Sol experiment sequentially.")
    p.add_argument("--scientific-root", default="/home/ubuntu")
    p.add_argument("--experiment-root", default="/home/ubuntu/mts-v4-gemini-sol-equivalence-20260920")
    p.add_argument("--gemini-model", default=os.getenv("MTS_GEMINI_EQUIVALENCE_MODEL", "google/gemini-3.7-flash"))
    p.add_argument("--direct-sol-cap", type=float, default=15.0)
    p.add_argument("--gemini-cap", type=float, default=5.0)
    p.add_argument("--gemini-max-calls", type=int, default=30)
    p.add_argument("--appeal-sol-cap", type=float, default=5.0)
    p.add_argument("--adjudicator-sol-cap", type=float, default=3.0)
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

    def has_paid_trace(subject_root: Path) -> bool:
        telemetry = [
            subject_root / "DIRECT_SOL" / "sol_transport_telemetry.jsonl",
            subject_root / "GEMINI_RD" / "openrouter_telemetry.jsonl",
            subject_root / "GEMINI_SOL_HYBRID" / "sol_appeal_telemetry.jsonl",
            subject_root / "BLIND_ADJUDICATOR" / "sol_transport_telemetry.jsonl",
        ]
        return any(path.is_file() and path.stat().st_size > 0 for path in telemetry)

    identity_path = exp / "BLIND_IDENTITY_SECRET.json"
    any_paid_trace = any(has_paid_trace(exp / ticker) for ticker in tickers)
    if identity_path.exists():
        identity = load_json(identity_path)
        salt = str(identity["salt"])
    else:
        if any_paid_trace:
            raise EquivalenceProtocolError("paid experiment traces exist but blind identity commitment is missing")
        salt = os.urandom(32).hex()
        write_frozen_json(identity_path, {"salt": salt, "selection_sha256": canonical_sha256(selection)})

    # Clean only unequivocally pre-spend debris. Never delete a directory that
    # contains provider telemetry or a completed paid artifact.
    for ticker in tickers:
        subject_root = exp / ticker
        if not subject_root.exists() or has_paid_trace(subject_root):
            continue
        if any((subject_root / p).exists() for p in ("COMPARISON.json", "BLIND_VERDICT.json")):
            continue
        for child in list(subject_root.iterdir()):
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    final_path = exp / "FINAL_QUALIFICATION.json"
    if final_path.is_file():
        final = load_json(final_path)
        print(f"FINAL qualified={final['qualified']} saving={float(final['cost_saving_fraction']):.1%} direct=${float(final['direct_cost_usd']):.2f} hybrid=${float(final['hybrid_cost_usd']):.2f}", flush=True)
        return 0 if final.get("qualified") else 3

    comparisons = []
    direct_total = 0.0
    hybrid_total = 0.0

    for ticker in tickers:
        comparison_path = exp / ticker / "COMPARISON.json"
        direct_manifest_path = exp / ticker / "DIRECT_SOL" / "ARM_MANIFEST.json"
        hybrid_manifest_path = exp / ticker / "GEMINI_SOL_HYBRID" / "ARM_MANIFEST.json"
        if comparison_path.is_file():
            if not direct_manifest_path.is_file() or not hybrid_manifest_path.is_file():
                raise EquivalenceProtocolError(f"{ticker} comparison exists without both arm manifests")
            comparison = load_json(comparison_path)
            direct = load_json(direct_manifest_path)
            hybrid = load_json(hybrid_manifest_path)
            hybrid_usage = hybrid.get("usage", [])
            if not isinstance(hybrid_usage, list) or len(hybrid_usage) < 2:
                raise EquivalenceProtocolError(f"{ticker} hybrid manifest lacks Gemini+appeal usage")
            dc = direct_cost(direct)
            hc = usage_cost(hybrid_usage[0]) + usage_cost(hybrid_usage[1])
            comparisons.append(comparison)
            direct_total += dc
            hybrid_total += hc
            status = "PASS" if comparison.get("materially_equivalent") and not comparison.get("material_direct_sol_finding_missed") and not comparison.get("disqualifying_false_hybrid_promotion") else "FAIL"
            print(f"{ticker} {status} direct=${dc:.2f} hybrid=${hc:.2f} (recovered)", flush=True)
            if status == "FAIL":
                return 2
            continue
        print(f"START {ticker}", flush=True)
        start_path = exp / ticker / "START.json"
        if start_path.exists():
            start = load_json(start_path)
            verify_identical_start(start, start)
        else:
            start = prepare_identical_start(root=scientific_root, ticker=ticker, experiment_root=exp)
            verify_identical_start(start, start)
        direct_manifest_path = exp / ticker / "DIRECT_SOL" / "ARM_MANIFEST.json"
        if direct_manifest_path.is_file():
            direct = load_json(direct_manifest_path)
        elif (exp / ticker / "DIRECT_SOL").exists():
            direct = freeze_existing_direct_sol_arm(ticker=ticker, experiment_root=exp, start=start)
        else:
            direct = run_direct_sol_arm(root=scientific_root, ticker=ticker, experiment_root=exp, start=start, sol_spend_usd=args.direct_sol_cap)

        gemini_root = exp / ticker / "GEMINI_RD"
        gemini_usage_path = gemini_root / "GEMINI_USAGE.json"
        if gemini_usage_path.is_file():
            gemini_usage = load_json(gemini_usage_path)
            for required in ("decisions.json", "reports.json", "outcome.json"):
                if not (gemini_root / required).is_file():
                    raise EquivalenceProtocolError(f"completed Gemini usage exists but scientific artifact is missing: {required}")
        elif (gemini_root / "openrouter_telemetry.jsonl").is_file() and (gemini_root / "openrouter_telemetry.jsonl").stat().st_size > 0:
            required_paths = [gemini_root / name for name in ("decisions.json", "reports.json", "outcome.json")]
            if not all(path.is_file() for path in required_paths):
                raise EquivalenceProtocolError("partial paid Gemini arm detected; refusing to delete or rerun paid work")
            outcome_doc = load_json(gemini_root / "outcome.json")
            outcome_state = outcome_doc.get("outcome", {})
            if not isinstance(outcome_state, dict) or not (outcome_state.get("closed") or outcome_state.get("waiting_for_future_cohorts")):
                raise EquivalenceProtocolError("paid Gemini arm is not at a governed terminal state; refusing paid rerun")
            gemini_usage = recover_openrouter_usage(gemini_root / "openrouter_telemetry.jsonl")
            write_frozen_json(gemini_usage_path, gemini_usage)
        else:
            # An interrupted pre-spend Gemini launch can leave arm-local setup
            # artifacts behind even though no provider call occurred. Because a
            # completed Direct-Sol arm gives the subject paid telemetry, the
            # subject-level cleanup above must not remove these files. Clean
            # only this Gemini arm when there is unequivocally no Gemini spend
            # and no completed Gemini artifact, then start it fresh.
            if gemini_root.exists():
                telemetry = gemini_root / "openrouter_telemetry.jsonl"
                completed = any(
                    (gemini_root / name).is_file()
                    for name in ("GEMINI_USAGE.json", "decisions.json", "reports.json", "outcome.json")
                )
                if telemetry.is_file() and telemetry.stat().st_size > 0:
                    raise EquivalenceProtocolError("partial paid Gemini arm detected; refusing to delete or rerun paid work")
                if completed:
                    raise EquivalenceProtocolError("Gemini arm has scientific artifacts without recoverable paid telemetry; refusing cleanup")
                shutil.rmtree(gemini_root)
            gemini_root, gemini_usage, _ = run_gemini_rd_arm(root=scientific_root, ticker=ticker, experiment_root=exp, start=start, model=args.gemini_model, max_calls=args.gemini_max_calls, max_spend_usd=args.gemini_cap)

        hybrid_root = exp / ticker / "GEMINI_SOL_HYBRID"
        if hybrid_manifest_path.is_file():
            hybrid = load_json(hybrid_manifest_path)
            hybrid_usage = hybrid.get("usage", [])
            if not isinstance(hybrid_usage, list) or len(hybrid_usage) < 2:
                raise EquivalenceProtocolError("hybrid manifest lacks Gemini+appeal usage")
            appeal_usage = hybrid_usage[1]
        else:
            hybrid_root.mkdir(parents=True, exist_ok=True)
            appeal_usage_path = hybrid_root / "SOL_APPEAL_USAGE.json"
            appeal_path = hybrid_root / "SOL_APPEAL.json"
            appeal_telemetry = hybrid_root / "sol_appeal_telemetry.jsonl"
            if appeal_path.is_file() and appeal_usage_path.is_file():
                appeal_usage = load_json(appeal_usage_path)
            elif appeal_path.is_file() and appeal_telemetry.is_file() and appeal_telemetry.stat().st_size > 0:
                appeal_usage = recover_sol_usage(appeal_telemetry)
                if int(appeal_usage.get("completed_sol_calls", 0)) != 1:
                    raise EquivalenceProtocolError("bounded Sol appeal recovery found other than one completed call")
                write_frozen_json(appeal_usage_path, appeal_usage)
            elif appeal_telemetry.is_file() and appeal_telemetry.stat().st_size > 0 and (hybrid_root / "SOL_APPEAL_RAW.txt").is_file():
                recover_bounded_sol_appeal(hybrid_root)
                appeal_usage = recover_sol_usage(appeal_telemetry)
                if int(appeal_usage.get("completed_sol_calls", 0)) != 1:
                    raise EquivalenceProtocolError("recovered Sol appeal has other than one completed call")
                write_frozen_json(appeal_usage_path, appeal_usage)
            else:
                if appeal_telemetry.is_file() and appeal_telemetry.stat().st_size > 0:
                    raise EquivalenceProtocolError("partial paid Sol appeal detected without recoverable raw response")
                appeal_provider = SolResearchPackageAwareResearchDirector(
                    research_package_store=JsonResearchPackageStore(hybrid_root / "_appeal_transport_packages"),
                    base_url=os.environ["MTS_SOL_BASE_URL"],
                    model=os.environ["MTS_SOL_MODEL"],
                    api_key=os.environ["MTS_SOL_API_KEY"],
                    timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
                )
                appeal_provider.configure_sol_spend_guard(authorized_spend_usd=args.appeal_sol_cap, authorization_callback=None)
                prior_telemetry = os.environ.get("MTS_SOL_TELEMETRY_PATH")
                os.environ["MTS_SOL_TELEMETRY_PATH"] = str(appeal_telemetry)
                try:
                    run_bounded_sol_appeal(start=start, gemini_root=gemini_root, hybrid_root=hybrid_root, sol_provider=appeal_provider, max_sol_calls=1, max_sol_spend_usd=args.appeal_sol_cap)
                finally:
                    if prior_telemetry is None:
                        os.environ.pop("MTS_SOL_TELEMETRY_PATH", None)
                    else:
                        os.environ["MTS_SOL_TELEMETRY_PATH"] = prior_telemetry
                snapshot = appeal_provider.sol_spend_snapshot()
                if snapshot is None or snapshot.completed_sol_calls != 1:
                    raise EquivalenceProtocolError("bounded Sol appeal lacks exactly one accounted Sol call")
                appeal_usage = asdict(snapshot)
                write_frozen_json(appeal_usage_path, appeal_usage)
            hybrid = freeze_hybrid_manifest(ticker=ticker, start=start, gemini_root=gemini_root, hybrid_root=hybrid_root, gemini_usage=gemini_usage, sol_usage=appeal_usage)

        blind_path = exp / ticker / "BLINDED_PAIR.json"
        if blind_path.is_file():
            blind = load_json(blind_path)
        else:
            blind = create_blinded_packet(direct_manifest=direct, hybrid_manifest=hybrid, output=blind_path, salt=salt)

        adjudication_root = exp / ticker / "BLIND_ADJUDICATOR"
        adjudication_root.mkdir(parents=True, exist_ok=True)
        prompt = {"task": "Blindly compare ARM_X and ARM_Y. Evaluate missed research lines, false promotions, findings, direction, horizon, robustness, and trading conclusion. A material finding present in one arm but absent in the other must be explicitly identified. Do not infer model identity. Return strict JSON with materially_equivalent, material_finding_present_in_X_missing_Y, material_finding_present_in_Y_missing_X, disqualifying_false_promotion_X, disqualifying_false_promotion_Y, dimensions, rationale.", "packet": blind}
        verdict_path = exp / ticker / "BLIND_VERDICT.json"
        if verdict_path.is_file():
            verdict = load_json(verdict_path)
        else:
            adjudicator_telemetry = adjudication_root / "sol_transport_telemetry.jsonl"
            raw_path = adjudication_root / "RAW_RESPONSE.txt"
            if adjudicator_telemetry.is_file() and adjudicator_telemetry.stat().st_size > 0 and raw_path.is_file():
                raw = raw_path.read_text(encoding="utf-8")
                try:
                    verdict = json.loads(raw)
                except json.JSONDecodeError:
                    left, right = raw.find("{"), raw.rfind("}")
                    if left < 0 or right <= left:
                        raise EquivalenceProtocolError("paid blinded adjudication has no recoverable JSON object")
                    verdict = json.loads(raw[left:right + 1])
                write_frozen_json(verdict_path, verdict)
            elif adjudicator_telemetry.is_file() and adjudicator_telemetry.stat().st_size > 0:
                raise EquivalenceProtocolError("partial paid blinded adjudication detected without recoverable raw response")
            else:
                adjudicator = SolResearchPackageAwareResearchDirector(
                    research_package_store=JsonResearchPackageStore(adjudication_root / "_transport_packages"),
                    base_url=os.environ["MTS_SOL_BASE_URL"],
                    model=os.environ["MTS_SOL_MODEL"],
                    api_key=os.environ["MTS_SOL_API_KEY"],
                    timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
                )
                adjudicator.configure_sol_spend_guard(authorized_spend_usd=args.adjudicator_sol_cap, authorization_callback=None)
                prior_telemetry = os.environ.get("MTS_SOL_TELEMETRY_PATH")
                os.environ["MTS_SOL_TELEMETRY_PATH"] = str(adjudicator_telemetry)
                try:
                    raw = adjudicator._chat_completion([{"role":"system","content":"You are a blinded scientific adjudicator. Return JSON only."},{"role":"user","content":json.dumps(prompt,sort_keys=True,separators=(",",":"))}])
                    raw_path.write_text(raw + "\n", encoding="utf-8")
                finally:
                    if prior_telemetry is None:
                        os.environ.pop("MTS_SOL_TELEMETRY_PATH", None)
                    else:
                        os.environ["MTS_SOL_TELEMETRY_PATH"] = prior_telemetry
                try:
                    verdict = json.loads(raw)
                except json.JSONDecodeError:
                    left, right = raw.find("{"), raw.rfind("}")
                    if left < 0 or right <= left:
                        raise EquivalenceProtocolError("blinded adjudicator did not return a JSON object")
                    verdict = json.loads(raw[left:right + 1])
                snapshot = adjudicator.sol_spend_snapshot()
                if snapshot is None or snapshot.completed_sol_calls != 1:
                    raise EquivalenceProtocolError("blinded adjudication lacks exactly one accounted Sol call")
                write_frozen_json(adjudication_root / "USAGE.json", asdict(snapshot))
                write_frozen_json(verdict_path, verdict)
        direct_is_x = blind["ARM_X"].get("freeze_sha256") == direct.get("freeze_sha256")
        missed = bool(verdict.get("material_finding_present_in_X_missing_Y")) if direct_is_x else bool(verdict.get("material_finding_present_in_Y_missing_X"))
        false_hybrid = bool(verdict.get("disqualifying_false_promotion_Y")) if direct_is_x else bool(verdict.get("disqualifying_false_promotion_X"))
        comparison = {"ticker": ticker, "materially_equivalent": bool(verdict.get("materially_equivalent")), "material_direct_sol_finding_missed": missed, "disqualifying_false_hybrid_promotion": false_hybrid, "blind_verdict_sha256": canonical_sha256(verdict)}
        write_frozen_json(comparison_path, comparison)
        comparisons.append(comparison)
        dc = direct_cost(direct)
        hc = usage_cost(gemini_usage) + usage_cost(appeal_usage)
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
