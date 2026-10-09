"""DEV80-only Phase B 126-session outcome extension; does not select or breed parents."""
import json,time,pathlib,hashlib,numpy as np,pandas as pd
from Core.layered_ga.stage2_path_v3 import build_execution_paths,build_prospective_costs
root=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint')
out=pathlib.Path('Research/Runs/gen1-merit-screen-20261008/phaseB_dev80_126_20261009');out.mkdir(exist_ok=True)
def status(stage,**kwargs):
 (out/'status.json').write_text(json.dumps({'stage':stage,'time':time.time(),**kwargs},indent=2));print(stage,kwargs,flush=True)
status('READING_RAW')
raw=pd.read_parquet(root/'dev80_raw.parquet')
assert len(raw)==399691, f'unexpected rows {len(raw)}'
status('BUILDING_126_PATHS',rows=len(raw))
paths=build_execution_paths(raw,max_horizon=126)
status('BUILDING_126_COSTS')
costs=build_prospective_costs(raw,paths)
arrays={'endpoint_return':paths.endpoint_return,'low_excursion':paths.low_excursion,'high_excursion':paths.high_excursion,'calendar_days':paths.calendar_days,'long_roundtrip':costs.long_roundtrip,'short_roundtrip':costs.short_roundtrip,'spread_bps':costs.spread_bps,'impact_bps':costs.impact_bps,'adv_dollars':costs.adv_dollars,'regulatory_sell_fraction':costs.regulatory_sell_fraction}
status('VERIFYING_ORIGINAL_63')
original=np.load(root/'dev80_execution_arrays.npz')
checks={}
for key in ('endpoint_return','low_excursion','high_excursion','calendar_days','long_roundtrip','short_roundtrip'):
 a=arrays[key][:,:63];b=original[key]
 checks[key]=bool(np.allclose(a,b,rtol=0,atol=1e-7,equal_nan=True))
status('VALIDATED_63_PREFIX',checks=checks)
if not all(checks.values()):raise RuntimeError('Phase B 126 extension differs from archived 63-session paths; stop for audit')
np.savez_compressed(out/'dev80_execution_arrays_126.npz',**arrays,cluster_ids=original['cluster_ids'])
manifest={'status':'OUTCOME_EXTENSION_BUILT_NOT_CERTIFIED','rows':len(raw),'horizons':126,'prefix_comparisons':checks,'scope':'DEV80 only','sha256':hashlib.sha256((out/'dev80_execution_arrays_126.npz').read_bytes()).hexdigest()}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));status('COMPLETE',manifest=manifest)
