"""Actual chronological replay fitness adapter for the existing GA6 pilot.
Research bridge: evolves conditional exit override only. Does NOT claim full
GA6/GA7 proposal coordination or calibrated opportunity allocation.
"""
import numpy as np
from discovery.competitive_ga.manager_evolution_v1 import population,offspring,identity

def exit_policy(genes):
    def manager(age,row,held):
        close=float(row["close"])
        gain=close/held.entry_price-1.
        # causal conditional override using only current close, entry, age
        return (age>=5 and gain < -genes.min_edge and
                float(row.get("volatility",0) or 0)>genes.risk_penalty/4)
    return manager

def evaluate(genes,start_date="2020-01-01",end_date="2020-12-31"):
    # Native research imports read external schemas. Keep pure policy and
    # injected-evaluator tests usable when those archives are unavailable.
    from discovery.competitive_ga.ga6_native_position_replay import run
    result=run(manager=exit_policy(genes),manager_entry_cap=genes.max_initial,start_date=start_date,
               end_date=end_date,output=False)
    # No invented expectancy/stability: only observed portfolio metrics.
    return result,(result["net_return"],-result["max_drawdown"])

def evaluate_population(genomes,**kwargs):
    return [(g,evaluate(g,**kwargs)) for g in genomes]

if __name__=="__main__":
    g=population(1)[0]
    result,fitness=evaluate(g)
    print({"genome":identity(g),"fitness_observed":fitness,"replay":result})
