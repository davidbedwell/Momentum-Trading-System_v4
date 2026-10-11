import numpy as np,pandas as pd
from scripts.thirteen_window_crash_mask_20261011 import mask,HORIZONS
cal=pd.bdate_range('2020-01-01',periods=130)
episodes={'episodes':{'synthetic':{'peak':str(cal[10].date()),'trough':str(cal[20].date())}}}
import tempfile,json,pathlib
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'episodes.json';p.write_text(json.dumps(episodes))
 a=mask(cal,cal,p)
 assert a.shape==(130,64)
 assert not a[22,0] and not a[12,-1]
 assert a[0,0] and not a[0,-1]
 assert not a[-1,-1]
print('THIRTEEN_WINDOW_CRASH_MASK_TEST_PASS')
