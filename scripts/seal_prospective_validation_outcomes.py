from __future__ import annotations

import argparse
from datetime import datetime, timezone

from MTS_V4.prospective_outcome_vault import (
    load_vault_key,
    seal_available_outcomes,
    write_new_vault_key,
)
from MTS_V4.prospective_validation import JsonProspectiveValidationStore
from MTS_V4.prospective_validation_runtime import load_authoritative_sessions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Custodian-only: encrypt matured prospective outcomes without exposing them."
    )
    parser.add_argument("--validation-state", required=True)
    parser.add_argument("--authoritative-snapshot", required=True)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--vault-key-file", required=True)
    parser.add_argument("--as-of-utc", default=None)
    parser.add_argument(
        "--initialize-key",
        action="store_true",
        help="Create the key file with mode 0600 if it does not already exist.",
    )
    args = parser.parse_args()

    if args.initialize_key:
        write_new_vault_key(args.vault_key_file)
    key = load_vault_key(args.vault_key_file)
    as_of = args.as_of_utc or datetime.now(timezone.utc).isoformat()
    result = seal_available_outcomes(
        validation_store=JsonProspectiveValidationStore(args.validation_state),
        sessions=load_authoritative_sessions(args.authoritative_snapshot),
        as_of_utc=as_of,
        vault_path=args.vault,
        vault_key=key,
    )
    print(f"AS_OF_UTC={as_of}")
    print(f"LOCKED_TRIALS={result.locked_trials}")
    print(f"SEALED_TRIALS={result.sealed_trials}")
    print(f"NEWLY_SEALED_TRIALS={result.newly_sealed_trials}")
    print(f"COLLECTIVE_RELEASE_READY={result.release_ready}")
    print("INDIVIDUAL_OUTCOMES_EXPOSED=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
