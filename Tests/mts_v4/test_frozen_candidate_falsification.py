from MTS_V4.frozen_candidate_falsification import analyze_frozen_candidate, pairwise_candidate_overlap


def _candidate(name, dates, returns):
    return {
        "candidate_id":name,"family_id":"TEST","genome":{"forward_horizon":20},
        "paths":[{
            "signal_date":d,"entry_date":d,"exit_date":d,
            "fixed_horizon_return":r,"mae_return":min(0.0,r),"mfe_return":max(0.0,r),
            "stop_results":{},
        } for d,r in zip(dates,returns)]
    }


def test_concentration_stability_and_leave_one_out_are_deterministic():
    c=_candidate("a",["2020-01-01","2020-02-01","2020-03-01","2020-04-01"],[0.1,-0.1,0.2,0.4])
    r=analyze_frozen_candidate(c)
    assert r["trade_count"] == 4
    assert r["fixed_horizon_statistics"]["mean"] == 0.15
    assert r["winner_concentration"]["top_1_share_of_positive_returns"] == 0.4/0.7
    assert r["leave_one_out"]["available"] is True
    assert len(r["chronological_thirds"]) == 3


def test_pairwise_overlap_uses_exact_executable_entry_dates():
    a=_candidate("a",["2020-01-01","2020-02-01"],[0.1,0.2])
    b=_candidate("b",["2020-02-01","2020-03-01"],[0.2,0.3])
    row=pairwise_candidate_overlap({"A":a,"B":b})[0]
    assert row["same_entry_date_count"] == 1
    assert row["jaccard_same_entry_dates"] == 1/3
    assert row["share_of_smaller_candidate"] == 0.5
