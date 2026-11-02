import pytest
from discovery.competitive_ga.native_four_family_orchestrator import produce
from discovery.competitive_ga.native_signal_contract import NativeProposal

DATE='2026-01-12'
def test_ga6_callback_preserves_native_provenance():
    def callback(date,held,defensive):
        return [NativeProposal(date,'AAA','GA6','native-1','ENTER',.08,.08,
            'entry_equity_fraction','source','snapshot','2026-01-11')]
    p=produce(DATE,trained_through='2026-01-11',source_hash='source',
        snapshot_hash='snapshot',ga6_producer=callback)
    assert len(p)==1 and p[0].family=='GA6'

def test_missing_required_panels_rejected():
    with pytest.raises(ValueError,match='GA4 compiler'):
        produce(DATE,trained_through='2026-01-11',source_hash='source',
            snapshot_hash='snapshot',ga4_specs=[{'id':'a','chromosomes':[(1,2)]}])
    with pytest.raises(ValueError,match='Horizons causal panel'):
        produce(DATE,trained_through='2026-01-11',source_hash='source',
            snapshot_hash='snapshot',horizons_specs=[{'id':'h','genome':object()}])
