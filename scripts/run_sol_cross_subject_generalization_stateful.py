from __future__ import annotations

import argparse
import os

from run_sol_cross_subject_generalization import main as run_generalization


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Launch the existing Sol cross-subject generalization campaign with durable explicit generalization-state persistence enabled.", add_help=False)
    parser.add_argument("--generalization-state-path", required=True)
    known, remaining = parser.parse_known_args(argv)
    os.environ["MTS_GENERALIZATION_STATE_PATH"] = known.generalization_state_path
    return run_generalization(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
