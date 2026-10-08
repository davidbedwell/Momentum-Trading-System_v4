"""Verify a Stage 1 PIT context artifact against Stage 2 predictor rows.

Does not assert Stage 1 scientific certification or classify regimes.
"""
import hashlib
from pathlib import Path
import pandas as pd

KEYS=("security_id","effective_date")

def verify_context_link(predictors, context, artifact_path, *, scope):
    if not scope or not isinstance(scope,str):
        raise ValueError("Explicit Stage 1 scope required")
    if not set(KEYS).issubset(predictors.columns) or not set(KEYS).issubset(context.columns):
        raise ValueError("Missing alignment keys")
    if not isinstance(artifact_path,(str,Path)) or not Path(artifact_path).is_file():
        raise ValueError("Stage 1 artifact missing")
    if not len(context) or context.duplicated(list(KEYS)).any() or predictors.duplicated(list(KEYS)).any():
        raise ValueError("Empty or duplicated PIT keys")
    a=predictors.loc[:,KEYS].copy()
    b=context.loc[:,KEYS].copy()
    for frame in (a,b):
        frame["security_id"]=frame["security_id"].astype(str)
        frame["effective_date"]=pd.to_datetime(frame["effective_date"],utc=True,errors="raise")
    if a.isna().any().any() or b.isna().any().any():
        raise ValueError("Null PIT keys")
    keys=a.merge(b,how="left",on=list(KEYS),indicator=True,validate="one_to_one")
    if not keys["_merge"].eq("both").all():
        raise ValueError("Stage 1 context coverage incomplete")
    digest=hashlib.sha256(Path(artifact_path).read_bytes()).hexdigest()
    return {"status":"ALIGNED_NOT_SCIENTIFICALLY_CERTIFIED","sha256":digest,
            "scope":scope,"aligned_rows":len(a),"context_rows":len(b)}
