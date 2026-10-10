#!/usr/bin/env python3
"""Frozen review cadence for both evolutionary studies; no live-run mutation."""
from dataclasses import dataclass
@dataclass(frozen=True)
class ReviewPolicy:
    journal_every:int=1
    economic_review_every:int=25
    scientific_review_every:int=100
    major_review_generation:int=200
    plateau_window:int=100
    minimum_generations:int=100
    confidence_level:float=.95
    minimum_effective_n:int=30
    def __post_init__(self):
        assert self.journal_every==1
        assert self.economic_review_every>0
        assert self.scientific_review_every%self.economic_review_every==0
        assert self.major_review_generation%self.scientific_review_every==0
        assert self.plateau_window>=self.economic_review_every
        assert .5<self.confidence_level<1
    def milestones(self,generation):
        assert generation>=1
        return {"durable_checkpoint":True,
                "economic_review":generation%self.economic_review_every==0,
                "scientific_review":generation%self.scientific_review_every==0,
                "major_review":generation%self.major_review_generation==0}
    def stop_decision(self,generation,reviews):
        """Stop only on sustained lack of *credible* economic progress.
        Review entries: generation, credible_improvement, confidence_audited,
        risk_audited, multiplicity_audited. Missing evidence fails open for research
        continuation, never falsely certifies a plateau.
        """
        if generation<self.minimum_generations:return False
        start=generation-self.plateau_window
        window=[r for r in reviews if start<r["generation"]<=generation]
        expected=list(range(start+self.economic_review_every,generation+1,self.economic_review_every))
        if [r["generation"] for r in window]!=expected:return False
        return all(r.get("confidence_audited") is True and
                   r.get("risk_audited") is True and
                   r.get("multiplicity_audited") is True and
                   r.get("credible_improvement") is False for r in window)
POLICY=ReviewPolicy()
