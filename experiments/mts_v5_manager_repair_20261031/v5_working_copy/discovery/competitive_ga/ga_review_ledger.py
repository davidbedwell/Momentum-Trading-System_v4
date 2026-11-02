"""Durable, deduplicated research review claims. No GA launch or promotion.
Uses SQLite transactions so concurrent workers cannot claim the same event twice.
"""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from .ga_review_gate import review_due

NY=ZoneInfo('America/New_York')

class ReviewLedger:
    def __init__(self,path):
        self.path=str(path)
        with sqlite3.connect(self.path,timeout=30) as db:
            db.execute('CREATE TABLE IF NOT EXISTS review_events (event_key TEXT PRIMARY KEY, reason TEXT NOT NULL, observed_at TEXT NOT NULL, evolve INTEGER NOT NULL, status TEXT NOT NULL)')

    def claim(self,now,dramatic_regime_change=False,drift_confirmed=False,event_id=None):
        decision=review_due(now,dramatic_regime_change,drift_confirmed)
        if not decision.review:return None
        if decision.reason=='DRAMATIC_REGIME_CHANGE':
            if not event_id or not isinstance(event_id,str):
                raise ValueError('stable causal regime event_id required')
            key='regime:'+event_id
        else:
            key='friday:'+now.astimezone(NY).date().isoformat()
        with sqlite3.connect(self.path,timeout=30,isolation_level=None) as db:
            db.execute('BEGIN IMMEDIATE')
            cursor=db.execute('INSERT OR IGNORE INTO review_events(event_key,reason,observed_at,evolve,status) VALUES (?,?,?,?,?)',
                              (key,decision.reason,now.isoformat(),int(decision.evolve),'PENDING'))
            claimed=cursor.rowcount==1
            db.commit()
        return (key,decision) if claimed else None

    def events(self):
        with sqlite3.connect(self.path,timeout=30) as db:
            return db.execute('SELECT event_key,reason,observed_at,evolve,status FROM review_events ORDER BY observed_at').fetchall()
