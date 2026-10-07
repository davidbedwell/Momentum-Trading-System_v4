#!/usr/bin/env python3
from layered_stage_common_20261007 import *
bank=load_bank();rows=[]
for c in bank:
 confidence=max(0,min(1,c['transport_ev']/(abs(c['transport_ev'])+max(1e-9,abs(c['transport_lcb']-c['transport_ev'])))))
 rows.append({'candidate':c,'evidence_weight':confidence,'rule':'relative evidence weight only; portfolio normalization deferred to Stage9'})
write(8,'position-sizing',{'sizing_evidence':rows,'constraints':['no leverage','uncertainty reduces weight','context may modify size, never permission']})
