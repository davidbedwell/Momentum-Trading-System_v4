from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping

from .contracts import SubjectMetadata
from .intake import IntakePayload
from .live_sources import LiveSourceError


SEC_TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def _user_agent() -> str:
    """Return the descriptive User-Agent required by SEC fair-access policy."""
    value = os.getenv("SEC_EDGAR_USER_AGENT", "").strip()
    if not value:
        raise LiveSourceError(
            "SEC_EDGAR_USER_AGENT is required for SEC EDGAR access; set a descriptive application/contact value"
        )
    return value


def _get_json(url: str) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": _user_agent(),
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise LiveSourceError(
            f"SEC EDGAR request failed for {url}: {type(exc).__name__}: {exc}"
        ) from exc


def _resolve_cik(ticker: str, document: object) -> tuple[str, str | None]:
    if not isinstance(document, Mapping):
        raise LiveSourceError("SEC ticker map response was not an object")
    target = ticker.upper()
    for item in document.values():
        if not isinstance(item, Mapping):
            continue
        if str(item.get("ticker", "")).upper() != target:
            continue
        cik = str(item.get("cik_str", "")).strip()
        if not cik:
            break
        return cik.zfill(10), str(item.get("title")) if item.get("title") else None
    raise LiveSourceError(f"SEC ticker map did not contain ticker {target}")


def _fact_rows(
    companyfacts: Mapping[str, object],
    *,
    taxonomy: str,
    tag: str,
    fact_kind: str,
) -> list[dict[str, object]]:
    facts = companyfacts.get("facts")
    if not isinstance(facts, Mapping):
        return []
    tax = facts.get(taxonomy)
    if not isinstance(tax, Mapping):
        return []
    concept = tax.get(tag)
    if not isinstance(concept, Mapping):
        return []
    units = concept.get("units")
    if not isinstance(units, Mapping):
        return []

    rows: list[dict[str, object]] = []
    for unit, observations in units.items():
        if not isinstance(observations, list):
            continue
        for observation in observations:
            if not isinstance(observation, Mapping):
                continue
            filed = observation.get("filed")
            value = observation.get("val")
            if filed in (None, "") or value is None:
                continue
            rows.append(
                {
                    "fact_kind": fact_kind,
                    "taxonomy": taxonomy,
                    "tag": tag,
                    "unit": str(unit),
                    "value": value,
                    "period_end": observation.get("end"),
                    "filed_date": str(filed),
                    "known_at": str(filed),
                    "form": observation.get("form"),
                    "fiscal_year": observation.get("fy"),
                    "fiscal_period": observation.get("fp"),
                    "frame": observation.get("frame"),
                    "accession": observation.get("accn"),
                    "source": "SEC_COMPANYFACTS_XBRL",
                }
            )
    return rows


def normalize_sec_share_structure(
    *, ticker: str, cik: str, companyfacts: Mapping[str, object]
) -> list[dict[str, object]]:
    """Normalize raw SEC XBRL facts without inventing historical public-float shares.

    EntityCommonStockSharesOutstanding is a share-count fact. EntityPublicFloat is
    the SEC public-float disclosure and is normally monetary; it is deliberately
    retained in its reported unit rather than divided by a price or converted into
    a share count here. Such reconstruction, if scientifically requested, belongs
    in Analysis with explicit price/date lineage.
    """
    rows: list[dict[str, object]] = []
    rows.extend(
        _fact_rows(
            companyfacts,
            taxonomy="dei",
            tag="EntityCommonStockSharesOutstanding",
            fact_kind="SHARES_OUTSTANDING",
        )
    )
    rows.extend(
        _fact_rows(
            companyfacts,
            taxonomy="dei",
            tag="EntityPublicFloat",
            fact_kind="PUBLIC_FLOAT_REPORTED",
        )
    )
    for row in rows:
        row["ticker"] = ticker.upper()
        row["cik"] = cik
    rows.sort(
        key=lambda row: (
            str(row.get("known_at") or ""),
            str(row.get("period_end") or ""),
            str(row.get("fact_kind") or ""),
            str(row.get("accession") or ""),
        )
    )
    return rows


@dataclass(frozen=True, slots=True)
class SecEdgarShareStructureSource:
    """Acquire point-in-time SEC share-structure disclosures for one equity.

    The evidence separates the date represented by a fact (`period_end`) from the
    date it became available to MTS (`known_at`/`filed_date`). It does not infer a
    continuous historical float, back-project current float, choose among duplicate
    filings, or convert monetary public float into shares.
    """

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        ticker = subject.ticker.upper()
        ticker_map = _get_json(SEC_TICKER_MAP_URL)
        cik, company_name = _resolve_cik(ticker, ticker_map)
        document = _get_json(SEC_COMPANYFACTS_URL.format(cik=cik))
        if not isinstance(document, Mapping):
            raise LiveSourceError("SEC companyfacts response was not an object")
        rows = normalize_sec_share_structure(
            ticker=ticker,
            cik=cik,
            companyfacts=document,
        )
        known_dates = [str(row["known_at"]) for row in rows if row.get("known_at")]
        yield IntakePayload(
            payload=rows,
            evidence_type="POINT_IN_TIME_SHARE_STRUCTURE",
            artifact_type="NORMALIZED_DATASET",
            source_identity="SEC_EDGAR_COMPANYFACTS_SHARE_STRUCTURE",
            coverage_start=min(known_dates) if known_dates else None,
            coverage_end=max(known_dates) if known_dates else None,
            row_count=len(rows),
            schema=(
                "ticker", "cik", "fact_kind", "taxonomy", "tag", "unit", "value",
                "period_end", "filed_date", "known_at", "form", "fiscal_year",
                "fiscal_period", "frame", "accession", "source",
            ),
            provenance={
                "provider": "U.S. Securities and Exchange Commission EDGAR",
                "ticker": ticker,
                "cik": cik,
                "company_name": company_name or document.get("entityName"),
                "ticker_map_url": SEC_TICKER_MAP_URL,
                "companyfacts_endpoint": SEC_COMPANYFACTS_URL.format(cik=cik),
                "concepts": [
                    "dei:EntityCommonStockSharesOutstanding",
                    "dei:EntityPublicFloat",
                ],
                "point_in_time_anchor": "filed_date",
                "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
            },
            neutral_semantics=(
                "SEC-filed XBRL share-structure facts with filing-date provenance. "
                "Shares outstanding and reported public float are disclosures, not trading signals. "
                "EntityPublicFloat is preserved in its SEC-reported unit and is not assumed to be "
                "freely tradable share count. Duplicate/amended filings are retained for governed "
                "point-in-time reconciliation by Analysis."
            ),
        )
