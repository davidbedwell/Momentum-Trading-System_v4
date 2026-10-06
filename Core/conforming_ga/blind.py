"""Blind replay ordering barrier."""
from __future__ import annotations
from .gates import require_all_fold_freezes
def authorize_blind_replay(paths,hashes):
    return require_all_fold_freezes(paths,hashes)
