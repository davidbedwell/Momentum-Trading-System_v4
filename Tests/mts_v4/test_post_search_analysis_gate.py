from scripts.analyze_saved_search_candidates import _evaluate
from MTS_V4.search_candidate_analysis import _compile_signal


def test_nonoverlap_gate_reduces_clustered_signal_days():
    predictors=[]; outcomes=[]
    for i in range(12):
        date=f"d{i:02d}"
        predictors.append({"security_id":"S1","effective_date":date,"return_20__v1":float(i)})
        outcomes.append({"security_id":"S1","effective_date":date,"forward_return_5__v1":0.10})
    candidate={"candidate_id":"c","family_id":"MOMENTUM","genome":{
        "momentum_feature":"return_20__v1","direction":"ABOVE","threshold_quantile":0.0,
        "context_feature":"NONE","context_threshold":0.5,"forward_horizon":5,
    }}
    result=_evaluate(candidate,predictors,outcomes)
    assert result["raw_signal_day_statistics"]["count"] == 12
    assert result["non_overlapping_opportunity_statistics"]["count"] == 3
    assert result["trade_policy"]["stop_loss"].startswith("UNAVAILABLE")
    assert result["ev"]["cost_adjusted_ev"].startswith("UNAVAILABLE")


def test_volatility_price_context_is_an_actual_filter():
    predictors=[]
    for i in range(10):
        predictors.append({
            "realized_vol_63__v1":float(i),
            "close_to_sma_50__v1":float(i),
        })
    base={"family_id":"VOLATILITY","genome":{
        "volatility_feature":"realized_vol_63__v1","state":"HIGH","threshold_quantile":0.5,
        "price_context":"NONE","forward_horizon":5,
    }}
    filtered={"family_id":"VOLATILITY","genome":dict(base["genome"],price_context="close_to_sma_50__v1")}
    a=_compile_signal(predictors,base)
    b=_compile_signal(predictors,filtered)
    assert sum(a) > 0
    assert sum(b) > 0
    assert sum(b) <= sum(a)


def test_volatility_low_state_uses_lower_tail():
    predictors=[{"realized_vol_63__v1":float(i)} for i in range(10)]
    candidate={"family_id":"VOLATILITY","genome":{
        "volatility_feature":"realized_vol_63__v1","state":"LOW","threshold_quantile":0.8,
        "price_context":"NONE","forward_horizon":5,
    }}
    signal=_compile_signal(predictors,candidate)
    assert signal[0] is True
    assert signal[-1] is False
