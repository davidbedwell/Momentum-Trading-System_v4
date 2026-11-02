"""Local v2 executor. Read authorization precedes outcome access; failures consume Stage1."""
import json
import math
import platform
import statistics as st
from collections import defaultdict
from .adapters import ROOT, local, available, timestamp
from .core import SIGNALS, add_months, form_rows, metrics, placebo, ic
from .gate import stage_gate
from .storage import digest, file_hash, publish

STATE = ROOT / 'research_state'


def configuration(manifest):
    return dict(manifest=manifest, python=platform.python_version(), protocol=file_hash(ROOT/'CONTROLLING_PROTOCOL_V2.md'),
                conventions=file_hash(ROOT/'RESEARCH_PROTOCOL.md'),
                implementation={p.name: file_hash(p) for p in sorted((ROOT/'sector_pipeline').glob('*.py'))})


def load_record(path):
    record = json.loads(path.read_text())
    if record['hash'] != digest(record['body']):
        raise ValueError('Ledger integrity failure')
    return record['body']


def commit(path, body):
    publish(path, dict(body=body, hash=digest(body)))


def verify_coverage(bundle, years):
    """Check evidence bytes and normalized coverage, never accept a certified boolean alone.

    Evidence is local, explicit provenance, not independent authentication of a vendor.
    The verifier cannot establish the truth of a fabricated source archive.
    """
    sessions = bundle['sessions']
    if sessions != sorted(set(sessions)) or not sessions:
        raise ValueError('Invalid explicit exchange sessions')
    closes = bundle['closes']
    opens = bundle['opens']
    for date in sessions:
        if timestamp(closes[date]).date().isoformat() != date or timestamp(opens[date]) >= timestamp(closes[date]):
            raise ValueError('Invalid exchange session timestamps')
    evidence = bundle['evidence']
    normalized = dict(calendar=dict(sessions=sessions,closes=closes,opens=opens),
                      membership=dict(members=bundle['members'],inventory=bundle['inventory']),
                      gics=bundle['members'],identities=bundle['members'],prices=bundle['prices'],
                      fundamentals=bundle['fundamentals'],earnings=bundle['earnings'])
    for kind in ('calendar', 'membership', 'gics', 'identities', 'prices', 'fundamentals', 'earnings'):
        item = evidence[kind]
        if item.get('status') != 'verified' or not item.get('reviewer') or not item.get('method'):
            raise ValueError('Unverified source: ' + kind)
        if kind == 'prices' and 'yahoo' in item.get('provider', '').lower():
            raise ValueError('Yahoo prices remain provisional')
        if kind in ('membership','gics') and 'wikipedia' in item.get('provider','').lower():
            raise ValueError('Wikipedia alone is insufficient')
        evidence_path = local(item['path'])
        if file_hash(evidence_path) != item['sha256']:
            raise ValueError('Evidence hash mismatch: ' + kind)
        attestation = json.loads(evidence_path.read_text())
        if attestation.get('normalized_hash') != digest(normalized[kind]):
            raise ValueError('Normalized source binding mismatch: '+kind)
    months = {}
    for date in sessions:
        months[date[:7]] = date
    expected = [f'{year}-{month:02d}' for year in years for month in range(1,13)
                if f'{year}-{month:02d}' <= '2026-09']
    if any(m not in months for m in expected):
        raise ValueError('Missing formation month')
    prices, members = bundle['prices'], bundle['members']
    for month in expected:
        t = months[month]
        active = [m for m in members if m['start'] <= t < m['end']]
        inventory = bundle['inventory'].get(t)
        if not active or inventory is None or sorted(m['symbol'] for m in active) != sorted(inventory):
            raise ValueError('PIT inventory mismatch at ' + t)
        if len(set(inventory)) != len(inventory):
            raise ValueError('Duplicate PIT identity')
        for member in active:
            if not member.get('sector') or not member.get('identity') or not member.get('available_at') or not available(member['available_at'],closes[t]):
                raise ValueError('Missing PIT identity/GICS availability')
            rows = prices.get(member['symbol'], [])
            bydate = {r['date']: r for r in rows}
            if len(bydate) != len(rows) or rows != sorted(rows, key=lambda r:r['date']):
                raise ValueError('Duplicate or unordered prices')
            endpoint = max((d for d in sessions if d[:7] == add_months(t,-13)[:7]),default=None)
            if endpoint is None:
                raise ValueError('Missing t-13 momentum endpoint')
            start = min(sessions.index(t)-252,sessions.index(endpoint))
            end = max(d for d in sessions if d <= add_months(t,6))
            if start < 0 or sessions[-1][:7] < add_months(t,6)[:7]:
                raise ValueError('Insufficient signal/horizon calendar')
            for date in sessions[start:sessions.index(end)+1]:
                row = bydate.get(date)
                if row is None or any(not isinstance(row.get(k), (float,int)) or not math.isfinite(row[k]) or row[k] <= 0 for k in ('adj_open','adj_close')):
                    raise ValueError('Missing price/terminal price: '+member['symbol']+' '+date)
                if not row.get('open_available_at') or not available(row['open_available_at'],opens[date]):
                    raise ValueError('Open availability violation')
                if not row.get('available_at') or not available(row['available_at'],closes[date]):
                    raise ValueError('Price availability violation')
    for symbol in {m['symbol'] for m in members}:
        facts = bundle['fundamentals'].get(symbol,{}).get('facts',{}).get('us-gaap',{})
        records = [r for tag in ('GrossProfit','Assets') for r in facts.get(tag,{}).get('units',{}).get('USD',[])]
        records += bundle['earnings'].get(symbol,{}).get('quarterlyEarnings',[])
        if not records or any(not r.get('available_at') for r in records):
            raise ValueError('Missing as-filed/event availability evidence: '+symbol)
        for r in records:
            timestamp(r['available_at'])
    return [months[m] for m in expected]


