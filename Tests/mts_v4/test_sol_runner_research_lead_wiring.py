from pathlib import Path


def test_production_sol_runner_wires_research_lead_intake_and_sec_precompute():
    text = Path("scripts/run_sol_batched_one_subject.py").read_text(encoding="utf-8")

    assert "standard_research_lead_market_source" in text
    assert "build_sec_share_structure" in text
    assert "source=standard_research_lead_market_source()" in text
    assert "precomputed_results.update(build_sec_share_structure(" in text

    sec_precompute = text.index("precomputed_results.update(build_sec_share_structure(")
    sol_run = text.index("outcome = runtime.orchestrator.run(")
    assert sec_precompute < sol_run


def test_standard_research_lead_source_includes_sec_and_intraday_inputs(monkeypatch):
    monkeypatch.setenv("UNUSUAL_WHALES_API_KEY", "test-placeholder")
    monkeypatch.setenv("FINRA_API_CLIENT_ID", "test-placeholder")
    monkeypatch.setenv("FINRA_API_CLIENT_SECRET", "test-placeholder")

    from MTS_V4.research_lead_sources import standard_research_lead_market_source
    from MTS_V4.participation_sources import YFinanceIntradaySource
    from MTS_V4.sec_share_structure_source import SecEdgarShareStructureSource

    source = standard_research_lead_market_source()
    sources = tuple(source._sources)

    assert any(isinstance(item, YFinanceIntradaySource) for item in sources)
    assert any(isinstance(item, SecEdgarShareStructureSource) for item in sources)
