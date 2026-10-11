"""Regression: repeated stock dates must not compress excluded trading sessions."""
import json,pathlib,tempfile
import numpy as np,pandas as pd
from scripts.thirteen_window_crash_mask_20261011 import mask
from Core.layered_ga.ga4_oracle_crash_mask import frozen_episode_intervals
cal=pd.bdate_range('2020-01-01',periods=140)
frame_dates=pd.DatetimeIndex(np.repeat(cal.values,3))
episodes={'episodes':{'synthetic':{'peak':str(cal[10].date()),'trough':str(cal[20].date())}}}
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'episodes.json';p.write_text(json.dumps(episodes))
 single=mask(cal,cal,p)
 multi=mask(frame_dates,cal,p)
 assert multi.shape==(3*len(cal),64)
 assert np.array_equal(multi,np.repeat(single,3,axis=0))
 start,end=frozen_episode_intervals(cal,episodes['episodes'],10)[0]
 assert start==cal[20] and end==cal[30]
 assert not single[19,0] # entry at excluded boundary
 assert not single[29,0] # exit touches excluded boundary
 assert single[30,0] # entry after exclusion
 assert single[0,0]
 print('CALENDAR_INTEGRITY_DUPLICATES_BOUNDARIES_PASS')
