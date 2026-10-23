import json
from pathlib import Path
QUANTILES=json.loads((Path(__file__).parent/"threshold_calibration.json").read_text())["quantiles"]
def calibrated(f,u):
 q=QUANTILES[f];return q[min(len(q)-1,max(0,int(u*len(q))))]
