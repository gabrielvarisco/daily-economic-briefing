import tempfile
import unittest
from unittest.mock import patch

from Scripts import history_store


class HistoryStoreTests(unittest.TestCase):
    def test_save_snapshot_with_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("Scripts.history_store.HISTORY_DIR", tmp_dir):
                path = history_store.save_daily_snapshot(
                    {"k": "v"},
                    metadata={"run_id": "abc", "health_report": {"ok_sections": 1}},
                )
                content = history_store.load_latest_snapshot()

        self.assertTrue(path.endswith(".json"))
        self.assertEqual(content["schema_version"], 2)
        self.assertIn("metadata", content)
        self.assertEqual(content["metadata"]["run_id"], "abc")


if __name__ == "__main__":
    unittest.main()
