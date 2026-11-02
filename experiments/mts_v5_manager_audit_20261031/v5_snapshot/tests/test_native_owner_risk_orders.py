from discovery.competitive_ga.native_owner_risk_orders import mandatory_orders
from discovery.competitive_ga.native_signal_contract import NativeProposal

def p(family='GA7',cid='owned',action='EXIT',weight=0):
    return NativeProposal('2020-01-03','AAA',family,cid,action,weight,0.,
        'net_return_fraction' if family=='GA7' else 'entry_equity_fraction',
        'source','snapshot','2020-01-02')

def test_uncalibrated_owner_exit_is_mandatory():
    result=mandatory_orders([p()],'2020-01-03',{'AAA':.08},{'AAA':('GA7','owned')})
    assert result['AAA'].target_weight==0

def test_foreign_chromosome_cannot_exit():
    assert not mandatory_orders([p(cid='other')],'2020-01-03',{'AAA':.08},{'AAA':('GA7','owned')})

def test_reduce_never_increases_position():
    result=mandatory_orders([p(action='REDUCE',weight=.15)],'2020-01-03',{'AAA':.08},{'AAA':('GA7','owned')})
    assert result['AAA'].target_weight==.08
