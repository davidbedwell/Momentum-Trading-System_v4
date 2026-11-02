"""Fail-closed GA7 defense tape: A-v2/B/B1/C triggers and R-1 recovery."""
import csv
from datetime import date
from pathlib import Path

TRIGGERS=('A_v2','B','B1','C')
COMPONENTS=(*TRIGGERS,'R1')

def parse_flag(value,name):
    if str(value).strip().lower() in ('1','true'):return True
    if str(value).strip().lower() in ('0','false'):return False
    raise ValueError('Invalid defense flag '+name+': '+str(value))

def read_defense_state(path):
    with Path(path).open(newline='') as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames or not {'date','defensive',*COMPONENTS}.issubset(reader.fieldnames):
            raise ValueError('Full A-v2/B/B1/C/R1 defense columns required')
        states={}
        previous_day=None
        previous_defensive=None
        for row in reader:
            day=row['date']
            try: parsed=date.fromisoformat(day)
            except (ValueError,TypeError):raise ValueError('Invalid defense date: '+str(day))
            if previous_day is not None and parsed<=previous_day:
                raise ValueError('Defense dates must be strictly increasing: '+day)
            previous_day=parsed
            values={k:parse_flag(row[k],k) for k in ('defensive',*COMPONENTS)}
            triggered=any(values[k] for k in TRIGGERS)
            if triggered and not values['defensive']:
                raise ValueError('Active defense trigger marked normal: '+day)
            if values['R1'] and values['defensive'] and not triggered:
                # R1 may be a raw readiness signal; it does not itself force an exit.
                pass
            if previous_defensive is True and not values['defensive'] and not values['R1']:
                raise ValueError('Defense deactivated without R-1 recovery: '+day)
            previous_defensive=values['defensive']
            states[day]=values
    if not states:raise ValueError('Empty defense tape')
    return states
