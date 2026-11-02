"""Connect executed-fill holdings to four-family native daily producers.
Feature inputs and archived genomes are provided by caller for each date.
No future bars or inferred fills enter the native producer boundary.
"""
from .native_four_family_orchestrator import produce


def daily_producer(inputs_by_date):
    """Return callable accepted by chronological_manager_replay.run.

    Each date's inputs must contain trained_through, source_hash,
    snapshot_hash and any family-specific specs/panels.
    """
    def native(date, session, bars, holdings, owners, defense, fills):
        if date not in inputs_by_date:raise ValueError('missing dated native inputs')
        settings=dict(inputs_by_date[date])
        states={}
        for ticker,owner in owners.items():
            if ticker not in holdings or ticker not in fills.positions:
                raise ValueError('native owner/fill reconciliation failed')
            position=fills.positions[ticker]
            if position.owner!=owner:raise ValueError('native position owner mismatch')
            states[ticker]={'entry':position.entry,'initial_stop':position.stop,
                            'weight':holdings[ticker],'owner':owner,
                            'shares':position.shares,'peak':position.peak,
                            'entry_session':position.entry_session}
        settings.setdefault('session',session)
        return produce(date,held=states,defensive=defense,**settings)
    return native



def shadow_producer(inputs_by_date):
    """Evaluate chromosomes against their independent executed shadow states."""
    def native(date, session, bars, defense, book):
        settings = dict(inputs_by_date[date])
        settings.setdefault('session', session)
        return produce(date, held_by_owner=book.native_states(bars),
                       defensive=defense, **settings)
    return native