def missingness(bundle, formations, expected=None):
    issues = []
    bykey = {(r['asof'],r['symbol'],r['horizon']):r for r in formations}
    months = expected if expected is not None else sorted(set(r['asof'] for r in formations))
    for date in months:
        for m in bundle['members']:
            if m['start'] <= date < m['end']:
                for h in (1,3,6):
                    row = bykey.get((date,m['symbol'],h))
                    reasons = ['missing_open_or_terminal_price'] if row is None else [s for s in SIGNALS if row.get(s+'_rank') is None]
                    if row is not None and row.get('excess') is None:
                        reasons.append('incomplete_sector_benchmark')
                    if reasons:
                        issues.append(dict(asof=date,symbol=m['symbol'],horizon=h,reasons=reasons))
    return issues


def lookahead(rows, allowed=None):
    lookup = {(r['asof'][:7],r['symbol'],r['horizon']):r for r in rows}
    groups = defaultdict(list)
    for row in rows:
        nxt = lookup.get((add_months(row['asof'],1)[:7],row['symbol'],row['horizon']))
        if nxt is not None and row.get('excess') is not None:
            for signal in SIGNALS:
                if allowed is not None and f"{signal}_{row['horizon']}" not in allowed:
                    continue
                value = nxt.get(signal+'_rank')
                if value is not None:
                    groups[row['asof'],row['sector'],row['horizon'],signal].append((value,row['excess']))
    return dict(warning='Future signal versus prior return can correlate through persistence; not definitive proof of leakage.',
                sector_month=[dict(asof=k[0],sector=k[1],horizon=k[2],signal=k[3],ic=ic(*zip(*v))) for k,v in sorted(groups.items())])


def evaluate(bundle, years, expected, allowed=None):
    formation_years = list(range(2016,2027)) if bundle.get('stage')==2 else years
    rows = form_rows(bundle['prices'], bundle['members'], formation_years, bundle['fundamentals'], bundle['earnings'], sessions=bundle['sessions'], closes=bundle['closes'])
    evaluation_rows = [r for r in rows if int(r['asof'][:4]) in years]
    issues = missingness(bundle, evaluation_rows, expected)
    allowed_metrics = None if allowed is None else set(allowed) | {k.split('_')[0]+'_6' for k in allowed}
    monthly, summary = metrics(rows, allowed_metrics, set(expected), {2019,2020} if bundle.get('stage')==2 and 2019 not in years and 2020 not in years else set())
    for key, value in summary.items():
        signal, h = key.split('_'); h = int(h)
        selected = [r for r in monthly if r['signal']==signal and r['horizon']==h]
        dates = set(r['asof'] for r in selected if r['ic'] is not None)
        value['complete'] = dates == set(expected) and all(r['coverage']==1 and r['ic'] is not None and r['spread'] is not None and r['turnover'] is not None for r in selected) and not any(i['horizon']==h for i in issues)
        value['placebo'] = placebo(evaluation_rows,signal,h)
        value['placebo_pass'] = value['placebo']['passed']
        direction = -1 if signal=='H5' else 1
        value['raw_mean'], value['raw_t'] = value['mean'],value['t']
        value['mean'] = value['mean']*direction if value['mean'] is not None else None
        value['t'] = value['t']*direction if value['t'] is not None else None
        bydate = defaultdict(list)
        for r in selected:
            if r['net_spread_15bps'] is not None:
                bydate[r['asof']].append(r['net_spread_15bps'])
        value['net_spread'] = st.mean(st.mean(v) for v in bydate.values()) if bydate else None
        value['same_sign'] = value['mean'] is not None and value['mean'] > 0
        value['passed'] = h in (1,3) and (allowed is None or key in allowed) and stage_gate(value, 1 if years==list(range(2006,2016)) else 2)
    return dict(summary=summary,monthly=monthly,missingness=issues,lookahead=lookahead(evaluation_rows, allowed_metrics),
                decay={s:{str(h):summary.get(f'{s}_{h}',{}).get('mean') for h in (1,3,6)} for s in SIGNALS})


