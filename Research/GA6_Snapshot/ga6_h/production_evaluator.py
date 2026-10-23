"""Picklable, explicit GA6-H measured evaluator adapter.
Only caller-provided audited discovery panels and verified earnings schedules are used.
"""
from dataclasses import dataclass
from historical_fitness import measured_discovery_fitness

@dataclass
class HistoricalDiscoveryEvaluator:
    folds:list
    schedules:dict
    verified_tickers:set
    minimum_completed:int=3
    def __call__(self,genome):
        return measured_discovery_fitness(genome,self.folds,self.schedules,self.verified_tickers,
                                          minimum_completed=self.minimum_completed)
