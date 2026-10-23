"""Fail-closed trial-family accounting; no statistical significance without full ledger."""
from collections import Counter

def family_census(ledger,expected_discovery=None,expected_feedback=None):
 rows=ledger.db.execute('SELECT trial_id,chromosome_id,activity,niche,generation,role,reward_status FROM trials ORDER BY trial_id').fetchall()
 ids=[r[0] for r in rows]
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate trial IDs')
 roles=Counter(r[5] for r in rows)
 if expected_discovery is not None and roles['discovery']!=expected_discovery:raise ValueError('Discovery trial count mismatch')
 if expected_feedback is not None and roles['development_feedback']!=expected_feedback:raise ValueError('Development-feedback trial count mismatch')
 if any(r[5] not in ('discovery','development_feedback') for r in rows):raise ValueError('Invalid development role')
 activities=Counter(r[2] for r in rows)
 return {'total_trials':len(rows),'discovery_trials':roles['discovery'],'development_feedback_trials':roles['development_feedback'],'credited_feedback_trials':sum(r[5]=='development_feedback' and r[6]=='CREDITED' for r in rows),'activities':dict(activities),'family_complete':expected_discovery is not None and expected_feedback is not None,'statistically_certified':False}

def require_complete_family(census):
 if not census['family_complete'] or census['total_trials']<1:raise PermissionError('Full discovery and adaptive-feedback family must be reconciled before SPA or promotion')
 return census['total_trials']
