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
            "crypto": "c",
            "quant": "q",
            "news": "n",
        }

        batches = pipeline.build_batches(sections)
        self.assertEqual(len(batches), 3)
        self.assertIn("macro", batches[0])
        self.assertIn("c", batches[1])

    def test_build_sections_collects_metrics(self):
        fake_specs = [
            pipeline.SectionSpec("a", "A", lambda: "ok"),
            pipeline.SectionSpec("b", "B", lambda: ""),
        ]

        with patch("Scripts.pipeline.get_section_specs", return_value=fake_specs):
            sections, metrics = pipeline.build_sections(run_id="r1")

        self.assertIn("a", sections)
        self.assertIn("b", sections)
        self.assertEqual(metrics["a"]["status"], "ok")
        self.assertIn(metrics["b"]["status"], {"empty", "ok"})


if __name__ == "__main__":
    unittest.main()
