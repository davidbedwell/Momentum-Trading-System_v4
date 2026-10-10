#!/usr/bin/env python3
"""Replay precomputed frozen A/B/C/R1 signals; never regenerate from heldout data."""
import argparse,csv,json,hashlib
from pathlib import Path
from Core.layered_ga.defensive_daily_replay import DayRecord,replay

def parse_bool(value):
    if value in ('True','true','TRUE','1'):return True
    if value in ('False','false','FALSE','0'):return False
    raise ValueError(f'Invalid or missing observed boolean: {value!r}')

def run(source,output):
    source=Path(source); output=Path(output)
    with source.open(newline='') as f:
        reader=csv.DictReader(f)
        needed={'date','A','B','C','R1_evidence'}
        if not needed.issubset(reader.fieldnames or []):
            raise ValueError(f'missing required frozen signal columns: {sorted(needed-set(reader.fieldnames or []))}')
        rows=[DayRecord(row['date'],*[parse_bool(row[k]) for k in ('A','B','C','R1_evidence')]) for row in reader]
    if not rows:raise ValueError('empty state tape')
    events=replay(rows)
    report={'status':'REPLAY_ONLY_NOT_HISTORICAL_SIGNAL_CERTIFICATION',
            'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'sessions':len(events),'defensive_sessions':sum(x['state']=='DEFENSIVE' for x in events),
            'crash_entries':[x['date'] for x in events if x['crash_entry']],
            'r1_exits':[x['date'] for x in events if x['r1_exit']],
            'end_state':events[-1]['state'],'no_brokerage_or_trade_fills':True,
            'protected_banks_not_loaded_by_this_script':True}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(run(a.input,a.output),indent=2))
