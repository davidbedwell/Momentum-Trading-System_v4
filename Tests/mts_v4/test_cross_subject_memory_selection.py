import json
import tempfile
import unittest
from pathlib import Path

from MTS_V4.cross_subject_memory import ResearchFrontierState, ScientificMemoryRecord
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore


class CrossSubjectMemorySelectionTests(unittest.TestCase):
    def _store(self, root: Path, run_name: str) -> JsonCrossSubjectScientificMemoryStore:
        path = root / run_name / "cross_subject_memory.json"
        return JsonCrossSubjectScientificMemoryStore(path)

    @staticmethod
    def _record(record_id: str, subject_id: str = "equity:AAPL") -> ScientificMemoryRecord:
        return ScientificMemoryRecord(
            record_id=record_id,
            subject_id=subject_id,
            kind="TEST_RECORD",
            summary=f"summary for {record_id}",
        )

    def test_discover_current_selects_unique_accumulated_superset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            older = self._store(root, "mts-v4-older")
            newer = self._store(root, "mts-v4-newer")

            shared = self._record("r1")
            added = self._record("r2", "equity:MSFT")
            older.publish(shared)
            newer.publish_batch((shared, added))
            newer.set_frontier(
                ResearchFrontierState(
                    version=2,
                    summary="newer accumulated frontier",
                    source_record_ids=("r1", "r2"),
                )
            )

            selection = JsonCrossSubjectScientificMemoryStore.discover_current(root)

            self.assertIsNotNone(selection)
            assert selection is not None
            self.assertEqual(selection.source_path, newer.path)
            self.assertEqual({record.record_id for record in selection.store.records()}, {"r1", "r2"})
            self.assertEqual(selection.superseded_paths, (older.path,))

    def test_discover_current_rejects_incomparable_snapshots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = self._store(root, "mts-v4-first")
            second = self._store(root, "mts-v4-second")
            first.publish(self._record("r1"))
            second.publish(self._record("r2", "equity:MSFT"))

            with self.assertRaisesRegex(ValueError, "multiple incomparable current snapshots"):
                JsonCrossSubjectScientificMemoryStore.discover_current(root)

    def test_discover_current_rejects_conflicting_record_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first_path = root / "mts-v4-first" / "cross_subject_memory.json"
            second_path = root / "mts-v4-second" / "cross_subject_memory.json"
            first = JsonCrossSubjectScientificMemoryStore(first_path)
            first.publish(self._record("r1"))

            second_path.parent.mkdir(parents=True, exist_ok=True)
            raw = json.loads(first_path.read_text(encoding="utf-8"))
            raw["records"][0]["summary"] = "different scientific statement under reused identity"
            second_path.write_text(json.dumps(raw), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "conflicting cross-subject scientific memory record_id"):
                JsonCrossSubjectScientificMemoryStore.discover_current(root)

    def test_persisted_snapshot_metadata_is_storage_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = self._store(root, "mts-v4-run")
            store.publish(self._record("r1"))
            store.set_frontier(
                ResearchFrontierState(
                    version=3,
                    summary="RD-authored frontier",
                    source_record_ids=("r1",),
                )
            )

            raw = json.loads(store.path.read_text(encoding="utf-8"))
            self.assertEqual(raw["snapshot"]["record_count"], 1)
            self.assertEqual(raw["snapshot"]["record_ids"], ["r1"])
            self.assertEqual(raw["snapshot"]["frontier_version"], 3)
            self.assertEqual(
                raw["snapshot"]["supersession_semantics"],
                "OBJECTIVE_ACCUMULATED_RECORD_CONTAINMENT",
            )
            self.assertEqual(raw["policy"]["scientific_content_authority"], "AI_RD")


if __name__ == "__main__":
    unittest.main()
