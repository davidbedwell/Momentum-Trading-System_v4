"""Convert authentic GA7 research proposals to bounded Competitive GA requests.

A proposal is not a trade. This adapter does not certify the producer's PIT inputs.
"""
from .native_signal_contract import NativeProposal

def from_ga7(proposal, *, decision_date, trained_through, source_hash, snapshot_hash):
    proposal.validate()
    if proposal.action=="PASS":
        return None
    action={"ENTER":"ENTER","INCREASE":"ADD","HOLD":"HOLD","REDUCE":"REDUCE","EXIT":"EXIT"}[proposal.action]
    target=min(.30,proposal.requested_weight)
    if action=="EXIT":target=0.
    # GA7 proposal.expected_net_return is a net-return fraction, NOT its archived EV_R.
    # Never claim this is R-multiple. Native score contract requires explicit units.
    return NativeProposal(
        decision_date=decision_date,ticker=proposal.ticker,family="GA7",
        chromosome_id=proposal.chromosome_id,action=action,target_weight=target,
        native_score=float(proposal.expected_net_return),
        native_score_unit="net_return_fraction",
        source_manifest_hash=source_hash,feature_snapshot_hash=snapshot_hash,
        model_trained_through=trained_through)
