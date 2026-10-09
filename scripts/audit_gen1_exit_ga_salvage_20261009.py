"""Read-only DEV80 asset and scope audit; does not load protected partitions."""
import hashlib,json,pathlib,datetime
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
assets={'candidate_catalog':R/'all_candidates.jsonl','horizon_assignments':R/'original_4360_train_horizon_20261009/assignments.jsonl','execution_arrays':R/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz','dev80_features':pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet'),'old_forensic':R/'matched_horizon_v4_full_20261009/forensic_matched_path_20261009.json'}
result={'status':'ASSET_INVENTORY_ONLY_NOT_PIT_CERTIFIED','scope':'DEV80','assets':{},'protected_banks_accessed':False}
for name,p in assets.items():
 item={'path':str(p),'exists':p.is_file()}
 if p.is_file():
  item['size_bytes']=p.stat().st_size
  if p.suffix=='.jsonl':
   with p.open() as f:item['lines']=sum(1 for _ in f)
  if p.stat().st_size<2_000_000:
   item['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 result['assets'][name]=item
out=R/'exit_ga_salvage_audit_20261009';out.mkdir(exist_ok=True)
(out/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
