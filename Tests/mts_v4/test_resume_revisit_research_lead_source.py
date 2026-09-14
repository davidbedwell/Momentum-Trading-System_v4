from pathlib import Path


def test_resume_interprets_completed_batch_before_any_fresh_intake():
    text = Path("scripts/resume_fresh_subject.py").read_text(encoding="utf-8")

    interpret = text.index("decision = rd.interpret_batch_results(")
    intake = text.index("evidence = IntakeEngine(runtime.cache).ingest(", interpret)
    assert interpret < intake
