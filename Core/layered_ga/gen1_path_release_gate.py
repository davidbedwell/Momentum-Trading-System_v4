"""Fail-closed release-time gate: features need verified as-of availability."""
import pandas as pd
def verify_feature_release(feature_rows,decision_times,release_times,feature_names):
 if len(feature_rows)!=len(decision_times) or len(release_times)!=len(decision_times):
  raise ValueError('Misaligned timestamps')
 if not feature_names:raise ValueError('No feature names')
 decision=pd.to_datetime(decision_times,utc=True,errors='coerce')
 release=pd.to_datetime(release_times,utc=True,errors='coerce')
 if decision.isna().any() or release.isna().any():raise ValueError('Missing or invalid release timestamp')
 if (release>decision).any():raise ValueError('Feature published after decision')
 if not all(name in feature_rows.columns for name in feature_names):raise ValueError('Missing feature')
 if feature_rows[list(feature_names)].isna().any().any():raise ValueError('Missing feature values')
 return {'status':'RELEASE_TIMESTAMPS_VALIDATED_FOR_PROVIDED_ROWS','rows':len(decision),
         'feature_names':list(feature_names),'note':'Source lineage must separately establish authenticity'}
