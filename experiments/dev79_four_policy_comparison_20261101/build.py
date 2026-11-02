from pathlib import Path
import shutil
p=Path(__file__).resolve().parent
src=p.parent/'dev79_minimal_manager_20261101'
shutil.copyfile(src/'trade_accounting.py',p/'trade_accounting.py')
s=(src/'manager.py').read_text()
s=s.replace('def targets(mode,','def original_targets(mode,',1)
s=s.replace("if delta>0 and mode!='buy_hold':", "if delta>0 and mode!='buy_hold':")
s=s.replace("equity=sum(q*openmarks[x] for x,q in book.q.items())\n                delta=min(delta,max(0.,.10*open_nav-book.q.get(t,0.)*ops[t])/ops[t],max(0.,.90*open_nav-equity)/ops[t])", "equity=sum(q*openmarks[x] for x,q in book.q.items())\n                name_cap=.10 if mode in ('manager','claude_approx') else 1.\n                gross_cap={'manager':.90,'claude_approx':.70,'gemini_approx':1.,'grok_dev79_approx':.98}.get(mode,.90)\n                delta=min(delta,max(0.,name_cap*open_nav-book.q.get(t,0.)*ops[t])/ops[t],max(0.,gross_cap*open_nav-equity)/ops[t])")
s=s.replace("ts=list(d.close.columns);dates=", "f['_state']={};ts=list(d.close.columns);dates=")
s=s.replace("max(25.,.005*nav))", "(max(25.,.005*nav) if mode=='manager' else .01))")
s=s.replace("f=features(d);f['close']=d.close", "f=features(d);f.update(policy_features(d));f['close']=d.close")
s=s.replace("['manager','buy_hold','momentum']", "['manager','claude_approx','gemini_approx','grok_dev79_approx']")
s=s.replace("unrealized_pnl=unreal,reconciliation_error=err", "unrealized_pnl=unreal,reconciliation_error=err,cumulative_fees=book.fees")
# Keep imported provenance, adding experiment-specific metadata in reporting step.
extra='''
def policy_features(d):
    c=d.close; prev=c.shift(1)
    tr=np.maximum(d.high-d.low,np.maximum((d.high-prev).abs(),(d.low-prev).abs()))
    return {'mom126':c/c.shift(126)-1,'sma200':c.rolling(200,min_periods=200).mean(),
            'sma20':c.rolling(20,min_periods=20).mean(),'sma50':c.rolling(50,min_periods=50).mean(),
            'atr14':tr.rolling(14,min_periods=14).mean()}

def targets(mode,i,date,f,ts,held,seen,nav,peak):
    if mode in ('manager','buy_hold','momentum'):return original_targets(mode,i,date,f,ts,held,seen,nav,peak)
    state=f['_state']; c=f['close'].loc[date]
    if mode=='grok_dev79_approx':
        month=(date.year,date.month)
        if state.get('month')==month:return None,'hold_between_monthly_rebalances'
        state['month']=month
        # All 79 retain identical allocations; unavailable listings leave their slot in cash.
        return {t:nav*.98/len(ts) for t in ts if pd.notna(c[t])},'first_session_close_monthly_98pct_all79_equal_weight_adaptation'
    if mode=='gemini_approx':
        eligible=(f['sma20'].loc[date]>f['sma50'].loc[date])&c.notna()
        chosen=list(eligible[eligible].index)
        return {t:nav/len(chosen) for t in chosen},'daily_equal_weight_active_SMA20_gt_SMA50_sell_first_Tplus1_cash'
    # Explicit reconstruction: 14-session simple ATR, 2 ATR close trailing stop;
    # 15% drawdown liquidates, pauses 20 decision sessions, then resets risk anchor.
    if i<state.get('resume',-1):return {},'drawdown_halt_20_sessions'
    if state.get('resume')==i:
        state['risk_peak']=nav
    state['risk_peak']=max(state.get('risk_peak',INITIAL),nav)
    dd=1-nav/state['risk_peak']
    if dd>=.15:
        state['resume']=i+20;state['stops']={}
        return {},'drawdown_15pct_liquidate_and_halt20'
    stops=state.setdefault('stops',{});blocked=set()
    for t in list(stops):
        if t not in held:del stops[t]
    for t in held:
        atr=f['atr14'].at[date,t]
        if pd.notna(c[t]) and pd.notna(atr):
            old=stops.get(t,-float('inf'))
            if c[t]<=old:blocked.add(t)
            else:stops[t]=max(old,c[t]-2*atr)
    m=f['mom126'].loc[date];atr=f['atr14'].loc[date]
    eligible=(m>0)&(c>f['sma200'].loc[date])&(atr>0)&c.notna()
    eligible.loc[list(blocked)]=False
    chosen=list(m[eligible].sort_values(ascending=False,kind='stable').head(10).index)
    weights={t:min(.10,.02/(2*atr[t]/c[t])) for t in chosen}
    total=sum(weights.values());scale=min(1.,.70/total) if total else 1.
    for t in chosen:
        if t not in stops:stops[t]=c[t]-2*atr[t]
    return {t:nav*w*scale for t,w in weights.items()},f'top10_mom126_trend200_2ATR14_risk2pct_gross70pct_dd={dd:.8f};stopped={sorted(blocked)}'

'''
s=s.replace('def main():',extra+'def main():')
(p/'comparison.py').write_text(s)
# Copy input audit, pointing it at isolated module/output.
s=(src/'audit_inputs.py').read_text().replace('from manager import','from comparison import')
(p/'audit_inputs.py').write_text(s)
