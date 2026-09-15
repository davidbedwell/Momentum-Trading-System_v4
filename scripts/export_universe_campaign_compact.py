from __future__ import annotations

import argparse
import json

from MTS_V4.campaign_compact_export import create_compact_campaign_export


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export compact universe campaign science and analytics without the derived market store.")
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    manifest = create_compact_campaign_export(state_dir=args.state_dir, output_path=args.output)
    print(json.dumps({
        "COMPACT_EXPORT": args.output,
        "FILES": len(manifest["contents"]),
        "DERIVED_MARKET_STORE_INCLUDED": False,
        "RAW_MARKET_DATA_INCLUDED": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
