"""Independent iteration6; inherited DGP, classifier and horizon accounting."""
import copy,csv,gzip,hashlib,importlib.util,json,math,random,secrets,statistics as st,time
from pathlib import Path
O=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('iteration5_reference',O.parent/'discrimination_iteration5/experiment.py')
e=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(e)
START=e.START;END=e.END;COST=e.COST;mean=e.mean

def generate(seed,scenario,change=None):
    # Identical RNG, noise, prices, sensor noise and class law. Only switch time varies.
    p,f,t=e.generate(seed,'learnable' if scenario=='random_reversal' else scenario)
    if scenario=='random_reversal':
        for i in range(change,e.N):f[i]=[4-c for c in f[i]]
    return p,f,t

class Gate:
    """PIT safety latch; no truth, switch time, seed or scenario is supplied."""
    def __init__(self,p,f,models):
        self.p=p;self.f=f;self.models=models;self.latched=False;self.events=[];self.trace=[]
    def contrast(self,d):
        groups=[]
        for c in [0,4]:
            vals=[e.observed(self.p,d,j)-self.models[c]['mean'] for j in range(24) if self.f[d][j]==c]
            if len(vals)<2:return None
            groups.append(mean(vals))
        return groups[1]-groups[0]
    def __call__(self,now,row,trades):
        # All scan endpoints require signal+3 <= now; no scheduled-change indicator.
        signals=[]
        for w in [2,4,8]:
            ds=list(range(now-2-w,now-2))
            contrasts=[self.contrast(d) for d in ds]
            if all(v is not None for v in contrasts):
                value=-mean(contrasts)
                # Conservative fixed date-contrast envelope, max126*3 looks.
                threshold=.014*math.sqrt(2*math.log(2*126*3/.01)/w)
                if value>threshold:signals.append(dict(channel='CROSS_SECTIONAL_RESIDUAL',window=w,value=value,threshold=threshold))
        # Actual funded fills only, grouped by signal date to avoid pseudo replication.
        mature=[t for t in trades if t['signal']+3<=now and t['signal']>=now-10]
        errors=[]
        for d in sorted(set(t['signal'] for t in mature)):
            ts=[t for t in mature if t['signal']==d]
            errors.append(sum(t['debit']*(t['net']-self.models[self.f[d][t['j']]]['mean']) for t in ts)/sum(t['debit'] for t in ts))
        if len(errors)>=3:
            threshold=.018*math.sqrt(2*math.log(2*126/.01)/len(errors))
            if -mean(errors)>threshold:signals.append(dict(channel='MATURED_FUNDED_SURPRISE',window=len(errors),value=-mean(errors),threshold=threshold))
        if signals and not self.latched:
            self.events.append(dict(index=now,last_signal=now-3,evidence=signals));self.latched=True
        self.trace.append(dict(index=now,matured_fills=len(mature),funded_error=mean(errors) if errors else None,alarm=bool(signals),latched=self.latched))
        # Full abstention is conservative under detected drift. Recovery needs new disjoint evidence,
        # not a countdown or fitted reversal sign; no automatic re-entry in this bounded horizon.
        if self.latched:return [dict(z,label='UNKNOWN',reason='RAPID_DRIFT_ABSTAIN') for z in row]
        return row

def replay(prices,states,policy='tier',scale=1.,gate=None):
    cash=100000.;nav=cash;peak=nav;mdd=0.;costs=0.;risks=[];trades=[];daily=[];gap_exceed=0
    # All trades hold exactly one open-to-open session. Prior sales settle one session later.
    receivable=0.;positions=[]
    for k,i in enumerate(range(START,END)):
        opening=nav;cash+=receivable;receivable=0.;pnl=0.;exit_value=0.
        for t in positions:
            exitp=prices[i+1][t['j']]; proceeds=t['shares']*exitp*(1-COST/2)
            exit_value+=proceeds;costs+=t['shares']*exitp*COST/2
            t.update(exit_index=i+1,exit_open=exitp,net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav'])
            gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        receivable=exit_value;positions=[]
        opening=cash+receivable
        available=cash
        if gate is not None: states[k]=gate(i,states[k],trades)
        order=sorted(range(24),key=lambda j:states[k][j]['mean'],reverse=True)
        for j in order:
            c=states[k][j]
            if policy=='cash' or (policy=='tier' and c['label'] not in ('GOOD','GREAT')):continue
            gap=[.03,.06,.12,.24][j%4];weight=min(.10*scale,.02/(gap+COST)); debit=min(available,opening*weight)
            if debit<=1e-8:continue
            entry=prices[i+1][j];shares=debit/(entry*(1+COST/2));risk=shares*entry/opening*(gap+COST)
            assert risk<=.02+1e-12
            costs+=shares*entry*COST/2;available-=debit
            positions.append(dict(signal=i,j=j,entry_index=i+1,entry_open=entry,shares=shares,debit=debit,entry_nav=opening,modeled_risk=risk,tier=c['label']))
        cash=available;nav=cash+receivable+sum(t['shares']*prices[i+1][t['j']] for t in positions)
        assert cash>=-1e-8
        peak=max(peak,nav);mdd=max(mdd,1-nav/peak);daily.append(dict(index=i,nav=nav,cash=cash,receivable=receivable,exposure=sum(t['shares']*prices[i+1][t['j']] for t in positions)/nav))
    # Explicit final horizon liquidation; settle for ending NAV.
    for t in positions:
        proceeds=t['shares']*prices[END+1][t['j']]*(1-COST/2);costs+=t['shares']*prices[END+1][t['j']]*COST/2
        t.update(exit_index=END+1,exit_open=prices[END+1][t['j']],net=proceeds/t['debit']-1,realized_loss_nav=max(0,t['debit']-proceeds)/t['entry_nav']);gap_exceed+=t['realized_loss_nav']>t['modeled_risk']+1e-12;trades.append(t)
        cash+=proceeds
    nav=cash+receivable;peak=max(peak,nav);mdd=max(mdd,1-nav/peak)
    return dict(total_return=nav/100000-1,cagr=(nav/100000)**(252/126)-1,mdd=mdd,costs=costs,final_nav=nav,max_modeled_risk=max((t['modeled_risk'] for t in trades),default=0),gap_loss_exceedances=gap_exceed,max_realized_trade_loss_nav=max((t['realized_loss_nav'] for t in trades),default=0),trades=len(trades),mean_exposure=mean([d['exposure'] for d in daily])),trades,daily
