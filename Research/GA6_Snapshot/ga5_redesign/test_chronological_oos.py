import pandas as pd
import pytest
from ga5_redesign.chronological_oos import partition

def test_chronological_no_overlap():
 frame=pd.DataFrame({'date':['2020-01-01','2020-06-01','2021-01-01','2022-01-01'],'ticker':['A']*4})
 a,b,c=partition(frame,'2020-06-01','2022-01-01')
 assert len(a)==1 and len(b)==2 and len(c)==1
 assert a.date.max()<b.date.min()<c.date.min()

def test_invalid_folds_fail():
 frame=pd.DataFrame({'date':['2020-01-01','2021-01-01'],'ticker':['A','A']})
 with pytest.raises(ValueError):partition(frame,'2021-01-01','2021-01-01')
 with pytest.raises(ValueError):partition(frame,'2021-01-01','2022-01-01')
