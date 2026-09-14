from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from MTS_V4.contracts import SubjectMetadata
from MTS_V4.sec_share_structure_source import SecEdgarShareStructureSource


DEFAULT_MATRIX = (
    ("AAPL", "mega_cap_operating_company"),
    ("XOM", "large_cap_operating_company"),
    ("SOFI", "younger_growth_company"),
    ("GME", "high_turnover_retail_interest"),
    ("AMC", "dilution_and_reverse_split_history"),
    ("MULN", "microcap_reverse_split_dilution_history"),
    ("BRK-B", "multi_class_equity"),
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit SEC point-in-time share-structure coverage across heterogeneous equities.")
    parser.add_argument("--tickers", nargs="*", default=None)
    parser.add_argument("--output", default=None)
    return parser


def _summary(ticker: str, category: str) -> dict[str, object]:
    subject = SubjectMetadata(subject_id=f"equity:{ticker}", ticker=ticker)
    payload = next(iter(SecEdgarShareStructureSource().acquire(subject)))
    rows = list(payload.payload)
    shares = [row for row in rows if row.get("fact_kind") == "SHARES_OUTSTANDING"]
    public_float = [row for row in rows if row.get("fact_kind") == "PUBLIC_FLOAT_REPORTED"]
    direct_float_shares = [
        row for row in public_float
        if str(row.get("unit", "")).lower() in {"share", "shares"}
    ]
    monetary_float = [
        row for row in public_float
        if str(row.get("unit", "")).upper() == "USD"
    ]
    accessions = {str(row.get("accession")) for row in rows if row.get("accession")}
    forms = sorted({str(row.get("form")) for row in rows if row.get("form")})
    ciks = sorted({str(row.get("cik")) for row in rows if row.get("cik")})
    return {
        "ticker": ticker,
        "test_category": category,
        "row_count": len(rows),
        "coverage_start_known_at": payload.coverage_start,
        "coverage_end_known_at": payload.coverage_end,
        "shares_outstanding_fact_count": len(shares),
        "public_float_fact_count": len(public_float),
        "public_float_usd_fact_count": len(monetary_float),
        "direct_public_float_share_fact_count": len(direct_float_shares),
        "distinct_accessions": len(accessions),
        "forms": forms,
        "cik": payload.provenance.get("cik"),
        "issuer_ciks": ciks,
        "issuer_lineage": payload.provenance.get("issuer_lineage"),
        "company_name": payload.provenance.get("company_name"),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    matrix = DEFAULT_MATRIX if not args.tickers else tuple((ticker.upper(), "user_selected") for ticker in args.tickers)
    results: list[dict[str, object]] = []
    for ticker, category in matrix:
        try:
            results.append(_summary(ticker, category))
        except Exception as exc:
            results.append({
                "ticker": ticker,
                "test_category": category,
                "error": f"{type(exc).__name__}: {exc}",
            })

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output = Path(args.output or f"/home/ubuntu/MTS_V4_SEC_SHARE_STRUCTURE_MATRIX_{stamp}.txt")
    document = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "coverage_and_provenance_audit_only",
        "results": results,
    }
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OUTPUT={output}")
    for row in results:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
