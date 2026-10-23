"""Unrestricted GA5 breeding adapter; niche is historical provenance only.
This does not yet implement scale-in/scale-out or replace the legacy runner.
"""
from dataclasses import replace
from ga5_chromosome_contract import crossover,mutate

def cross_any(a,b,rng):
 # Existing crossover forbids different historical seed labels.
 # Relabel a temporary copy for recombination, retaining parent A provenance.
 return crossover(a,replace(b,niche=a.niche),rng)

def breed(population,rng,count):
 if not population:raise ValueError('Empty population')
 if count<1:raise ValueError('Invalid count')
 children=[]
 while len(children)<count:
  a,b=rng.choices(population,k=2)
  children.append(mutate(cross_any(a,b,rng),rng))
 return children
