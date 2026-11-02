"""Research-only shared-capital competition among niche and unrestricted chromosomes.
Not a certified allocator; same DEV79 data must not be treated as validation.
"""
from ga7.request_replay import replay_requests

def compare_banks(banks, sessions, passes):
    """Replay each full bank against the same cash pool; rank portfolio metrics.

    Each bank maps niche identifiers to chromosomes, with NON_NICHE fallback.
    This is bank-level comparison, not an independent-stock return sum.
    """
    results=[]
    for name,bank in banks.items():
        if 'NON_NICHE' not in bank:
            raise ValueError('Bank needs unrestricted fallback')
        metrics,_=replay_requests(bank,sessions,passes)
        results.append((name,metrics))
    return sorted(results,key=lambda row:(-row[1]['cagr'],row[1]['mdd'],row[0]))
