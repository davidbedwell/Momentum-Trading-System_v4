"""Read-only audit of frozen G2 prerequisites; never launches compute."""
from pathlib import Path
import hashlib
import json

MANIFEST = 'Research/Protocols/MTS_G2_WORKFLOW_APPROVED_MANIFEST_20261006.json'
NULL = 'Research/Conformance/MTS_H7_NULL_CALIBRATION_20261006.json'
PLANTED = 'Research/Conformance/MTS_H7_PLANTED_CALIBRATION_20261006.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verified_report(path):
    try:
        sidecar = path.with_suffix(path.suffix + '.sha256')
        expected = sidecar.read_text().split()[0]
        if len(expected) != 64 or digest(path) != expected:
            return None
        return json.loads(path.read_text())
    except (OSError, ValueError, TypeError, IndexError):
        return None

def manifest_hash_failures(root):
    try:
        m = json.loads((root / MANIFEST).read_text())
        bound = dict(m['runtime_code_bindings'])
        gate = m['production']['controller_semantic_gate']
        bound[gate['controller']] = gate['controller_sha256']
        for k in ('runner', 'fixture', 'fold_worker', 'compute_plan', 'compute_fixture'):
            item = m['null']['runner_gate']
            bound[item[k]] = item[k + '_sha256']
        return ['HASH_DRIFT:' + rel for rel, expected in bound.items()
                if not (root / rel).is_file() or digest(root / rel) != expected]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ['MANIFEST_INVALID:' + type(exc).__name__]

def planted_failures(root):
    r = verified_report(root / PLANTED)
    if r is None:
        return ['PLANTED_MISSING_OR_BAD_HASH']
    m = r.get('mechanics', {})
    if not (r.get('passed') is True and r.get('decision') in ('early_pass', 'pass')
            and m.get('islands') == 9 and m.get('population_per_island') == 64
            and m.get('maximum_generations_per_seed') == 500
            and m.get('seeds') == [0, 1, 2, 3]
            and sum(x is True for x in r.get('recovered', [])) >= 3):
        return ['PLANTED_SEMANTICS_INVALID']
    return []

def null_failures(root):
    r = verified_report(root / NULL)
    if r is None:
        return ['NULL_MISSING_OR_BAD_HASH']
    train = r.get('train_results', [])
    blind = r.get('blind_results', [])
    if not (r.get('passed') is True and r.get('status') == 'PASS'
            and r.get('mechanics', {}).get('population_per_island') == 250
            and len(train) == 4 and len(blind) == 4
            and sorted(x.get('fold') for x in train) == [0, 1, 2, 3]
            and sorted(x.get('fold') for x in blind) == [0, 1, 2, 3]):
        return ['NULL_SEMANTICS_INVALID']
    failures = []
    for x in train:
        try:
            path = (root / x['freeze_path']).resolve()
            if not path.is_relative_to(root.resolve()) or digest(path) != x['freeze_sha256']:
                failures.append('NULL_FREEZE_HASH_DRIFT:' + str(x['fold']))
        except (OSError, KeyError, ValueError):
            failures.append('NULL_FREEZE_MISSING:' + str(x.get('fold')))
    return failures

def risk_failures(root):
    policy = root / 'Research/Protocols/MTS_G2_CATASTROPHIC_RISK_POLICY_APPROVED.json'
    cases = root / 'Research/Conformance/MTS_G2_45_CASE_OBSERVATIONAL_EVIDENCE.json'
    failures = []
    if verified_report(policy) is None:
        failures.append('RISK_POLICY_NOT_FROZEN_OR_VERIFIED')
    if verified_report(cases) is None:
        failures.append('45_CASE_EVIDENCE_MISSING_OR_UNVERIFIED')
    # A self-declared JSON approval cannot substitute for user authorization.
    failures.append('RISK_POLICY_USER_AUTHORIZATION_NOT_VERIFIED')
    return failures

def audit(root):
    checks = {}
    errors = []
    for name, fn in (('manifest', manifest_hash_failures),
                     ('planted', planted_failures),
                     ('null', null_failures), ('risk', risk_failures)):
        problems = fn(Path(root))
        checks[name] = not problems
        errors.extend(problems)
    return {'passed': all(checks.values()), 'checks': checks, 'errors': errors}
