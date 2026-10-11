"""Opt-in durable batching; flush complete batches, preserve input order and crash replay."""
from scripts.evolution_safety_20261010 import durable_append

def journal_evaluations(iterator,path,results,batch_size=8):
    if not isinstance(batch_size,int) or batch_size<1:raise ValueError('invalid batch_size')
    pending=[]
    for result in iterator:
        pending.append(result)
        if len(pending)>=batch_size:
            durable_append(path,pending)
            for row in pending:results[row['genome_hash']]=row
            pending=[]
    if pending:
        durable_append(path,pending)
        for row in pending:results[row['genome_hash']]=row
