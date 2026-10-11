"""Non-selecting candidate-level Stage 1 metadata, aligned to evaluated rows."""
import numpy as np

FIELDS=('galaxy_strength','galaxy_trajectory','galaxy_rv20','sector_strength','sector_trajectory','sector_rv20','sector_rel20','sector_rel60')

def summarize_candidate_context(context_frame, selected, reference):
    mask=np.asarray(selected)
    if mask.dtype!=np.dtype(bool) or mask.ndim!=1 or len(mask)!=len(context_frame):
        raise ValueError('Candidate/context row alignment mismatch')
    if reference.get('status')!='ALIGNED_METADATA_NOT_PIT_CERTIFIED':
        raise ValueError('Unverified Stage 1 context reference')
    subset=context_frame.loc[mask]
    summary={}
    for name in FIELDS:
        values=subset[name].to_numpy(dtype=float)
        finite=values[np.isfinite(values)]
        summary[name]={'observed_n':int(len(finite)),'missing_n':int(len(values)-len(finite)),
                       'mean':float(finite.mean()) if len(finite) else None}
    return {'reference':dict(reference),'selected_rows':int(mask.sum()),
            'continuous_descriptors':summary,
            'broad_labels_use':'DESCRIPTIVE_ONLY_NOT_GA_SELECTION'}
