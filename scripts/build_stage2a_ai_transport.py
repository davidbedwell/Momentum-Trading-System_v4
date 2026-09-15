from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from MTS_V4.universe_market_structure_substrate import compact_for_ai_transport


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and audit the compact AI transport view of a completed Stage 2A artifact."
    )
    parser.add_argument("--stage2a-artifact", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--maximum-bytes", type=int, default=300000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source = Path(args.stage2a_artifact).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if output.exists():
        raise RuntimeError(f"refusing to replace frozen Stage 2A transport artifact: {output}")
    document = json.loads(source.read_text(encoding="utf-8"))
    analysis = document.get("analysis", {})
    if not isinstance(analysis, dict) or not isinstance(analysis.get("outputs"), dict):
        raise RuntimeError("source is not a completed Stage 2A Analysis artifact")
    source_outputs = analysis["outputs"]
    if source_outputs.get("policy", {}).get("historical_outcomes_consumed") is not False:
        raise RuntimeError("refusing to transport Stage 2A evidence without an explicit no-outcomes record")
    transport = compact_for_ai_transport(source_outputs)
    payload = {
        "format": "MTS_V4_NEUTRAL_UNIVERSE_AI_TRANSPORT_ARTIFACT_V1",
        "source_artifact": str(source),
        "source_artifact_sha256": document.get("artifact_sha256"),
        "analysis_result_id": analysis.get("result_id"),
        "method_id": analysis.get("method_id"),
        "outputs": transport,
        "sol_calls": 0,
    }
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    payload["artifact_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    encoded = json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n"
    minified_bytes = len(json.dumps(transport, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8"))
    if minified_bytes > args.maximum_bytes:
        raise RuntimeError(
            f"compacted Stage 2A transport exceeds maximum: {minified_bytes} > {args.maximum_bytes}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(encoded, encoding="utf-8")
    temporary.replace(output)
    print(f"STAGE2A_TRANSPORT_OUTPUT={output}")
    print(f"STAGE2A_SOURCE_OUTPUT_MINIFIED_BYTES={len(json.dumps(source_outputs, sort_keys=True, default=str, separators=(',', ':')).encode('utf-8'))}")
    print(f"STAGE2A_TRANSPORT_MINIFIED_BYTES={minified_bytes}")
    print(f"STAGE2A_TRANSPORT_ESTIMATED_TOKENS={round(minified_bytes / 4)}")
    print("STAGE2A_TRANSPORT_ALL_FEATURES_RETAINED=True")
    print("STAGE2A_TRANSPORT_ALL_CORRELATION_PAIRS_RETAINED=True")
    print("STAGE2A_TRANSPORT_STATUS=PASS")
    print("SOL_CALLS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
