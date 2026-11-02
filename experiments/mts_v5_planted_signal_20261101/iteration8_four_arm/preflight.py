"""Read-only source inventory; writes only this experiment's preflight artifacts.

No engine import, entropy draw, portfolio replay, or claim of preregistration.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

O = Path(__file__).resolve().parent
ROOT = O.parents[2]
P = O.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    paths = set()
    for name in ('discrimination_iteration5', 'discrimination_iteration6',
                 'competing_independent_tests'):
        for p in (P / name).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py', '.md', '.json'):
                paths.add(p)
    paths.update((O/'CHARTER.md', P/'claude_iteration8_review/review.md',
                  P/'claude_vs_chat_iteration7/TASK.md'))
    manifest = {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}
    previous = O/'source_inventory.json'
    if previous.exists():
        old = json.loads(previous.read_text())
        if old != manifest:
            raise SystemExit('Source inventory changed; investigate before replacing evidence')
    previous.write_text(json.dumps(manifest, indent=2)+'\n')
    report = dict(execution_status='BLOCKED_SPECIFICATION', experiment_complete=False,
                  utc=datetime.now(timezone.utc).isoformat(), portfolio_replays=0,
                  seed_draws=0, commitment_created=False, source_files=len(manifest),
                  sources_unchanged=all(sha(ROOT/k)==v for k,v in manifest.items()),
                  issues='SPECIFICATION_ISSUES.md', preregistration='preregister.draft.json',
                  experiment_results=None)
    (O/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    (O/'summary.md').write_text(
        '# Four-arm experiment: specification blocked\n\n'
        'The experiment has not run. Preflight found no approved 8B detector definition '
        'and no unique mapping of Claude’s three-policy package to single arm 8A. '
        'See SPECIFICATION_ISSUES.md for exact source conflicts and budget arithmetic.\n\n'
        'Zero seed draws; zero portfolio replays; no experimental pass/fail claims. '
        'preregister.draft.json is an uncommitted draft. source_inventory.json hashes '
        'the baseline, iteration7 source/results, charter and review. Existing sources '
        'are only read. Re-run `python3 preflight.py` to verify their identity.\n\n'
        'To proceed, supply the approved 8B definition and the intended 8A policy. '
        'Finalize budget/criteria, complete implementation and independent validation, '
        'then freeze code and preregistration before drawing seeds.\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