def _execute(bundle_path, stage, manifest):
    """The once-only slot is protocol-global, not configurable by caller or input hash."""
    if manifest.get('protocol_version') != 2 or manifest.get('stage1') != list(range(2006,2016)) or manifest.get('stage2') != list(range(2016,2027)) or manifest.get('contaminated_years') != [2019,2020]:
        raise ValueError('Controlling v2 stage intervals and exclusions required')
    config = configuration(manifest); config_hash = digest(config)
    if stage == 2:
        if not (STATE/'stage1-result.json').exists():
            raise ValueError('Stage2 SEALED: valid Stage1 result required')
        record = load_record(STATE/'stage1-result.json')
        if record['configuration_hash'] != config_hash or not record['valid'] or not record['passers']:
            raise ValueError('Stage2 SEALED: no valid matching Stage1 release')
        primaries = {f'{signal}_{h}' for signal in SIGNALS for h in (1,3)}
        if {k for k,v in record['result']['summary'].items() if not v['exploratory']} != primaries:
            raise ValueError('Stage2 SEALED: incomplete primary family')
        expected_passers = sorted(k for k,v in record['result']['summary'].items() if not v['exploratory'] and stage_gate(v,1))
        if sorted(record['passers']) != expected_passers or not all(v['complete'] for v in record['result']['summary'].values() if not v['exploratory']):
            raise ValueError('Stage2 SEALED: invalid gate record')
        stage1_claim = load_record(STATE/'stage1-claim.json')
        if record['claim_hash'] != digest(stage1_claim):
            raise ValueError('Stage2 SEALED: claim binding mismatch')
    elif stage != 1:
        raise ValueError('Unknown stage')

    path = local(bundle_path)
    # Bundle is stage-specific. No blind bundle is opened above the Stage2 seal.
    existing = STATE/f'stage{stage}-claim.json'
    if existing.exists():
        old = load_record(existing)
        if old['configuration_hash'] != config_hash or old['file_hash'] != file_hash(path):
            raise ValueError('Once-only slot already claimed with different configuration/input')
        completed = STATE/f'stage{stage}-result.json'
        if completed.exists():
            return load_record(completed)
    bundle = json.loads(path.read_text())
    years = manifest['stage1'] if stage==1 else manifest['stage2']
    if bundle.get('stage') != stage:
        raise ValueError('Stage-specific bundle required')
    expected = verify_coverage(bundle, years)
    claim = dict(configuration_hash=config_hash,input_hash=digest(bundle),file_hash=file_hash(path),stage=stage)
    claim_path = STATE/f'stage{stage}-claim.json'
    if not claim_path.exists():
        commit(claim_path,claim)
    elif load_record(claim_path) != claim:
        raise ValueError('Claim mismatch')
    result = evaluate(bundle,years,expected, None if stage==1 else record['passers'])
    valid = all(v['complete'] for k,v in result['summary'].items() if not v['exploratory'])
    if stage == 2:
        clean_years = [y for y in years if y not in (2019,2020)]
        result['controlling_excluded_2019_2020'] = evaluate(bundle,clean_years,[d for d in expected if int(d[:4]) in clean_years],record['passers'])
        result['contaminated_years'] = [2019,2020]
    controlling = result if stage==1 else result['controlling_excluded_2019_2020']
    valid = valid and all(v['complete'] for v in controlling['summary'].values() if not v['exploratory'])
    passers = [k for k,v in controlling['summary'].items() if v['passed']] if valid else []
    body = dict(configuration_hash=config_hash,claim_hash=digest(claim),valid=valid,passers=passers,result=result)
    commit(STATE/f'stage{stage}-result.json',body)
    return body


def execute(bundle_path, stage, manifest):
    # Serialize execution, including resumes. A second worker cannot evaluate the slot.
    import fcntl
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE/'executor.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Executor already active; no duplicate evaluation') from exc
        return _execute(bundle_path,stage,manifest)


def register_variant(name, specification, family):
    if not name or name in SIGNALS or name not in family or len(set(family)) != len(family):
        raise ValueError('Unique variant and expanded family required')
    primary = {f'{s}_{h}' for s in SIGNALS for h in (1,3)}
    if not primary <= set(family):
        raise ValueError('Expanded family must include all twelve primaries')
    body = dict(name=name,specification=specification,family=sorted(family))
    commit(STATE/'variants'/(digest(name)+'.json'),body)
    return body
