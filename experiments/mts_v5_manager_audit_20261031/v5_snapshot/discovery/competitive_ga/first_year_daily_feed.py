"""Fail-closed causal daily inputs for the native four-family orchestrator.

The loader is called with an already authorized cutoff. It must push that cutoff
into its storage query; a full-history load followed by filtering is not allowed.
"""
from .first_year_manifest import audit_contracts, eligibility, validate_panel
from .first_year_parity import feature_eligibility


class DailyFeed:
    def __init__(self, *, calendar, tickers, contracts, scenario_hash, loader):
        self.calendar = calendar
        self.tickers = tuple(tickers)
        self.contracts = contracts
        self.scenario_hash = scenario_hash
        self.loader = loader
        self.last = None

    def at_close(self, date, *, decision_at, gates, requirements):
        self.calendar.permit(date)  # Before even invoking caller I/O.
        if self.last is not None and self.calendar.sessions.index(date) != self.calendar.sessions.index(self.last)+1:
            raise ValueError('daily feed cannot skip, repeat or reverse sessions')
        blockers = audit_contracts(self.contracts, decision_date=date, scenario_hash=self.scenario_hash)
        if blockers:
            raise ValueError('blocked native input contracts: '+ '; '.join(blockers))
        if set(requirements) != set(self.contracts) or set(gates) != set(requirements):
            raise ValueError('explicit requirements and gates required for each family')
        # Validate dated controls before loading feature values.
        allowed = {f: eligibility(gates[f], decision_date=date, decision_at=decision_at,
                    tickers=self.tickers, family=f) for f in requirements}
        panels = self.loader(as_of=date)
        if set(panels) != set(requirements):
            raise ValueError('incomplete four-family panels')
        result = {}
        for family, panel in panels.items():
            validate_panel(panel, calendar=self.calendar, as_of=date, tickers=self.tickers)
            today = panel.loc[panel.date == date].copy()
            entry = feature_eligibility(today, requirements[family], allowed[family])
            today['eligible'] = today.ticker.map(entry)
            if family == 'GA7':
                today['controlling_niche'] = today.ticker.map(gates[family].set_index('ticker')['niche'])
            result[family] = today
        self.last = date
        return result
