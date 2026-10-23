import sys
sys.path.insert(0,'/opt/mts')
from ga6.chronological_validation import split
paths=[ [('2020-01-01',100,100),('2020-01-02',99,99)], [('2020-01-02',100,100),('2020-01-04',100,100)], [('2020-01-03',100,100),('2020-01-04',101,101)] ]
train,valid,excluded=split(paths,'2020-01-03')
assert len(train)==1 and len(valid)==1 and excluded==1
print('PASS chronological split excludes overlapping trades')
