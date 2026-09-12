from __future__ import annotations

import argparse

from MTS_V4.prospective_outcome_vault import (
    load_vault_key,
    release_collective_outcomes,
)
from MTS_V4.prospective_validation import JsonProspectiveValidationStore
from MTS_V4.research_package_store import JsonResearchPackageStore


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Collectively release a prospective validation only after all first "
            "20 locked trials have sealed outcomes."
        )
    )
    parser.add_argument("--validation-state", required=True)
    parser.add_argument("--research-package-dir", required=True)
    parser.add_argument("--rp-id", required=True)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--vault-key-file", required=True)
    args = parser.parse_args()

    result = release_collective_outcomes(
        validation_store=JsonProspectiveValidationStore(args.validation_state),
        research_package_store=JsonResearchPackageStore(args.research_package_dir),
        rp_id=args.rp_id,
        vault_path=args.vault,
        vault_key=load_vault_key(args.vault_key_file),
    )
    print(f"RELEASE_STATUS={result.status}")
    print(f"COMPLETED_TRIALS={result.completed_trials}")
    print(f"SUCCESS_COUNT={result.success_count}")
    print(f"FAILURE_COUNT={result.failure_count}")
    print(f"SUCCESS_RATE={result.success_rate}")
    print(f"HYPOTHESIS_STATUS={result.hypothesis_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
