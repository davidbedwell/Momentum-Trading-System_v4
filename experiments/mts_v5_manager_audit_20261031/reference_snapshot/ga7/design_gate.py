"""Fail-closed GA7 launch certification. No discovery run without full design parity."""
import json
from pathlib import Path

REQUIRED = ('chronological_folds','sector_balanced_stock_folds','frozen_fold_membership',
 'independent_fold_promotion','niche_group_evolution','niche_and_unrestricted_competition',
 'actual_r_accounting','p90_mae','full_defense_ab_b1_c_r1',
 'earnings_blackout','pit_feature_provenance','pit_membership_provenance',
 'settled_cash_parity','risk_limits','portfolio_bank_selection',
 'dev87_isolation','dev50b_isolation','blind17_isolation')

def certify(path):
    document=json.loads(Path(path).read_text())
    checks=document.get('checks',{})
    missing=[key for key in REQUIRED if checks.get(key,{}).get('status')!='verified']
    if missing:
        raise RuntimeError('GA7 DESIGN GATE BLOCKED: '+', '.join(missing))
    return document
