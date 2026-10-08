"""Freeze risk policy before *new* search; do not retroactively certify old runs."""
import hashlib,json,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'Research/Protocols/MTS_DISCOVERY_DYNAMIC_ADVERSE_PATH_STOP_PROTOCOL_20261001.md'
text=source.read_text()
assert '6, 8, 10, 12 ATR20' in text and '20%, 25%, 30%, 40%' in text
policy={
 'policy_id':'STAGE2_V3_PRESEARCH_DISASTER_LAYER_20261007',
 'provenance':{'source':str(source.relative_to(root)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
 'metrics':['adverse_excursion_atr20','loss_from_entry_fraction','gap_through_fill_price'],
 'thresholds':{'atr20_sensitivity':[6,8,10,12],'loss_fraction_sensitivity':[.20,.25,.30,.40]},
 'interpretation':'Sensitivity analysis of independent emergency cap; report uncapped and all cap scenarios. No 2R hard ceiling. No cap is chosen based on observed calibration results.',
 'fill_rule':'first available observed price after gap; never assume fill at threshold',
 'status':'FROZEN_FOR_NEW_SEARCH_NOT_CERTIFIED',
 'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'independent_recalculation':None,
 'search_started_at':None,
}
canonical=json.dumps(policy,sort_keys=True,separators=(',',':')).encode()
policy['policy_hash']=hashlib.sha256(canonical).hexdigest()
out=root/'Research/Design/MTS_STAGE2_V3_CATASTROPHIC_POLICY_FREEZE_20261007.json'
if out.exists():
 print('EXISTING_FREEZE_PRESERVED',out)
else:
 out.write_text(json.dumps(policy,indent=2)+'\n');print('FROZEN',out,policy['policy_hash'])
