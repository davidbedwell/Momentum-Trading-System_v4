"""Causal synthetic input contract. Validation never reads a sealed proof panel.

Assertions in a caller's manifest are not certification: source hashes and gate
rows must come from governed inputs. Missing contracts remain blocking.
"""
from dataclasses import dataclass
from datetime import date
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

FAMILIES = ('GA4', 'HORIZONS', 'GA6', 'GA7')
GATES = ('member', 'earnings_clear', 'risk_clear', 'corporate_actions_verified')


def day(value):
    # Deliberately reject timestamp truncation, NaT and ambiguous date formats.
    normalized = date.fromisoformat(str(value)).isoformat()
    if str(value) != normalized:
        raise ValueError('strict ISO YYYY-MM-DD date required')
    return normalized


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class Calendar:
    sessions: tuple
    train_end: str
    validation_end: str
    proof_start: str

    def __post_init__(self):
        days = tuple(day(d) for d in self.sessions)
        if not days or days != tuple(sorted(set(days))):
            raise ValueError('sessions must be unique and chronological')
        bounds = tuple(day(d) for d in (self.train_end, self.validation_end, self.proof_start))
        if not all(d in days for d in bounds) or not bounds[0] < bounds[1] < bounds[2]:
            raise ValueError('invalid train/validation/proof separation')
        object.__setattr__(self, 'sessions', days)

    def phase(self, value):
        d = day(value)
        if d not in self.sessions:
            raise ValueError('date outside declared exchange sessions')
        if d >= self.proof_start:
            return 'proof'
        return 'train' if d <= self.train_end else ('validation' if d <= self.validation_end else 'embargo')

    def permit(self, value):
        if self.phase(value) in ('proof', 'embargo'):
            raise ValueError('sealed proof inputs cannot be opened by engineering feed')


def validate_panel(frame, *, calendar, as_of, tickers):
    """Require the full declared prefix, not merely 500 names somewhere in it."""
    calendar.permit(as_of)
    universe = tuple(tickers)
    if len(universe) != 500 or len(set(universe)) != 500 or any(not isinstance(t, str) or not t for t in universe):
        raise ValueError('require exactly 500 unique ticker identities')
    if not {'date', 'ticker'} <= set(frame):
        raise ValueError('missing panel keys')
    keys = frame[['date', 'ticker']].copy()
    keys['date'] = [day(d) for d in keys.date]
    expected = pd.MultiIndex.from_product(
        [[d for d in calendar.sessions if d <= as_of], universe], names=['date', 'ticker'])
    actual = pd.MultiIndex.from_frame(keys)
    if actual.has_duplicates or len(actual) != len(expected) or len(expected.difference(actual)):
        raise ValueError('incomplete, duplicate, future or foreign panel rows')
    return keys


def eligibility(rows, *, decision_date, tickers, family, decision_at):
    """Dated entry gate; held positions must still receive native management.

    earnings_clear is the result of the SELECTED versioned native embargo, not
    an assumed absence of events. The coverage row itself requires provenance.
    """
    if family not in FAMILIES:
        raise ValueError('unknown family')
    required = {'date', 'ticker', 'available_at', 'source_hash', 'security_id',
                'earnings_contract', *GATES}
    if not required <= set(rows):
        raise ValueError('missing PIT/earnings gate contract')
    if rows.ticker.duplicated().any() or rows.security_id.duplicated().any() or set(rows.ticker) != set(tickers):
        raise ValueError('gate coverage must match full universe')
    result = {}
    cutoff = pd.Timestamp(decision_at)
    if pd.isna(cutoff) or cutoff.tzinfo is None or str(cutoff.date()) != day(decision_date):
        raise ValueError('explicit dated close decision timestamp required')
    for row in rows.to_dict('records'):
        if day(row['date']) != decision_date:
            raise ValueError('gate date mismatch')
        available = pd.Timestamp(row['available_at'])
        if pd.isna(available) or available.tzinfo is None or available > cutoff:
            raise ValueError('gate availability is missing or in the future')
        if not all(isinstance(row[k], (bool, np.bool_)) for k in GATES):
            raise ValueError('gate flags must be explicit booleans')
        if not all(isinstance(row[k], str) and row[k] for k in ('source_hash', 'security_id', 'earnings_contract')):
            raise ValueError('missing gate provenance')
        allowed = all(row[k] for k in GATES)
        if family == 'GA7':
            # Non-niche is explicit; a missing niche model is not NON_NICHE.
            if not {'niche', 'niche_trained_through', 'niche_source_hash'} <= row.keys():
                raise ValueError('missing GA7 niche PIT contract')
            if not all(isinstance(row[k],str) and row[k] for k in ('niche','niche_source_hash')) or day(row['niche_trained_through']) >= decision_date:
                raise ValueError('invalid GA7 niche chronology')
        result[row['ticker']] = bool(allowed)
    return result


