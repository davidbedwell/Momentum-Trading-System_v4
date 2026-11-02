"""Hash-locked native fill arithmetic extraction; RESEARCH ONLY, not replay parity.

Compile unchanged statement slices from the authorized read-only replay. Sizing,
policy, ledger outcome reporting and loop control are deliberately outside these
kernels. No reference executor is called. Original replay code is never patched.
"""
import ast
import hashlib
from pathlib import Path

ROOT = Path('/opt/mts/ga7-deploy/ga7_unbounded/ga7')
HASHES = {
    'request_replay.py': 'efc9fa9d2ea39d2e3f5d247b402cdc1ebadf40b9954830568c910b1a3e5bc375',
    'portfolio_priority.py': '7e8d5717e6e9f6a674c98f328a7db24fb1c9d96a6d6290987e505ef33e5a60b0',
    'proposals.py': '9ec6affa80d8523c1a022214d4a84f5db1ea313ce229def41c6cc1372adc879c',
    'shadow_ledger.py': '29babc4179d6206d94edc1861887ca2631970eb95ea88e88edbeaa78954add54',
    'trade_accounting.py': '26038bc3db8345e10c4c263b0b7a3030677cde2752540fb6b0bfedc7549de757',
}


def sources():
    result = {}
    for name, expected in HASHES.items():
        data = (ROOT / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('unsupported native source: ' + name)
        result[name] = data.decode()
    return result


def load():
    source = sources()
    # Only pure dataclasses/math definitions are executed; native import paths
    # cannot silently resolve a different TradeAccount or Position implementation.
    account_tree = ast.parse(source['trade_accounting.py'])
    scope = {}
    exec(compile(account_tree, str(ROOT/'trade_accounting.py'), 'exec'), scope)
    tree = ast.parse(source['request_replay.py'])
    position = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Position')
    exec(compile(ast.Module(body=[position], type_ignores=[]), str(ROOT/'request_replay.py'), 'exec'), scope)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'replay_requests')
    branches = {ast.unparse(n.test): n for n in ast.walk(fn) if isinstance(n, ast.If)}
    exit_body = branches["proposal.action == 'EXIT' and ticker in positions"].body[:4]
    reduce_body = branches["proposal.action == 'REDUCE' and ticker in positions"].body
    # The sole removed statement is native half-share sizing (qty = max(...)).
    reduce_body = [n for n in reduce_body[:-1] if not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'qty' for t in n.targets))]
    add_body = branches['qty'].body
    enter_body = branches['qty > 0'].body[:6]
    kernels = {}
    for name, body in [('EXIT', exit_body), ('REDUCE', reduce_body), ('ADD', add_body), ('ENTER', enter_body)]:
        kernels[name] = compile(ast.Module(body=body, type_ignores=[]), str(ROOT/'request_replay.py'), 'exec')
    return scope, kernels
