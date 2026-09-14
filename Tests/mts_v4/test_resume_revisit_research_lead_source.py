from pathlib import Path


def test_resume_revisit_preserves_production_research_lead_intake_surface():
    text = Path("scripts/resume_fresh_subject.py").read_text(encoding="utf-8")

    assert "from MTS_V4.research_lead_sources import standard_research_lead_market_source" in text
    assert "source=standard_research_lead_market_source()" in text
    assert "source=standard_live_market_source()" not in text


def test_resume_interprets_completed_batch_before_any_fresh_intake():
    text = Path("scripts/resume_fresh_subject.py").read_text(encoding="utf-8")

    interpret = text.index("decision = rd.interpret_batch_results(")
    intake = text.index("evidence = IntakeEngine(runtime.cache).ingest(", interpret)
    assert interpret < intake
