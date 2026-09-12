from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Mapping, Sequence


SEQUENCE = (
    "AAPL",
    "AMD",
    "AMZN",
    "BA",
    "GOOGL",
    "JPM",
    "META",
    "MSFT",
    "NVDA",
    "TSLA",
    "XOM",
)
DEFAULT_PER_SUBJECT_SOL_SPEND_USD = 15.0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the eleven previously researched tickers sequentially through the explicit "
            "deep-history revisit path. Each ticker receives its own governed Sol spend ceiling."
        )
    )
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument("--campaign-dir", default=None)
    parser.add_argument(
        "--per-subject-sol-spend-limit-usd",
        type=float,
        default=DEFAULT_PER_SUBJECT_SOL_SPEND_USD,
    )
    parser.add_argument(
        "--start-at",
        choices=SEQUENCE,
        default=SEQUENCE[0],
        help="start a new ordered run at this ticker without rerunning earlier tickers",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _subject_command(
    *,
    python: str,
    runner: Path,
    ticker: str,
    root: Path,
    state_dir: Path,
    spend_limit_usd: float,
    dry_run: bool,
) -> list[str]:
    command = [
        python,
        str(runner),
        "--ticker",
        ticker,
        "--root",
        str(root),
        "--state-dir",
        str(state_dir),
        "--revisit",
        "--sol-spend-limit-usd",
        str(spend_limit_usd),
    ]
    if dry_run:
        command.append("--dry-run")
    return command


def _write_manifest(path: Path, payload: Mapping[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.per_subject_sol_spend_limit_usd <= 0:
        raise RuntimeError("--per-subject-sol-spend-limit-usd must be positive")

    root = Path(args.root).expanduser().resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    campaign_dir = Path(
        args.campaign_dir or root / f"mts-v4-20y-sequential-revisit-{stamp}"
    ).expanduser().resolve()
    if campaign_dir.exists():
        raise RuntimeError(f"campaign directory already exists: {campaign_dir}")
    campaign_dir.mkdir(parents=True)

    start_index = SEQUENCE.index(args.start_at)
    run_sequence = SEQUENCE[start_index:]
    runner = Path(__file__).with_name("run_sol_batched_one_subject.py").resolve()
    manifest_path = campaign_dir / "sequential_revisit_manifest.json"
    results: list[Mapping[str, object]] = []
    manifest: dict[str, object] = {
        "campaign_dir": str(campaign_dir),
        "sequence": list(run_sequence),
        "start_at": args.start_at,
        "dry_run": args.dry_run,
        "per_subject_sol_spend_limit_usd": args.per_subject_sol_spend_limit_usd,
        "maximum_authorized_campaign_spend_usd": (
            args.per_subject_sol_spend_limit_usd * len(run_sequence)
        ),
        "status": "RUNNING",
        "results": results,
    }
    _write_manifest(manifest_path, manifest)

    print("SEQUENCE=" + ",".join(run_sequence), flush=True)
    print(f"PER_SUBJECT_SOL_SPEND_LIMIT_USD={args.per_subject_sol_spend_limit_usd:.2f}", flush=True)
    print(
        "MAXIMUM_AUTHORIZED_CAMPAIGN_SPEND_USD="
        f"{args.per_subject_sol_spend_limit_usd * len(run_sequence):.2f}",
        flush=True,
    )
    print(f"CAMPAIGN_DIR={campaign_dir}", flush=True)
    print(f"MANIFEST={manifest_path}", flush=True)

    for ordinal, ticker in enumerate(run_sequence, start=start_index + 1):
        state_dir = campaign_dir / f"{ordinal:02d}-{ticker.lower()}"
        print(f"SUBJECT_START={ticker}", flush=True)
        command = _subject_command(
            python=sys.executable,
            runner=runner,
            ticker=ticker,
            root=root,
            state_dir=state_dir,
            spend_limit_usd=args.per_subject_sol_spend_limit_usd,
            dry_run=args.dry_run,
        )
        completed = subprocess.run(command, check=False)
        result = {
            "ticker": ticker,
            "state_dir": str(state_dir),
            "return_code": completed.returncode,
            "status": "COMPLETED" if completed.returncode == 0 else "STOPPED",
        }
        results.append(result)
        manifest["results"] = results
        print(f"SUBJECT_RETURN_CODE_{ticker}={completed.returncode}", flush=True)
        if completed.returncode != 0:
            manifest["status"] = "STOPPED"
            manifest["stopped_at"] = ticker
            manifest["stop_return_code"] = completed.returncode
            _write_manifest(manifest_path, manifest)
            print(f"SEQUENCE_STOPPED_AT={ticker}", flush=True)
            return completed.returncode
        _write_manifest(manifest_path, manifest)
        print(f"SUBJECT_COMPLETE={ticker}", flush=True)

    manifest["status"] = "DRY_RUN_COMPLETE" if args.dry_run else "COMPLETE"
    _write_manifest(manifest_path, manifest)
    print(f"SEQUENCE_COMPLETE={not args.dry_run}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
