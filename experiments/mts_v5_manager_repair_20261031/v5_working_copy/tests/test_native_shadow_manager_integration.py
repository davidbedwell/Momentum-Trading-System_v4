from discovery.competitive_ga.chronological_manager_replay import run
from discovery.competitive_ga.native_shadow_trade_book import ShadowBook
from discovery.competitive_ga.shadow_accounting_v2 import ShadowLedger
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

def test_manager_receives_only_prior_matured_shadow_trades():
    dates=[f'2026-01-{i:02d}' for i in range(2,11)]
    def native(date,session,bars,holdings,owners,defense):
        action='EXIT' if session in (2,5) else 'ENTER'
        return [NativeProposal(date,'AAA','GA6','c',action,
            0 if action=='EXIT' else .1,.1,'entry_equity_fraction',
            'source','snapshot','2026-01-01')]
    days=[(date,{'AAA':Bar(100+i*2,101+i*2)},native,[],False)
          for i,date in enumerate(dates)]
    result=run(days,min_samples=1,shadow_book=ShadowBook())
    assert result['shadow_completed']>=2
    assert result['decisions'][3]['eligible']==0
    assert result['decisions'][4]['eligible']>=1
    assert result['matured_outcomes']>=2

def test_manager_with_partial_fill_ledger():
    dates=[f'2026-02-{i:02d}' for i in range(2,11)]
    def native(date,session,bars,holdings,owners,defense):
        action='EXIT' if session in (2,5) else 'ENTER'
        return [NativeProposal(date,'AAA','GA6','c',action,
            0 if action=='EXIT' else .1,.1,'entry_equity_fraction',
            'source','snapshot','2026-02-01')]
    days=[(date,{'AAA':Bar(100+i*2,101+i*2)},native,[],False)
          for i,date in enumerate(dates)]
    result=run(days,min_samples=1,shadow_book=ShadowLedger())
    assert result['shadow_completed']>=2
    assert result['decisions'][4]['eligible']>=1
