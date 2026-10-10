#!/usr/bin/env python3
"""Adaptive economic plateau policy for future MTS evolutionary controllers.

This module does not modify a running GA. The controller must journal the
underlying statistical/risk/multiplicity evidence, not just booleans.
"""
from dataclasses import dataclass
@dataclass(frozen=True)
class ReviewPolicy:
    journal_every:int=1
    economic_review_every:int=25
    scientific_review_every:int=100
    major_review_generation:int=200
    standard_patience:int=50
    exceptional_patience:int=75
    confidence_level:float=.95
    minimum_effective_n:int=30
    def __post_init__(self):
        assert self.journal_every==1
        assert self.economic_review_every==25
        assert self.scientific_review_every%self.economic_review_every==0
        assert self.major_review_generation%self.scientific_review_every==0
        assert 0<self.standard_patience<self.exceptional_patience
        assert .5<self.confidence_level<1
    def milestones(self,generation):
        assert generation>=1
        return {"durable_checkpoint":True,
                "economic_review":generation%self.economic_review_every==0,
                "scientific_review":generation%self.scientific_review_every==0,
                "major_review":generation%self.major_review_generation==0}
    def decide(self,generation,last_credible_generation,reviews):
        """Return CONTINUE, STOP_PLATEAU, or REVIEW_REQUIRED (fail closed).

        A review at the current generation must contain auditable confidence,
        downside-risk, and multiplicity checks. Only a separately evidenced
        novel, promising-but-inconclusive frontier can justify 75 vs 50.
        Neither raw EV nor genetic novelty resets credible-improvement age.
        """
        assert generation>=1 and 0<=last_credible_generation<=generation
        stagnant=generation-last_credible_generation
        if stagnant<self.standard_patience:return "CONTINUE"
        if generation%self.economic_review_every:return "CONTINUE"
        current=[r for r in reviews if r.get("generation")==generation]
        if len(current)!=1:return "REVIEW_REQUIRED"
        r=current[0]
        if not all(r.get(k) is True for k in ("confidence_audited","risk_audited","multiplicity_audited","archive_audited")):
            return "REVIEW_REQUIRED"
        if r.get("credible_improvement") is True:return "REVIEW_REQUIRED"
        if r.get("credible_improvement") is not False:return "REVIEW_REQUIRED"
        if stagnant>=self.exceptional_patience:return "STOP_PLATEAU"
        if r.get("promising_inconclusive") is True and r.get("novel_nonredundant") is True:
            return "CONTINUE"
        if r.get("promising_inconclusive") is False:return "STOP_PLATEAU"
        return "REVIEW_REQUIRED"
    def stop_decision(self,generation,last_credible_generation,reviews):
        return self.decide(generation,last_credible_generation,reviews)=="STOP_PLATEAU"
POLICY=ReviewPolicy()
