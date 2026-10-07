#!/usr/bin/env python3
"""Frozen non-outcome structural reachability smoke: 2 islands x 20 generations."""
import json,random
from pathlib import Path
import numpy as np
from Core.g3.production import *
from Core.g3.starter import planted_dataset
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'Research/G3';SEED=20261007;NF=17;POP=256;ISLANDS=2;GENS=20
# Planted/development data only; outcomes are used only to generate behavior descriptors, never selection quality.
data={}
for i in range(8):
 x,y,_=planted_dataset(seed=7000+i,n=1200,p=NF,h=60,effect=.01);data[f'P{i}']=(x,y)
pops=[[random_genome(stable_seed(SEED,'reach',i,j),NF) for j in range(POP)] for i in range(ISLANDS)]
seen=set();all_desc=[];imm=[];qd=None;occupied=set()
for gen in range(GENS):
 for isl in range(ISLANDS):
  desc=[]
  for g in pops[isl]:
   seen.add(genome_key(g));d=descriptor(evaluate_genome(g,data,10));desc.append(d);all_desc.append(d)
  if qd is None and isl==ISLANDS-1:
   qd=qd_fit(np.asarray(all_desc),SEED,256)
  if qd is not None:
   occupied.update(qd_cell(d,qd) for d in desc)
  # Search-grammar reachability only: 85% mutation/crossover lineage + frozen 15% random immigrants.
  r=random.Random(stable_seed(SEED,gen,isl));new=[]
  while len(new)<POP:
   if r.random()<.15:
    g=random_genome(stable_seed(SEED,'imm',gen,isl,len(new)),NF);imm.append(genome_key(g))
   else:g=mutate(r.choice(pops[isl]),stable_seed(SEED,'mut',gen,isl,len(new)),NF)
   new.append(g)
  pops[isl]=new
occ=len(occupied)/256;unique=len(seen)/(ISLANDS*POP*GENS);out={'format':'MTS_G3_PRODUCTION_REACHABILITY_V1','complete':True,'islands':2,'population':256,'generations':20,'unique_genome_rate':unique,'descriptor_cells_occupied':len(occupied),'descriptor_occupancy':occ,'random_immigrant_count':len(set(imm)),'decision':'PASS_SEARCH_REACHABILITY' if occ>=.15 else 'STOP_SEARCH_REACHABILITY_FAILED'}
(R/'MTS_G3_PRODUCTION_REACHABILITY_20261007.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
