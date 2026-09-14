from pathlib import Path


def test_resume_interprets_completed_batch_before_any_fresh_intake():
    text = Path("scripts/resume_fresh_subject.py").read_text(encoding="utf-8")

    interpret = text.index("decision = rd.interpret_batch_results(")
    intake = text.index("evidence = IntakeEngine(runtime.cache).ingest(", interpret)
    assert interpret < intake


def test_resume_reacquires_the_same_research_lead_source_as_fresh_campaign():
    resume = Path("scripts/resume_fresh_subject.py").read_text(encoding="utf-8")
    fresh = Path("scripts/run_sol_batched_one_subject.py").read_text(encoding="utf-8")

    assert "standard_research_lead_market_source()" in resume
    assert "standard_research_lead_market_source()" in fresh
    assert "standard_live_market_source()" not in resume
