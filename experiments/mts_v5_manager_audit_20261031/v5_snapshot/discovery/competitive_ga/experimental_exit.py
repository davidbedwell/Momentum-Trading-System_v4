"""Explicit pluggable GA4 research exits; never an approved archive contract."""
from dataclasses import dataclass
from .native_signal_contract import NativeProposal


@dataclass(frozen=True)
class ExperimentalExit:
    version: str
    callback: object
    source_hash: str

    def __post_init__(self):
        if not self.version.startswith('EXPERIMENTAL_') or not callable(self.callback) or not self.source_hash:
            raise ValueError('versioned experimental callback and source identity required')

    def __call__(self, *, decision_date, held, chromosome_id, trained_through,
                 source_hash, snapshot_hash):
        # This type deliberately provides no exit_archive_link. The authentic
        # DailyFeed gate must remain blocked, even when this plugin is supplied.
        result = self.callback(decision_date=decision_date, held=held)
        if set(result) != set(held) or any(a not in ('HOLD', 'EXIT') for a in result.values()):
            raise ValueError('experimental exit requires exact held coverage')
        return [NativeProposal(decision_date, ticker, 'GA4', chromosome_id,
                action, held[ticker]['weight'] if action == 'HOLD' else 0.,
                0., 'native_horizon_score', self.source_hash, snapshot_hash, trained_through)
                for ticker, action in sorted(result.items())]

    def bind(self, *, chromosome_id, trained_through, snapshot_hash):
        """Return the existing GA4 exit_producer(date, held) hook."""
        hook = lambda date, held: self(decision_date=date, held=held,
            chromosome_id=chromosome_id, trained_through=trained_through,
            source_hash=self.source_hash, snapshot_hash=snapshot_hash)
        hook.experimental_exit_version = self.version
        return hook
