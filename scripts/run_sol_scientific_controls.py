from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys

from MTS_V4.acceptance_controls import BLINDED_CONTROLS
from MTS_V4.control_readiness import require_ready_report
from MTS_V4.scientific_control_campaign import (
    ControlAssessment,
    ControlGrade,
    ControlRunRecord,
    assemble_control_report,
)


def _load_object(path: str | Path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return raw


def _assessment_records(path: str | None):
    if not path:
        return ()
    raw = _load_object(path)
    output = []
    for control_id, item in raw.items():
        if not isinstance(item, dict):
            raise RuntimeError(f"assessment for {control_id} must be an object")
        output.append(
            ControlAssessment(
                control_id=control_id,
                grade=ControlGrade(str(item.get("grade", "UNASSESSED"))),
                rationale=str(item.get("rationale", "")),
                assessor=str(item.get("assessor", "")),
            )
        )
    return tuple(output)


def _append_repeatable(command: list[str], flag: str, values) -> None:
    for value in values or ():
        command.extend((flag, str(value)))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run all five blinded MTS scientific calibration controls through Sol and assemble one governed report.")
    parser.add_argument("--control-config-json", required=True, help="Per-control evidence/query configuration. Expected answers are deliberately not part of this file.")
    parser.add_argument("--campaign-root", required=True)
    parser.add_argument("--control-readiness-report", required=True, help="Passing zero-SOL preflight report bound to this exact configuration.")
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument("--derived-market-root", default=None)
    parser.add_argument(
        "--scientific-partition-manifest",
        required=True,
        help="Frozen partition forwarded to every historical-outcome control run.",
    )
    parser.add_argument("--per-control-sol-spend-limit-usd", type=float, required=True)
    parser.add_argument("--assessment-json", default=None, help="Optional independent post-run PASS/PARTIAL/FAIL assessments; never sent to Sol.")
    parser.add_argument("--continue-after-failure", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.per_control_sol_spend_limit_usd <= 0:
        raise RuntimeError("--per-control-sol-spend-limit-usd must be positive")

    config = _load_object(args.control_config_json)
    require_ready_report(args.control_readiness_report, config)
    expected = {control.control_id for control in BLINDED_CONTROLS}
    missing = expected - set(config)
    if missing:
        raise RuntimeError(f"control config missing required controls: {sorted(missing)}")
    campaign_root = Path(args.campaign_root)
    if campaign_root.exists() and any(campaign_root.iterdir()):
        raise RuntimeError("campaign-root must be new or empty")
    campaign_root.mkdir(parents=True, exist_ok=True)
    runs = []

    for control in BLINDED_CONTROLS:
        item = config[control.control_id]
        if not isinstance(item, dict):
            raise RuntimeError(f"config for {control.control_id} must be an object")
        state_dir = campaign_root / control.control_id
        command = [
            sys.executable,
            str(Path(__file__).with_name("run_sol_batched_universe.py")),
            "--universe-id", str(item["universe_id"]),
            "--feature-set-id", str(item["feature_set_id"]),
            "--feature-set-version", str(item["feature_set_version"]),
            "--root", args.root,
            "--state-dir", str(state_dir),
            "--sol-spend-limit-usd", str(args.per_control_sol_spend_limit_usd),
            "--no-interactive-spend-extension",
            "--research-objective", control.research_prompt,
            "--calibration-control-id", control.control_id,
            "--control-readiness-report", args.control_readiness_report,
        ]
        if args.derived_market_root:
            command.extend(("--derived-market-root", args.derived_market_root))
        command.extend(("--scientific-partition-manifest", args.scientific_partition_manifest))
        for optional in ("start_date", "end_date"):
            if item.get(optional):
                command.extend(("--" + optional.replace("_", "-"), str(item[optional])))
        _append_repeatable(command, "--security-id", item.get("security_ids"))
        _append_repeatable(command, "--feature-column", item.get("feature_columns"))
        if item.get("outcome_feature_set_id"):
            command.extend(("--outcome-feature-set-id", str(item["outcome_feature_set_id"])))
            command.extend(("--outcome-feature-set-version", str(item["outcome_feature_set_version"])))
            _append_repeatable(command, "--outcome-feature-column", item.get("outcome_feature_columns"))
            command.append("--allow-historical-outcomes")
        if args.dry_run:
            command.append("--dry-run")

        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        log_path = campaign_root / f"{control.control_id}.runner.txt"
        log_path.write_text(
            "COMMAND=" + " ".join(command) + "\n\nSTDOUT\n" + completed.stdout + "\nSTDERR\n" + completed.stderr,
            encoding="utf-8",
        )
        summary_path = state_dir / "run_summary.json"
        summary = _load_object(summary_path) if summary_path.exists() else {}
        spend = summary.get("sol_spend") if isinstance(summary.get("sol_spend"), dict) else {}
        runs.append(
            ControlRunRecord(
                control_id=control.control_id,
                state_dir=str(state_dir),
                exit_code=completed.returncode,
                analyses_executed=(int(summary["analyses_executed"]) if "analyses_executed" in summary else None),
                findings_promoted=(int(summary["findings_promoted"]) if "findings_promoted" in summary else None),
                closed=(bool(summary["closed"]) if "closed" in summary else None),
                sol_spend_usd=(float(spend["actual_spend_usd"]) if "actual_spend_usd" in spend else None),
                replay_capture_path=(str(summary["qwen_replay_capture"]) if summary.get("qwen_replay_capture") else None),
            )
        )
        if completed.returncode != 0 and not args.continue_after_failure:
            break

    report = assemble_control_report(runs, _assessment_records(args.assessment_json))
    report_path = campaign_root / "scientific_control_campaign_report.json"
    report_path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    dry_run_validated = bool(
        args.dry_run
        and len(runs) == len(BLINDED_CONTROLS)
        and all(run.exit_code == 0 for run in runs)
    )
    print(f"CAMPAIGN_ROOT={campaign_root}")
    print(f"CONTROLS_ATTEMPTED={len(runs)}")
    print(f"ALL_FIVE_CONTROLS_PRESENT={report.all_five_controls_present}")
    print(f"ALL_RUNS_COMPLETED={report.all_runs_completed}")
    print(f"ALL_CONTROLS_ASSESSED={report.all_controls_assessed}")
    print(f"OVERALL_STATUS={report.overall_status}")
    if args.dry_run:
        print(f"DRY_RUN_VALIDATED={dry_run_validated}")
    print(f"REPORT={report_path}")
    return 0 if report.all_runs_completed or dry_run_validated else 2


if __name__ == "__main__":
    raise SystemExit(main())
