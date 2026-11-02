"""GA6 native held-state decisions with authenticated proposal wrapping."""
from math import isfinite
from types import SimpleNamespace
from .native_signal_contract import NativeProposal


def decision(candidate, row, state, *, session, defensive=False, evaluator=None):
    """Return native action/target without asserting a model training cutoff."""
    if evaluator is None:
        from ga6.native_position_decision_adapter import native_action
        evaluator = native_action
    if state is None and (defensive or not row.get('eligible', False)):
        return None
    native_state = None if state is None else SimpleNamespace(shares=state['shares'],
        entry_price=state['entry'], peak_price=state['peak'], entry_session=state['entry_session'])
    action, amount = evaluator(candidate, row, native_state, session)
    if action in ('NO_DATA', 'NO_ENTRY'):
        if state is not None and action == 'NO_DATA':
            raise ValueError('missing held GA6 features')
        return None
    if state is not None and defensive:
        action, amount = 'EXIT', 0.
    if action not in ('ENTER', 'ADD', 'HOLD', 'REDUCE', 'EXIT'):
        raise ValueError('unsupported native GA6 action')
    if action == 'EXIT':
        target = 0.
    elif state is None:
        if action != 'ENTER':raise ValueError('native action requires held GA6 state')
        target = float(amount)
    elif action == 'ENTER':
        raise ValueError('native entry on held GA6 position')
    elif action == 'HOLD':
        target = state['weight']
    elif action == 'REDUCE':
        if not 0 <= float(amount) <= 1:raise ValueError('invalid native GA6 retained fraction')
        target = state['weight'] * float(amount)
    else:
        if not isfinite(float(amount)) or float(amount) < 0:raise ValueError('invalid native GA6 addition')
        target = min(.30, state['weight'] + float(amount))
        if target <= state['weight']:action, target = 'HOLD', state['weight']
    if not isfinite(target):raise ValueError('invalid native GA6 amount')
    return action, target


def produce(candidate, rows, *, decision_date, session, chromosome_id,
            trained_through, source_hash, snapshot_hash, held=None,
            defensive=False, evaluator=None):
    held = held or {}
    if set(held) - set(rows):raise ValueError('held GA6 ticker missing causal row')
    result = []
    for ticker, row in sorted(rows.items()):
        value = decision(candidate, row, held.get(ticker), session=session,
                         defensive=defensive, evaluator=evaluator)
        if value is None:continue
        action, target = value
        result.append(NativeProposal(decision_date, ticker, 'GA6', chromosome_id,
            action, target, 0., 'entry_equity_fraction', source_hash,
            snapshot_hash, trained_through))
    return result
