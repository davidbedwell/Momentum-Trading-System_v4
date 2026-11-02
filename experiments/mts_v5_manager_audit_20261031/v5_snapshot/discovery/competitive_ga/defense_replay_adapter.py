"""Connect causal close-time criteria to the next-open replay order queue."""
from .streaming_defense import StreamingDefense

def make_defense_callback(criteria_at_close):
    """Return callback(date) for functional_niche_manager.run_slice.

    criteria_at_close(date) must return the five Boolean detector criteria
    computed from observations available by that date's close.
    """
    machine=StreamingDefense()
    def at_close(date):
        return machine.observe(date, criteria_at_close(date))['defensive_next_open']
    return at_close
