"""Research-only native entry decisions and shared-capital next-open replay.
Does not yet evaluate held-position native decisions or manager-GA fitness.
"""
import json,sqlite3
from .synthetic_fiveyear_panel import load_year
from .native_signal_smoke import DB,worker
from engines.portfolio_replay.kernel import Replay,Bar,Signal

def run(scenario=1,chromosomes=3,sessions=12,start_session=300):
 frame=load_year(scenario)
 dates=sorted(frame.date.unique())[start_session:start_session+sessions]
 if len(dates)<3:raise ValueError('insufficient sessions')
 with sqlite3.connect(DB) as db:
  records=db.execute('select id,definition from chromosomes limit ?', (chromosomes,)).fetchall()
 if not records:raise ValueError('no chromosomes')
 replay=Replay();evaluated=0;entries=0;missing=0
 for date in dates:
  day=frame.loc[frame.date==date]
  rows=day.to_dict('records')
  bars={r['ticker']:Bar(float(r['open']),float(r['close'])) for r in rows}
  signals=[];seen=set()
  for ident,definition in records:
   # Worker uses the native structural evaluator; outputs aggregate counts only.
   result=worker((ident,definition,rows))
   if result['errors']:raise RuntimeError(result['errors'])
   evaluated+=result['evaluated'];entries+=result['entries'];missing+=result['missing']
  replay.day(str(date),bars,signals)
 return {'scenario':scenario,'sessions':len(dates),'chromosomes':len(records),
         'native_evaluations':evaluated,'entry_decisions':entries,'missing_features':missing,
         'portfolio_fills':len(replay.ledger),'status':'NATIVE_DECISION_REPLAY_SMOKE_NO_ORDER_BRIDGE'}
