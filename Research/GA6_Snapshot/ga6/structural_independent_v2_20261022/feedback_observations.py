"""Development-only feedback from completed GA6 discovery trials.

This does not use in-sample fitness as a scientific reward. It measures
candidate identity novelty per activity and recorded per-trial wall-time proxy.
"""
from collections import defaultdict
from ga6.structural_independent_v2_20261022.discovery_allocation import ACTIVITIES, Observation


def novelty_observations(ledger, through_generation, lag=2):
    """Use only completed earlier generations; never same-generation feedback."""
    rows = ledger.db.execute(
        'SELECT activity,chromosome_id,cpu_seconds,generation FROM trials '
        'WHERE role=? AND generation<=? ORDER BY generation,trial_id',
        ('discovery', through_generation-lag)).fetchall()
    counts=defaultdict(int)
    seconds=defaultdict(float)
    novel=defaultdict(int)
    seen=set()
    for activity,chromosome,elapsed,generation in rows:
        if activity not in ACTIVITIES:
            continue
        counts[activity]+=1
        seconds[activity]+=elapsed
        if chromosome not in seen:
            novel[activity]+=1
            seen.add(chromosome)
    return {a:Observation(trials=counts[a],novel=novel[a],compute_seconds=seconds[a])
            for a in ACTIVITIES if counts[a]>=5 and seconds[a]>0}
