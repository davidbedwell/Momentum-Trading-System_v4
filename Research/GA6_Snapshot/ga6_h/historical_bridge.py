"""Wire causal chromosome rankings into chronological execution.
This is an integration bridge, not a certified fitness evaluator.
"""
import pandas as pd
from historical_feature_adapter import score_session
from daily_simulator import simulate
from performance_metrics import equity_metrics,trade_net_ev
from realized_trade_ledger import realized_trades

def evaluate_chromosome(genome, bars, schedules, verified_tickers, discovery_end_date, price_adjustment_type='unadjusted_with_actions', initial_cash=100000):
    genome.validate()
    if discovery_end_date is None:raise ValueError('discovery end date required')
    required={'date','symbol','Open','Close','tradable_bar'}
    if not required.issubset(bars.columns):raise ValueError('missing execution fields')
    frame=bars.copy()
    frame['date']=pd.to_datetime(frame.date).dt.normalize()
    if frame.date.max()>pd.Timestamp(discovery_end_date).normalize():raise ValueError('data outside discovery')
    rows=[]
    for day,group in frame.groupby('date',sort=True):
        eligible=group[group.get('eligible_signal',pd.Series(True,index=group.index)).fillna(False)]
        ranked=score_session(genome,eligible.to_dict('records'))
        rows.extend({'date':day,**entry} for entry in ranked)
    ranks=pd.DataFrame(rows,columns=['date','symbol','score'])
    equity,trades=simulate(frame,ranks,schedules,verified_tickers,initial_cash=initial_cash,
       hold_sessions=genome.hold_sessions,weight=genome.target_weight,
       entry_threshold=genome.entry_threshold,stop_loss=genome.stop_loss,
       trailing_stop=genome.trailing_stop,replace_threshold=genome.replace_threshold,price_adjustment_type=price_adjustment_type,
       discovery_end_date=discovery_end_date)
    stats=equity_metrics([initial_cash]+equity.equity.tolist(),initial_cash=initial_cash) if len(equity)>1 else None
    actions=[]
    if price_adjustment_type=='unadjusted_with_actions':
        for row in frame[['date','symbol','Stock Splits','Dividends']].itertuples(index=False,name=None):
            dt,sym,split,dividend=row
            if float(split)>0:actions.append((str(dt.date()),sym,'split',float(split)))
            if float(dividend)>0:actions.append((str(dt.date()),sym,'dividend',float(dividend)))
    completed,open_lots=realized_trades(list(trades.itertuples(index=False,name=None)),actions,cost_bps=10)
    net_ev=trade_net_ev([x['net_pnl'] for x in completed]) if completed else None
    return {'equity':equity,'trades':trades,'stats':stats,'executed_buys':int((trades.side=='buy').sum()) if not trades.empty else 0,
            'completed_trades':completed,'open_lots':open_lots,'net_ev_dollars_per_completed_trade':net_ev,
            'limitations':['corporate action and earnings source validation required']}
