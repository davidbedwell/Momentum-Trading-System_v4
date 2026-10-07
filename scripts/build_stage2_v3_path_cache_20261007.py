from pathlib import Path
import sys,time,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_data_v3 import build_path_cache
if __name__=='__main__':
 t=time.time();cache=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/cache';m=build_path_cache(cache,cache/'dev117_predictors_v3.parquet');print(json.dumps({'seconds':time.time()-t,'rows':m['rows'],'bytes':sum(x['bytes'] for x in m['files'].values())}),flush=True)
