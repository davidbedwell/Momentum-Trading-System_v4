"""Run the frozen calibration preflight before any paid compute.

This command only checks local files and test prerequisites; it never starts
an evolutionary run or reads protected partitions.
"""
from __future__ import annotations
import json
import sys
from Core.layered_ga.stage2_recovered_source_preflight_v3 import verify_recovered_sources


def main():
    result = verify_recovered_sources()
    print(json.dumps(result, indent=2))
    if result["decision"] != "PASS":
        print("BLOCKED: recover or verify exact certified dependencies before launch", file=sys.stderr)
        return 2
    print("Recovered source checks passed. This is NOT calibration certification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
