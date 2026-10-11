"""Optional Stage1 human-semantic enrichment; machine GA requires only predictors."""
import pandas as pd
from .ga4_stage1_context_join import attach_context

def load_optional_context(pred,stage1,expected_hashes,sha):
    try:
        for name,digest in expected_hashes.items():
            if sha(stage1/name)!=digest:raise ValueError('Stage1 hash mismatch')
        gate=__import__('json').loads((stage1/'gate.json').read_text())
        if gate.get('decision')!='PASS':raise ValueError('Stage1 gate not PASS')
        linked=attach_context(pred,pd.read_parquet(stage1/'galaxy_context.parquet'),pd.read_parquet(stage1/'sector_context.parquet'))
        if len(linked)!=len(pred) or not linked.security_id.astype(str).reset_index(drop=True).equals(pred.security_id.astype(str).reset_index(drop=True)) or not pd.to_datetime(linked.effective_date).reset_index(drop=True).equals(pd.to_datetime(pred.effective_date).reset_index(drop=True)):
            raise ValueError('Stage1 ordering mismatch')
        return linked,{'status':'ALIGNED_METADATA_NOT_PIT_CERTIFIED','scope':'DEV80','galaxy_sha256':expected_hashes['galaxy_context.parquet'],'sector_sha256':expected_hashes['sector_context.parquet']}
    except (OSError,ValueError,KeyError,TypeError,ImportError) as exc:
        return None,{'status':'UNAVAILABLE_OPTIONAL','scope':'DEV80','reason':type(exc).__name__}
