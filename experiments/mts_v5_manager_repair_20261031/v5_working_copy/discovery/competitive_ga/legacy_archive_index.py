"""Read-only full GA4/HORIZONS bank discovery; no strategy pruning."""
import sqlite3
from dataclasses import dataclass
from pathlib import Path
DB=Path('/opt/mts/thunder-migration/mts-certification-20261011/cagr_mdd_library_20261013/STRATEGY_BANK_INDEX.sqlite')
STUDIES={'GA4_DIAGNOSTIC':'GA4','HORIZONS':'HORIZONS'}
@dataclass(frozen=True)
class LegacyStrategy:
 chromosome_id:str
 family:str
 definition:str
 chromosome:str
 horizon:str

def iter_strategies(study,db_path=DB):
 if study not in STUDIES:raise ValueError('unknown study')
 conn=sqlite3.connect('file:'+str(db_path)+'?mode=ro',uri=True)
 try:
  for key,definition,chromosome,horizon in conn.execute('SELECT strategy_key,definition,chromosome,horizon FROM strategies WHERE study=? AND definition_status=?',(study,'RESOLVED')):
   yield LegacyStrategy(key,STUDIES[study],definition,chromosome,horizon)
 finally:conn.close()

def counts(db_path=DB):
 conn=sqlite3.connect('file:'+str(db_path)+'?mode=ro',uri=True)
 try:return {STUDIES[s]:conn.execute('SELECT count(*) FROM strategies WHERE study=? AND definition_status=?',(s,'RESOLVED')).fetchone()[0] for s in STUDIES}
 finally:conn.close()
