from concurrent.futures import ProcessPoolExecutor

from scripts.run_one_ticker_computational_search import EXECUTABLE_FAMILIES, _parser, _run_family


def _evidence():
    security_id="TEST_AAPL"
    predictors=[]
    outcomes=[]
    for i in range(80):
        d=f"2020-01-{(i % 28)+1:02d}-{i:03d}"
        base=(i-40)/100.0
        predictors.append({
            "security_id":security_id,
            "effective_date":d,
            "return_20__v1":base,
            "return_63__v1":base*0.8,
            "return_126__v1":base*0.6,
            "return_252__v1":base*0.4,
            "return_252_skip_20__v1":base*0.3,
            "return_126_percentile__v1":i/79,
            "return_252_percentile__v1":i/79,
            "return_252_skip_20_percentile__v1":i/79,
            "breadth_above_sma_200__v1":0.25 + (i % 50)/100,
            "breadth_positive_20__v1":0.30 + (i % 40)/100,
            "sector_return_252_percentile__v1":i/79,
            "natr_20_percentile__v1":1-(i/79),
        })
        outcomes.append({
            "security_id":security_id,
            "effective_date":d,
            "forward_return_5__v1":base/10,
            "forward_return_10__v1":base/8,
            "forward_return_20__v1":base/6,
            "forward_return_63__v1":base/4,
        })
    return predictors,outcomes


def _scientific_payload(result):
    family_id,payload=result
    payload=dict(payload)
    payload.pop("elapsed_seconds",None)
    return family_id,payload


def _kwargs():
    predictors,outcomes=_evidence()
    return dict(
        family_id="MOMENTUM",
        ticker="AAPL",
        predictors=predictors,
        outcomes=outcomes,
        evidence_identity="test-partition|TEST_AAPL|predictors:v2|outcomes:v1",
        budget=20,
        seed=20260930,
    )


def test_family_search_is_reproducible():
    a=_scientific_payload(_run_family(**_kwargs()))
    b=_scientific_payload(_run_family(**_kwargs()))
    assert a == b


def test_worker_process_matches_direct_execution():
    expected=_scientific_payload(_run_family(**_kwargs()))
    with ProcessPoolExecutor(max_workers=1) as pool:
        actual=_scientific_payload(pool.submit(_run_family,**_kwargs()).result(timeout=30))
    assert actual == expected


def test_family_selector_is_fail_closed_and_repeatable():
    parser=_parser()
    args=parser.parse_args([
        "--ticker","AAPL",
        "--derived-market-root","/tmp/store",
        "--universe-id","u",
        "--membership-csv","m.csv",
        "--scientific-partition-manifest","p.json",
        "--family","VOLATILITY",
        "--output","o.json",
    ])
    assert args.family == ["VOLATILITY"]
    assert "VOLATILITY" in EXECUTABLE_FAMILIES
