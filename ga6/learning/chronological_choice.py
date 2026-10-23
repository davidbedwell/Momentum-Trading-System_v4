"""Fail-closed decision-day shadow ranking adapter.

Does not assert shared-capital execution. An adapter cannot turn independent
shadow fills into a valid shared-cash replay.
"""

def choose_chromosome(score_snapshot, candidates, *, fallback=None):
    """Choose among *currently eligible* candidates, not historical winners.

    No score from a future day or a different decision date may be supplied.
    Candidate records must contain chromosome, decision_date, evidence_cutoff.
    """
    day=score_snapshot["decision_date"]
    eligible=[]
    for candidate in candidates:
        if candidate["decision_date"]!=day:
            raise ValueError("candidate/score date mismatch")
        if candidate["evidence_cutoff"]>day:
            raise ValueError("future candidate evidence")
        if str(candidate["chromosome"]) in score_snapshot["scores"]:
            eligible.append(candidate)
    if eligible:
        chosen=max(eligible,key=lambda c:(
            score_snapshot["scores"][str(c["chromosome"])]["score"],
            -int(c["chromosome"]) if str(c["chromosome"]).isdigit() else 0))
        return dict(selected=chosen,reason="PAST_ONLY_MATURED_SCORE",
                    eligible_count=len(eligible),
                    status="PROPOSAL_ONLY_NOT_EXECUTED")
    if fallback is not None:
        for candidate in candidates:
            if str(candidate["chromosome"])==str(fallback):
                return dict(selected=candidate,reason="EXPLICIT_COLD_START_FALLBACK",
                            eligible_count=0,status="PROPOSAL_ONLY_NOT_EXECUTED")
    return dict(selected=None,reason="NO_MATURED_ELIGIBLE_CANDIDATE",
                eligible_count=0,status="PROPOSAL_ONLY_NOT_EXECUTED")
