from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterator, Mapping


def append_jsonl(path: str | Path, payload: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    ) + "\n"
    if target.suffix == ".gz":
        with gzip.open(target, "at", encoding="utf-8") as handle:
            handle.write(encoded)
        return
    with target.open("a", encoding="utf-8") as handle:
        handle.write(encoded)


def iter_jsonl(path: str | Path) -> Iterator[Mapping[str, object]]:
    source = Path(path)
    opener = gzip.open if source.suffix == ".gz" else source.open
    kwargs = {"encoding": "utf-8"}
    with opener(source, "rt", **kwargs) if source.suffix == ".gz" else opener("r", **kwargs) as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, Mapping):
                raise ValueError(f"JSONL row must be an object: {source}:{line_number}")
            yield value
