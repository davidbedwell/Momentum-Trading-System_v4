"""Shared-capital allocation without a fixed position-count ceiling."""
from ga6.shared_selector_engine_contract_20261025 import CandidateDecision

def allocate(candidates, held_weights, equity, available_cash, defensive=False):
    if equity <= 0 or available_cash < 0:
        raise ValueError('Invalid capital')
    if defensive:
        return []
    budget = min(available_cash, max(0, equity * (1 - sum(held_weights.values()))))
    ranked = sorted((c.validate() for c in candidates if c.action == 'ENTER'),
                    key=lambda c: (-c.score, c.ticker, c.chromosome_id))
    selected = []
    seen = set(held_weights)
    for candidate in ranked:
        if candidate.score <= 0 or candidate.ticker in seen:
            continue
        amount = min(budget, equity * min(.10, max(.03, candidate.weight)))
        if amount < equity * .03:
            continue
        selected.append((candidate.ticker, candidate.chromosome_id, amount / equity))
        budget -= amount
        seen.add(candidate.ticker)
    return selected
