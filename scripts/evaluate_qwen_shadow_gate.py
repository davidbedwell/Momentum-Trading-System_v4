from __future__ import annotations

import argparse

from MTS_V4.qwen_shadow_gate import evaluate_qwen_shadow_gate, load_shadow_observations, write_gate_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Assemble the governed Qwen replay/shadow autonomy-review report. This command cannot authorize autonomy.")
    parser.add_argument("--observations-jsonl", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)
    observations = load_shadow_observations(args.observations_jsonl)
    report = evaluate_qwen_shadow_gate(observations)
    write_gate_report(args.output_json, report)
    print(f"CASES={report.cases}")
    print(f"TOTAL_ANALYSIS_OPERATIONS={report.total_analysis_operations}")
    print(f"MINIMUM_20_ANALYSIS_OPERATIONS_REACHED={report.minimum_analysis_operations_reached}")
    print(f"AUTONOMY_STATUS={report.autonomy_status}")
    print("HUMAN_AUTHORIZATION_REQUIRED=True")
    print("QWEN_AUTONOMY_AUTHORIZED=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
