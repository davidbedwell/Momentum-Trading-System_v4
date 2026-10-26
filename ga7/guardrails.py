"""Research input guardrails. Require externally certified point-in-time policies."""
import json
from pathlib import Path

class Guardrails:
    def __init__(self, path):
        obj = json.loads(Path(path).read_text())
        if not obj.get("pit_certified") or not obj.get("earnings_certified"):
            raise ValueError("PIT membership and earnings certification required")
        if not obj.get("source_manifest"):
            raise ValueError("Missing policy provenance")
        self.membership = {(d, t): bool(ok) for d, t, ok in obj["membership"]}
        self.blocked = {(d, t) for d, t in obj["earnings_blocked"]}
        self.sectors = {(d, t): sector for d, t, sector in obj["sectors"]}
        self.dates = set(obj["dates"])
        if not self.dates:
            raise ValueError("Empty PIT policy")
    def check(self, day, ticker):
        key = (day, ticker)
        if day not in self.dates or key not in self.membership or key not in self.sectors:
            raise ValueError("Missing PIT eligibility or sector coverage: " + str(key))
        return self.membership[key] and key not in self.blocked
    def sector(self, day, ticker):
        return self.sectors[(day, ticker)]
