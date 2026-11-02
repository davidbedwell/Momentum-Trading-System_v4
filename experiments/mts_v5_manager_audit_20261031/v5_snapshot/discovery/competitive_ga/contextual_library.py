"""Contextual chromosome library. Index all recoverable candidates, never global top-N.
This is a selector research component, not a certified execution/fitness engine.
"""
from dataclasses import dataclass
from collections import defaultdict
from math import exp, log, sqrt, isfinite
import hashlib
import json
import sqlite3

@dataclass(frozen=True)
class Candidate:
    chromosome_id: str
    generation: str
    family: str
    behavior: str
    source: str

@dataclass(frozen=True)
class Observation:
    chromosome_id: str
    context: tuple
    decision_session: int
    maturity_session: int
    net_r: float
    source: str = "shadow"

class ContextLibrary:
    """Persist identities and *matured* causal feedback. No overall CAGR exclusion."""
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS candidates (
          chromosome_id TEXT PRIMARY KEY, generation TEXT NOT NULL,
          family TEXT NOT NULL, behavior TEXT NOT NULL, source TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS candidates_behavior ON candidates(behavior,family);
        CREATE TABLE IF NOT EXISTS observations (
          id INTEGER PRIMARY KEY, chromosome_id TEXT NOT NULL,
          context TEXT NOT NULL, decision_session INTEGER NOT NULL,
          maturity_session INTEGER NOT NULL, net_r REAL NOT NULL,
          source TEXT NOT NULL, CHECK(maturity_session>decision_session));
        CREATE INDEX IF NOT EXISTS observations_causal ON observations(chromosome_id,maturity_session);
        """)
    def register(self, items):
        with self.db:
            self.db.executemany(
              "INSERT OR IGNORE INTO candidates VALUES (?,?,?,?,?)",
              ((c.chromosome_id,c.generation,c.family,c.behavior,c.source) for c in items))
    def record(self, observation):
        if not isfinite(observation.net_r):
            raise ValueError("nonfinite outcome")
        with self.db:
            self.db.execute("INSERT INTO observations(chromosome_id,context,decision_session,maturity_session,net_r,source) VALUES (?,?,?,?,?,?)",
                (observation.chromosome_id,json.dumps(observation.context),observation.decision_session,
                 observation.maturity_session,observation.net_r,observation.source))
    def candidates(self, behavior=None):
        if behavior is None:
            rows=self.db.execute("SELECT * FROM candidates")
        else:
            rows=self.db.execute("SELECT * FROM candidates WHERE behavior=?",(behavior,))
        return [Candidate(*r) for r in rows]
    def select(self, context, asof_session, eligible_ids, limit=50, exploration=0.15, min_samples=5):
        """Return ranked eligible candidates, not portfolio orders.
        Context is a vector computed at close t; outcome maturity must be < t.
        Never inspect uncompleted trades or future labels. Exploration rotates
        deterministic candidates with weak evidence, preserving rare specialists.
        """
        if asof_session<0 or limit<1 or not 0<=exploration<=1:
            raise ValueError("invalid selection request")
        eligible=set(eligible_ids)
        if not eligible:return []
        rows=self.db.execute("SELECT chromosome_id,context,net_r FROM observations WHERE maturity_session<?",(asof_session,))
        evidence=defaultdict(list)
        for cid,stored,net_r in rows:
            if cid not in eligible:continue
            old=json.loads(stored)
            if len(old)!=len(context):continue
            distance=sum((float(a)-float(b))**2 for a,b in zip(old,context))
            weight=exp(-min(60.0,distance/2.0))
            if weight>1e-6:evidence[cid].append((weight,net_r))
        scored=[]
        for c in self.candidates():
            if c.chromosome_id not in eligible:continue
            obs=evidence[c.chromosome_id]
            mass=sum(w for w,_ in obs)
            mean=sum(w*r for w,r in obs)/mass if mass else 0.
            uncertainty=1/sqrt(1+mass)
            # Conservative conditional utility, not global historical ranking.
            score=mean-0.5*uncertainty
            novel=mass<min_samples
            tie=int(hashlib.sha256((str(asof_session)+c.chromosome_id).encode()).hexdigest()[:12],16)
            scored.append((score,tie,c,novel,mass))
        scored.sort(key=lambda x:(-x[0],x[1]))
        slots=min(limit,len(scored))
        explore_slots=min(slots,int(round(slots*exploration)))
        exploit=[x for x in scored if not x[3]][:slots-explore_slots]
        used={x[2].chromosome_id for x in exploit}
        novel=sorted((x for x in scored if x[2].chromosome_id not in used),
                     key=lambda x:(not x[3],x[1]))
        selected=(exploit+novel[:slots-len(exploit)])
        return [{"chromosome_id":x[2].chromosome_id,"family":x[2].family,
                 "behavior":x[2].behavior,"conditional_score":x[0],
                 "effective_samples":x[4],"exploration":x[3]} for x in selected]

    def inventory(self):
        """Persistent library size, independent of trade frequency."""
        return dict(self.db.execute("SELECT generation,COUNT(*) FROM candidates GROUP BY generation"))

    def eligible_by_context(self, context, asof_session, feature_gate, *, behaviors=None):
        """Use a caller's *causal* native feature/trigger gate for ALL candidates.
        The gate receives (Candidate, context, asof_session); it must not use
        realized future returns. Never filter by lifetime performance or use count.
        """
        for candidate in self.candidates():
            if behaviors is not None and candidate.behavior not in behaviors:
                continue
            if feature_gate(candidate, context, asof_session):
                yield candidate

    def select_from_gate(self, context, asof_session, feature_gate, *,
                         behaviors=None, limit=50, exploration=.15):
        eligible=[c.chromosome_id for c in self.eligible_by_context(
            context,asof_session,feature_gate,behaviors=behaviors)]
        return self.select(context,asof_session,eligible,limit=limit,
                           exploration=exploration)

    def record_batch(self, observations):
        """Store actual/shadow outcomes, never synthetic counterfactuals without
        their complete execution and position assumptions being recorded elsewhere.
        """
        with self.db:
            for o in observations:
                if not isfinite(o.net_r):
                    raise ValueError("nonfinite outcome")
                self.db.execute(
                    "INSERT INTO observations(chromosome_id,context,decision_session,maturity_session,net_r,source) VALUES (?,?,?,?,?,?)",
                    (o.chromosome_id,json.dumps(o.context),o.decision_session,
                     o.maturity_session,o.net_r,o.source))
