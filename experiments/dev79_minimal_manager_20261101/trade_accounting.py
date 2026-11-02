"""Trade accounting with additions and partial reductions.
Risk units are actual cumulative capital committed times initial stop fraction.
"""
from dataclasses import dataclass

@dataclass
class TradeAccount:
    invested:float=0.
    realized:float=0.
    open_cost:float=0.
    risk_units:float=0.
    def buy(self,cost,stop_fraction):
        if cost<=0 or not 0<stop_fraction<=1:raise ValueError('Invalid buy')
        self.invested+=cost
        self.open_cost+=cost
        self.risk_units+=cost*stop_fraction
    def sell(self,proceeds,fraction):
        if not 0<fraction<=1 or self.open_cost<=0:raise ValueError('Invalid sell')
        allocated=self.open_cost*fraction
        self.open_cost-=allocated
        self.realized+=proceeds-allocated
    def finish(self,proceeds):
        if self.risk_units<=0:raise ValueError('No risk capital')
        profit=self.realized+proceeds-self.open_cost
        return profit/self.invested,profit/self.risk_units
