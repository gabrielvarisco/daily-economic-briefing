import unittest
from unittest.mock import patch

from Scripts import pipeline


class PipelineTests(unittest.TestCase):
    def test_build_batches_with_optional_sections(self):
        sections = {
            "market_take": "m",
            "day_over_day": "d",
            "macro": "macro",
            "brazil": "br",
            "usa": "us",
            "drivers": "drv",
            "crypto": "c",
            "quant": "q",
            "news": "n",
        }

        batches = pipeline.build_batches(sections)
        self.assertEqual(len(batches), 3)
        self.assertIn("macro", batches[0])
        self.assertIn("drv", batches[0])
        self.assertIn("c", batches[1])

    def test_build_sections_collects_metrics_with_source(self):
        fake_specs = [
            pipeline.SectionSpec("a", "A", lambda: "ok", "internal"),
            pipeline.SectionSpec("b", "B", lambda: "", "rss"),
        ]

        with patch("Scripts.pipeline.get_section_specs", return_value=fake_specs):
            sections, metrics = pipeline.build_sections(run_id="r1")

        self.assertIn("a", sections)
        self.assertIn("b", sections)
        self.assertEqual(metrics["a"]["status"], "ok")
        self.assertEqual(metrics["a"]["source"], "internal")
        self.assertEqual(metrics["b"]["status"], "empty")
        self.assertEqual(metrics["b"]["source"], "rss")

    def test_build_health_report(self):
        metrics = {
            "m1": {"status": "ok", "elapsed_ms": 100},
            "m2": {"status": "empty", "elapsed_ms": 20},
            "m3": {"status": "error", "elapsed_ms": 5},
        }

        health = pipeline.build_health_report(metrics)
        self.assertEqual(health["ok_sections"], 1)
        self.assertEqual(health["empty_sections"], 1)
        self.assertEqual(health["error_sections"], 1)
        self.assertEqual(health["elapsed_total_ms"], 125)
        self.assertEqual(set(health["degraded_sections"]), {"m2", "m3"})


if __name__ == "__main__":
    unittest.main()
