from .legacy_archive_index import iter_strategies

def sample():
    out={}
    for study in ('GA4_DIAGNOSTIC','HORIZONS'):
        row=next(iter_strategies(study))
        out[study]={'key':row.chromosome_id,'definition':row.definition[:350], 'chromosome':row.chromosome[:200], 'horizon':row.horizon[:80]}
    return out
