from __future__ import annotations

from .live_sources import CompositeEvidenceSource, standard_live_market_source
from .participation_sources import (
    YFinanceCatalystEventsSource,
    YFinanceIntradaySource,
    YFinanceMarketStructureSource,
)
from .sec_share_structure_source import SecEdgarShareStructureSource


def standard_research_lead_market_source() -> CompositeEvidenceSource:
    """Standard market evidence plus neutral research-lead inputs.

    This composes acquisition only. It does not rank evidence, classify catalysts,
    define signals, select thresholds, or make scientific conclusions.
    """
    return CompositeEvidenceSource(
        standard_live_market_source(),
        YFinanceMarketStructureSource(),
        YFinanceCatalystEventsSource(),
        YFinanceIntradaySource(),
        SecEdgarShareStructureSource(),
    )
