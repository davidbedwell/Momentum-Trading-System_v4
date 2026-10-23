"""Frozen entry-equity position loss policy, for independent GA6 risk evaluation."""
from dataclasses import dataclass
from math import isfinite

@dataclass
class PositionRisk:
    entry_equity:float
    cumulative_realized_pnl:float=0.
    remaining_shares:int=0
    cost_basis:float=0.
    reassessed:bool=False
    forced_exit:bool=False

    def __post_init__(self):
        if not isfinite(self.entry_equity) or self.entry_equity<=0:raise ValueError('Bad entry equity')

    def buy(self,shares,price,fee=0.):
        if self.forced_exit:raise ValueError('Cannot reset forced-exit position')
        if shares<=0 or price<=0:raise ValueError('Invalid buy')
        self.cost_basis+=shares*price*(1+fee)
        self.remaining_shares+=shares

    def sell(self,shares,price,fee=0.):
        if shares<=0 or shares>self.remaining_shares or price<0:raise ValueError('Invalid sell')
        avg=self.cost_basis/self.remaining_shares
        self.cumulative_realized_pnl+=shares*price*(1-fee)-shares*avg
        self.cost_basis-=shares*avg
        self.remaining_shares-=shares
        if not self.remaining_shares:self.cost_basis=0.

    def mark(self,price,fee=0.):
        if price<0:raise ValueError('Invalid mark')
        pnl=self.cumulative_realized_pnl+self.remaining_shares*price*(1-fee)-self.cost_basis
        loss=max(0.,-pnl)/self.entry_equity
        if loss>=.01:self.reassessed=True
        if loss>=.02:self.forced_exit=True
        return {'pnl':pnl,'loss_fraction_entry_equity':loss,
                'reassess':self.reassessed,'mandatory_exit':self.forced_exit}
