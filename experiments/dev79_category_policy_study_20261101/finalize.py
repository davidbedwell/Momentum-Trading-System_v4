import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
import json,hashlib
from pathlib import Path
import pandas as pd
from study import ROOT,OUT,MODES

def table(df):
    def fmt(x):
        if isinstance(x,float):return f'{x:.4f}'
        return str(x).replace('|','/')
    lines=['| '+' | '.join(map(str,df.columns))+' |','| '+' | '.join(['---']*len(df.columns))+' |']
    lines.extend('| '+' | '.join(fmt(x) for x in row)+' |' for row in df.itertuples(index=False,name=None))
    return '\n'.join(lines)

def main():
    summ=pd.read_csv(OUT/'category_summary.csv');contrast=pd.read_csv(OUT/'matched_contrasts.csv');support=pd.read_csv(OUT/'support.csv');audit=json.loads((OUT/'study_audit.json').read_text());metrics=json.loads((OUT/'metrics.json').read_text())
    lines=['# DEV79 category-conditioned management — measured Phase 1',
    'Completed one real-OHLCV replay of the existing four policies. No selector fitted, no policy switching, no production changes. Claude, Gemini and Grok DEV79 implementations are approximations; exact Claude/Grok source was unavailable. State rules, split, horizon, benchmark and uncertainty procedure were frozen in [PROTOCOL.md](PROTOCOL.md) before execution.',
    '## Interpretation',
    'No category policy winner is established. Same-date/ticker matching removes different opportunity sets, but inventory, sizing, cash, turnover and earlier decisions remain policy-dependent. The primary result is a local one-session incremental management contribution versus holding the pre-execution inventory. It is not a counterfactual full portfolio, a category NAV, a long-horizon realized alpha estimate or a causal treatment effect. Realized sell PnL is reported separately and includes cost basis from previous states. Portfolio-level results below are replay parity context, not category evidence.',
    '## Actual replay context',table(pd.DataFrame([dict(policy=m,final_nav=metrics[m]['final_nav'],return_pct=100*metrics[m]['total_return'],mean_exposure_pct=100*metrics[m]['mean_exposure'],fees=metrics[m]['fees'],fills=metrics[m]['fills']) for m in MODES])),
    '## State and matched coverage',
    'Categories at decision close t use only data through t-1. Priority is reversal, deterioration, acceleration, uptrend, then residual consolidation; unknown requires more history. Exact formulas are in the protocol. Consolidation is deliberately an exhaustive residual, not solely a low-volatility range. No verified sector time series/membership was established: relative strength uses the local SPY close archive. SPY is price-only and was checked for unique dates, positive closes and session coverage; it is not independently vendor-certified.',table(support),
    f"SPY missing on replay sessions: {audit['spy_missing_on_dev_sessions']}. Each policy has {audit['coverage'][0]['all']:,} date/ticker opportunities; {audit['coverage'][0]['matched']:,} meet the common horizon/price/split rules. Missing/listing and boundary/terminal outcomes remain excluded, never filled with synthetic prices. All unknown categories remain separately recorded.",
    '## Category management measurements',
    'Exposure columns are mean contributions to total portfolio NAV over all segment days. Incremental dollars are the sum of actual-sized one-session action outcomes net of fees/slippage against unchanged pre-execution shares; they are not terminal wealth. Fees and realized PnL include every actual fill attributed by its signal category, including fills lacking a complete forward horizon. Action counts are actual filled entry/add/reduce/exit counts, distinguished from intentions in the CSV. Price returns exclude dividends.',
    table(summ[['segment','category','policy','matched_opportunities','mean_pre_exposure','mean_post_exposure','incremental_pnl','realized_pnl_all_fills','fees_all_fills','filled_enter','filled_add','filled_reduce','filled_exit']]),
    '## Matched contrasts and uncertainty',
    'Each effect is policy a minus b in basis points of NAV per calendar decision day: sum the paired ticker contributions in that category, include zero category-absent days, then average. Thus it combines actual sizing and opportunity frequency; it is not per-trade return. Calendar-month block bootstrap, seed 79, 2,000 draws, preserves contemporaneous stock dependence. 95% and family-adjusted 99.8333% intervals are descriptive, conditional on this archive and policy paths. Monte Carlo tail resolution is limited with 2,000 draws; no exact significance claim. Family adjustment covers 30 comparisons per segment for the five defined states; unknown is diagnostic.',
    table(contrast[contrast.category!='unknown'][['segment','category','a','b','discordant_actions','discordant_months','mean_daily_bps','ci95_low_bps','ci95_high_bps','family_low_bps','family_high_bps','status']]),
    'Insufficient support means fewer than 100 discordant executed-direction opportunities or 24 discordant calendar months. Other rows remain descriptive and path-confounded even when an interval excludes zero. All-four-flat and all-four-held matched support is in matched_contrasts.csv; empty or small strata cannot identify the relative quality of an entry or exit rule. No category selector is warranted by these diagnostics alone, and none was preregistered or run.',
    '## Chronology, limitations and audit',
    'Discovery is 2009–2017; later descriptive test is 2018–2026-09-14, with horizons crossing the split embargoed. No state thresholds or policies were tuned on test. Prior work examined these policies and history, so this later period is not an untouched prospective holdout for policy discovery. No claim of independent OOS alpha.',
    'DEV79 is a retrospective fixed-survivor archive, not point-in-time membership. Historical revisions and present-day split adjustment may restate earlier prices; no independent vendor receipts/as-of publication timestamps. Split-adjusted price treatment inherits the prior audit, no double share adjustment. No dividends, merger/delisting cashflow reconstruction, taxes, market impact calibration or historical settlement schedule. Missing opens cancel orders, stale closes are valuation-only. One-session outcomes omit subsequent management, cash opportunity yield and subsequent liquidation costs. Next-open admission caps, sell-first alphabetical processing and T+1 settlement are inherited unchanged. Full rules/limitations are in artifacts/provenance.json and the original four-policy report.',
    'Verification: copied replay tests, category prefix/future and same-decision-bar mutation tests, missing-history test, all-four common matching, hold identity, fill/fee/realized-PnL reconciliation, and exact original daily/fill/decision parity. See tests.log. All replay/analysis execution is pinned to one CPU and numerical threads to one, with a 1,150-second command ceiling.',
    'Reproduce: `bash experiments/dev79_category_policy_study_20261101/run.sh`. Full pre-decision features/states in artifacts/state_opportunities.csv.gz; per-policy opportunity and fill attribution ledgers; original execution/decision/position/NAV ledgers; category_summary.csv; matched_contrasts.csv; paired_daily.csv.gz; support.csv; study_audit.json. checksums.json hashes all run inputs/code/results except itself and runtime log. Runtime resource records are runtime.log and supplemental_runtime.log (inventory strata only). No network, GA, monitoring or external review used. Resource deviation: the first six-second supplemental inventory-stratum pass initialized numerical libraries before setting CPU affinity (112% CPU in supplemental_runtime_initial.log). It was rerun with affinity/thread limits set before numerical imports; the core replay/analysis/tests were always taskset-pinned to one CPU. The initial resource log is retained for audit.'
    ]
    measured=summ[summ.segment=='test'].groupby('policy',sort=False).agg(local_incremental_dollars=('incremental_pnl','sum'),fees_all_fills=('fees_all_fills','sum')).reset_index()
    later=contrast[(contrast.segment=='test')&(contrast.category!='unknown')]
    surviving=later[(later.family_low_bps>0)|(later.family_high_bps<0)]
    lines[4:4]=['## Main measured findings',
        'Matched coverage is 329,927 / 351,629 opportunities per policy (93.83%). Later-segment local incremental dollars against hold are below. These sums use each historical portfolio’s actual size, so their dollar levels are not directly comparable policy skill estimates. All four are negative at this one-session horizon; this does not imply all trades were harmful over their full holding periods.',table(measured),
        f'Of 30 later-segment known-state pair contrasts, {len(surviving)} has a family-adjusted interval excluding zero: Gemini approximation minus Grok DEV79 approximation in consolidation, -0.5069 basis points of NAV per decision day, interval [-1.8673, -0.0231]. This remains exposure/turnover/path-confounded and does not establish a category winner. All six later uptrend family-adjusted intervals include zero. Discovery differences therefore do not justify an uptrend selector.',
        'Later-segment common all-four-flat known-state opportunities: zero. All-four-held support in deterioration is one opportunity and reversal is 42. These cannot identify an entry/exit winner. There is no category selector or retrospective switching.']
    (ROOT/'REPORT.md').write_text('\n\n'.join(lines)+'\n')
    (ROOT/'README.md').write_text('See [REPORT.md](REPORT.md) for executed measurements and [PROTOCOL.md](PROTOCOL.md) for frozen definitions. Phase 1 only; no selector.\n')
    strata=pd.read_csv(OUT/'inventory_stratum_contrasts.csv') if (OUT/'inventory_stratum_contrasts.csv').exists() else None
    if strata is not None:
        roll=strata[strata.category!='unknown'].groupby(['segment','stratum']).agg(comparisons=('status','size'),insufficient=('status',lambda x:int(x.str.startswith('inconclusive').sum())),max_matched=('matched','max'),max_discordant=('discordant_actions','max')).reset_index()
        with (ROOT/'REPORT.md').open('a') as f:
            f.write('\n## Inventory-status matched diagnostics\n\n'+table(roll)+'\n\nFull paired effects and 95% month-block intervals (2,000 draws, separate seed 7901) are in artifacts/inventory_stratum_contrasts.csv. These are exploratory support diagnostics without additional multiplicity claims; starting dollar inventory and policy history still differ. Opportunity cost against hold is explicitly the negative of incremental dollars, in artifacts/opportunity_cost_summary.csv; positive means forgone hold profit.\n')
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in str(p) and p.name not in ['checksums.json','runtime.log']}
    hashes['INPUT:'+audit['source']]=audit['source_sha256'];hashes['INPUT:'+audit['spy']]=audit['spy_sha256']
    (ROOT/'checksums.json').write_text(json.dumps(hashes,indent=2))
    print('Report and checksums complete.')
if __name__=='__main__':main()
