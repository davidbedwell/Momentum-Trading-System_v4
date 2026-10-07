from pathlib import Path
import sys,time,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_features_v3 import build_dev117_predictors
if __name__=='__main__':
 t=time.time();d=build_dev117_predictors(sector_metadata_path=ROOT/'Research/Runs/layered/sector_metadata_dev117_20261007.json',cache_dir=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/cache',workers=6)
 print(json.dumps({'rows':len(d),'columns':len(d.columns),'seconds':time.time()-t}),flush=True)
