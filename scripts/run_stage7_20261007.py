#!/usr/bin/env python3
from layered_stage_common_20261007 import *
bank=load_bank();ranked=sorted(bank,key=lambda x:(x['transport_ev'],x['transport_n']),reverse=True)
write(7,'capital-competition',{'ranking':ranked,'safe_definition':'historical T-bill competitor required at execution; absence of sufficient credible stock EV permits SAFE','replacement_rule':'challenger must exceed incumbent credible transported EV after friction; no direction inference from exit'})
