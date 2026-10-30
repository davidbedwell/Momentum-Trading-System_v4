"""Exclusion configuration for exploratory development only."""

# AMD is a distinct successor security, never an alias for XLNX.
LINEAGES = (
    dict(lineage='FB/META', aliases=('FB', 'META'),
         reason='FB_META_IDENTITY_LINEAGE_QUARANTINED_FOR_EXPLORATORY_DEVELOPMENT'),
    dict(lineage='XLNX', aliases=('XLNX',),
         reason='XLNX_ACQUIRED_BY_AMD_DISTINCT_SUCCESSOR_NOT_A_BAR_ALIAS'),
)


def exclusions(paths):
    """Report every configured lineage, including absent/already blocked aliases."""
    paths = list(paths)
    records = []
    for rule in LINEAGES:
        matched = [p.stem for p in paths if p.stem.strip().upper() in rule['aliases']]
        records.append(dict(**rule, matched_symbols=matched, symbol_count=len(matched)))
    return records
