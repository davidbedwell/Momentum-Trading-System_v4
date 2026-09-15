from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.control_readiness import build_control_readiness_report, load_hidden_answer_key
from MTS_V4.derived_market_store import ParquetDerivedMarketStore


def _load_object(path: str | Path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return raw


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Perform a zero-SOL mechanical readiness audit of all blinded scientific controls."
    )
    parser.add_argument("--control-config-json", required=True)
    parser.add_argument("--hidden-answer-key-json", required=True)
    parser.add_argument("--derived-market-root", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)

    output = Path(args.output_json)
    if output.exists():
        raise RuntimeError(f"refusing to overwrite readiness report: {output}")
    config = _load_object(args.control_config_json)
    answer_key = load_hidden_answer_key(args.hidden_answer_key_json)
    store = ParquetDerivedMarketStore(Path(args.derived_market_root).expanduser().resolve())
    report = build_control_readiness_report(config, answer_key, store)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)

    print(f"CONTROL_READINESS_STATUS={report['status']}")
    print(f"FAILURES={len(report['failures'])}")
    print("SOL_CALLS=0")
    print(f"REPORT={output}")
    return 0 if report["status"] == "READY_FOR_BLINDED_CALIBRATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