def audit_contracts(contracts, *, decision_date, scenario_hash):
    """Report all missing native contracts without inventing semantics."""
    blockers = []
    for family in FAMILIES:
        c = contracts.get(family, {})
        for field in ('source_hash', 'snapshot_hash', 'trained_through', 'feature_contract', 'eligibility_contract'):
            if not c.get(field):
                blockers.append(f'{family}: missing {field}')
        if c.get('trained_through') and day(c['trained_through']) >= day(decision_date):
            blockers.append(f'{family}: training cutoff is not before decision')
    if not contracts.get('GA4', {}).get('exit_archive_link'):
        blockers.append('GA4: approved native exit/archive linkage missing')
    h = contracts.get('HORIZONS', {})
    if not scenario_hash or h.get('stress_scenario_hash') != scenario_hash or not h.get('stress_mapping_provenance') or not h.get('stress_availability_contract'):
        blockers.append('HORIZONS: compatible scenario stress/publication contract missing')
    return blockers


def manifest(frame, *, calendar, as_of, tickers, sources, contracts, gate_rows, decision_times):
    keys = validate_panel(frame, calendar=calendar, as_of=as_of, tickers=tickers)
    if not sources or any(not {'path', 'sha256', 'role'} <= s.keys() for s in sources):
        raise ValueError('source path/hash/role inventory required')
    for s in sources:
        if digest(s['path']) != s['sha256']:
            raise ValueError('source digest mismatch')
    scenario = next((s['sha256'] for s in sources if s['role'] == 'synthetic_bars'), None)
    blockers = audit_contracts(contracts, decision_date=as_of, scenario_hash=scenario)
    days = []
    for d in sorted(keys.date.unique()):
        blockers.extend(f'{d}: {b}' for b in audit_contracts(contracts, decision_date=d, scenario_hash=scenario))
        gates = gate_rows.get(d)
        counts = {}
        for family in FAMILIES:
            try:
                family_gates = gates.get(family) if isinstance(gates, dict) else gates
                allowed = eligibility(family_gates, decision_date=d, tickers=tickers, family=family, decision_at=decision_times.get(d)) if family_gates is not None else None
                if allowed is None:
                    raise ValueError('missing dated gate rows')
                counts[family] = sum(allowed.values())
            except ValueError as exc:
                counts[family] = None
                blockers.append(f'{d} {family}: {exc}')
        snapshot = frame.loc[keys.date.to_numpy() == d].sort_values('ticker').sort_index(axis=1)
        snapshot_hash = hashlib.sha256(
            json.dumps(list(snapshot.columns)).encode() +
            pd.util.hash_pandas_object(snapshot, index=False).to_numpy().tobytes()).hexdigest()
        days.append(dict(date=d, phase=calendar.phase(d), tickers=500,
                         input_snapshot_sha256=snapshot_hash, decision_at=decision_times.get(d),
                         next_open=calendar.sessions[calendar.sessions.index(d)+1] if d != calendar.sessions[-1] else None,
                         eligible=counts))
    return dict(schema_version=1, status='BLOCKED' if blockers else 'INPUT_CONTRACT_VALIDATED',
                as_of=as_of, sources=sources, contracts=contracts, daily=days,
                blockers=blockers, proof_opened=False,
                calendar=dict(train_end=calendar.train_end, validation_end=calendar.validation_end,
                              proof_start=calendar.proof_start),
                universe_sha256=hashlib.sha256(json.dumps(sorted(tickers)).encode()).hexdigest())
