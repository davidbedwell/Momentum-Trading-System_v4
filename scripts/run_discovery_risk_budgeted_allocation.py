#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,metrics,SPLIT
from run_discovery_portfolio_allocation_architecture import causal_score,same_day_rank,grouped,boot,match_equal_exposure

def simulate_budget(dates,E,X,U,W,base,gross_ceiling=None,heat_threshold=None):
    eo,ei=E; xo,xi=X; uo,ui,uf=U; n,P=W.shape
    cash=np.ones(P); val=np.zeros((n,P)); wealth=[]; gross=[]; cashfrac=[]; binds=np.zeros(P,int); active=np.zeros(P,int)
    for d in range(len(dates)):
        prev_eq=cash+val.sum(axis=0); inds=ei[eo[d]:eo[d+1]]
        if len(inds):
            req=base*prev_eq[None,:]*W[inds,:]
            if heat_threshold is not None:
                heat=np.minimum(1.0,heat_threshold/np.maximum(active+len(inds),1))
                # preserve 1x base; damp only redistribution away from 1x
                req0=base*prev_eq[None,:]
                req=req0+(req-req0)*heat[None,:]
                binds += (heat<.999999)
            if gross_ceiling is not None:
                cur=val.sum(axis=0); room=np.maximum(0.0,gross_ceiling*prev_eq-cur); tot=req.sum(axis=0)
                sc=np.minimum(1.0,np.divide(room,tot,out=np.ones_like(room),where=tot>0)); req*=sc[None,:]; binds+=(sc<.999999)
            tot=req.sum(axis=0); sc=np.minimum(1.0,np.divide(cash,tot,out=np.ones_like(cash),where=tot>0)); req*=sc[None,:]
            val[inds,:]=req; cash-=req.sum(axis=0); active+=len(inds)
        us=ui[uo[d]:uo[d+1]]; fac=uf[uo[d]:uo[d+1]]
        if len(us): val[us,:]*=fac[:,None]
        outs=xi[xo[d]:xo[d+1]]
        if len(outs): cash+=val[outs,:].sum(axis=0); val[outs,:]=0.0; active-=len(outs)
        eq=cash+val.sum(axis=0); wealth.append(eq.copy()); gross.append(np.divide(val.sum(axis=0),eq,out=np.zeros(P),where=eq!=0)); cashfrac.append(np.divide(cash,eq,out=np.zeros(P),where=eq!=0))
    return np.asarray(wealth),np.asarray(gross),np.asarray(cashfrac),binds/len(dates)

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest); rows=[r for r in z['rows'] if r['signal_date']<SPLIT]
    score,src=causal_score(rows); dates,E,X,U,lens,ass=build_events(rows); n=len(rows)
    # derive risk anchors only from equal-sizing Development path
    W0=np.ones((n,1)); w0,g0,c0,_=simulate_budget(dates,E,X,U,W0,ass['base_trade_fraction'])
    base=metrics(dates,w0[:,0],g0[:,0],c0[:,0]); gross_p90=float(np.quantile(g0[:,0],.90))
    # concurrency anchors from event schedule, independent of outcomes
    eo,ei=E; xo,xi=X; active=0; conc=[]
    for d in range(len(dates)):
        active+=int(eo[d+1]-eo[d]); conc.append(active); active-=int(xo[d+1]-xo[d])
    pos=[x for x in conc if x>0]; heat_med=float(np.median(pos)); heat_p90=float(np.quantile(pos,.90))
    gross_anchors=[('avg',base['avg_gross_exposure']),('p90',gross_p90),('peak',base['peak_gross_exposure'])]
    heat_anchors=[('median',heat_med),('p90',heat_p90)]
    specs=[]
    for q in (.25,.50):
      for cap in (1.10,1.25,1.50):
        raw=same_day_rank(rows,score,q,cap,True)
        for gn,gc in gross_anchors: specs.append((f'budget_top{int(q*100)}_c{cap:.2f}_gross_{gn}',raw,gc,None,'gross'))
        for hn,hc in heat_anchors: specs.append((f'budget_top{int(q*100)}_c{cap:.2f}_heat_{hn}',raw,None,hc,'heat'))
        for gn,gc in gross_anchors[:2]:
          for hn,hc in heat_anchors: specs.append((f'budget_top{int(q*100)}_c{cap:.2f}_gross_{gn}_heat_{hn}',raw,gc,hc,'combined'))
    out=[]
    ret=np.asarray([r['ret'] for r in rows])
    for name,Wv,gc,hc,fam in specs:
        wa,ga,ca,bind=simulate_budget(dates,E,X,U,Wv[:,None],ass['base_trade_fraction'],gc,hc)
        pm=metrics(dates,wa[:,0],ga[:,0],ca[:,0]); embase,em=match_equal_exposure(dates,E,X,U,n,pm['avg_gross_exposure'])
        # actual scheduled multiplier contribution remains ranking diagnostic
        d=ret*(Wv-1.0); gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}; ci=boot(rows,d)
        gate={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),'year60':bool(gs['year']['fraction']>=.60),'family60':bool(gs['family']['fraction']>=.60),'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),'cluster_ci_positive':bool(ci[0]>0),'wealth_gt_equal':bool(pm['terminal_wealth']>base['terminal_wealth']),'not_both_tail_worse':bool(not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05']))}
        out.append({'name':name,'risk_family':fam,'gross_ceiling':gc,'heat_threshold':hc,'binding_day_fraction':float(bind[0]),'mean_delta_scheduled':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,'portfolio':pm,'exposure_matched_equal':{'base_trade_fraction':embase,'metrics':em},'wealth_vs_equal_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),'wealth_vs_exposure_matched_rel':float(pm['terminal_wealth']/em['terminal_wealth']-1),'gate':gate,'pre_neighborhood_pass':all(gate.values())})
    for x in out:
        prefix=x['name'].split('_gross_')[0].split('_heat_')[0]
        x['passing_architecture_neighbors']=sum(y['pre_neighborhood_pass'] for y in out if y['name'].startswith(prefix.rsplit('_c',1)[0]))
        x['nominee']=bool(x['pre_neighborhood_pass'] and x['passing_architecture_neighbors']>=2)
    res={'stage':'RISK_BUDGETED_ALLOCATION_DEVELOPMENT','protocol_sha256':sha(a.protocol),'population':{'development':n,'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},'risk_anchors':{'gross_avg':base['avg_gross_exposure'],'gross_p90':gross_p90,'gross_peak':base['peak_gross_exposure'],'heat_median':heat_med,'heat_p90':heat_p90},'baseline':base,'candidate_count':len(out),'nominee_count':sum(x['nominee'] for x in out),'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('ANCHORS',res['risk_anchors']); print('CANDIDATES',len(out),'NOMINEES',res['nominee_count'])
    for x in sorted(out,key=lambda q:q['portfolio']['terminal_wealth'],reverse=True)[:25]:
        p=x['portfolio']; print(x['name'],'wealth',round(p['terminal_wealth'],6),'rel%',round(100*x['wealth_vs_equal_rel'],3),'em%',round(100*x['wealth_vs_exposure_matched_rel'],3),'DD',round(p['max_drawdown'],5),'CV',round(p['daily_cvar05'],5),'bind',round(x['binding_day_fraction'],3),'pass',x['pre_neighborhood_pass'],'nom',x['nominee'])
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
