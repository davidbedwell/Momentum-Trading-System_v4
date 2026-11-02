"""Durable local state; atomic publication, no overwrite, content-addressed adapters."""
import hashlib
import json
import os
import tempfile
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def publish(path, value):
    """Link a fully fsynced temporary inode once; concurrent writers cannot replace it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, sort_keys=True, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(name)


def resume_source(cache, provider, request, loader):
    """One immutable object per explicit provider/request; failures remain retryable."""
    key = digest(dict(provider=provider, request=request))
    path = Path(cache) / (key + '.json')
    if path.exists():
        item = json.loads(path.read_text())
        if item['request_hash'] != key or digest(item['payload']) != item['payload_hash']:
            raise ValueError('Corrupt source checkpoint')
        return item['payload']
    payload = loader()
    item = dict(provider=provider, request_hash=key, payload_hash=digest(payload), payload=payload)
    try:
        publish(path, item)
    except FileExistsError:
        return resume_source(cache, provider, request, loader)
    return payload
