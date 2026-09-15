from __future__ import annotations

import tarfile

from MTS_V4.campaign_compact_export import create_compact_campaign_export


def test_compact_export_includes_science_but_excludes_market_store_and_cache(tmp_path):
    state = tmp_path / "campaign"
    (state / "research_packages").mkdir(parents=True)
    (state / "research_nexus.json").write_text("{}\n", encoding="utf-8")
    (state / "batch_reports.jsonl").write_text("{}\n", encoding="utf-8")
    (state / "research_packages" / "RP-0001.json").write_text("{}\n", encoding="utf-8")
    (state / "analysis_cache" / "data").mkdir(parents=True)
    (state / "analysis_cache" / "data" / "rows.parquet").write_bytes(b"market rows")
    (state / "sol_replay_envelopes.jsonl").write_text("large transport", encoding="utf-8")
    output = tmp_path / "compact.tar.gz"

    manifest = create_compact_campaign_export(state_dir=state, output_path=output)

    with tarfile.open(output, "r:gz") as archive:
        names = set(archive.getnames())
    assert names == {
        "research_nexus.json",
        "batch_reports.jsonl",
        "research_packages/RP-0001.json",
        "compact_export_manifest.json",
    }
    assert all(not item["path"].endswith(".parquet") for item in manifest["contents"])
