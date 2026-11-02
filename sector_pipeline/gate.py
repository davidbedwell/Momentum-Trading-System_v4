"""Fail-closed research access and pure, direction-aware stage decisions."""
import math


def authorize(years, manifest):
    if manifest.get('protocol_version') != 2:
        raise ValueError('Controlling protocol v2 required')
    if not years or not set(years) <= set(manifest['stage1']):
        raise ValueError('Stage2 SEALED: Stage1 result and gate must be logged before any Stage2 access')
    raise ValueError('Stage1 blocked: validated full PIT/source coverage and once-only result ledger unavailable')


def stage_gate(summary, stage=1):
    """Input IC/t must be direction-oriented; H5 uses negative raw IC/t."""
    if stage not in (1, 2):
        raise ValueError('stage must be 1 or 2')
    required = ['mean','t','complete','placebo_pass'] + (['positive_blocks'] if stage == 1 else ['same_sign','net_spread'])
    if any(summary.get(k) is None for k in required):
        return False
    if not summary['complete'] or not summary['placebo_pass']:
        return False
    if not all(math.isfinite(summary[k]) for k in ('mean','t')):
        return False
    if stage == 1:
        return summary['mean'] > .01 and summary['t'] > 3 and summary['positive_blocks'] >= 3
    return summary['mean'] > 0 and summary['t'] > 2 and summary['same_sign'] and summary['net_spread'] > 0
