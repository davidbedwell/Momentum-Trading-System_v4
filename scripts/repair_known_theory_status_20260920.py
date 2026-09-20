from pathlib import Path

p = Path("MTS_V4/sol_batch_provider.py")
s = p.read_text()

repairs = [
    (
        '"(TESTED_SUPPORTED, TESTED_UNSUPPORTED, TESTED_MIXED, or OBJECTIVELY_NOT_TESTABLE), "',
        '"(TESTED_SUPPORTED, TESTED_UNSUPPORTED, or OBJECTIVELY_NOT_TESTABLE), "',
    ),
    (
        '            "TESTED_MIXED",\n',
        '',
    ),
    (
        '\n"Human governance requires coverage of every theory_id in context.known_predictive_theory_context before subject closure.',
        '\n            "Human governance requires coverage of every theory_id in context.known_predictive_theory_context before subject closure.',
    ),
    (
        '            ""Maintain research_state.campaign_learning_audit_state cumulatively as an audit annotation, not as a scientific constraint.',
        '            "Maintain research_state.campaign_learning_audit_state cumulatively as an audit annotation, not as a scientific constraint.',
    ),
]

for old, new in repairs:
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"REPAIR_ABORT pattern count={n}: {old[:100]!r}")
    s = s.replace(old, new, 1)

if '"TESTED_MIXED"' in s or 'TESTED_MIXED, or OBJECTIVELY_NOT_TESTABLE' in s:
    raise SystemExit("REPAIR_ABORT TESTED_MIXED remains in sol_batch_provider.py")

p.write_text(s)
print("REPAIR_PASS=True")
