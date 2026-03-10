import unittest
from unittest.mock import patch

import pandas as pd

from Scripts.asset_analyzer import _safe_download, analyze_asset


class AssetAnalyzerTests(unittest.TestCase):
    def test_safe_download_returns_series_when_data_available(self):
        idx = pd.date_range("2024-01-01", periods=2)
        df = pd.DataFrame({"Close": [10.0, 11.0]}, index=idx)

        with patch("Scripts.asset_analyzer.yf.download", return_value=df):
            close = _safe_download("SPY", retries=1)

        self.assertEqual(len(close), 2)
        self.assertAlmostEqual(float(close.iloc[-1]), 11.0)

    def test_analyze_asset_sets_quality_flags(self):
        idx = pd.date_range("2024-01-01", periods=6)
        # salto diário extremo para disparar outlier
        df = pd.DataFrame({"Close": [10.0, 10.0, 10.0, 10.0, 10.0, 20.0]}, index=idx)

        with patch("Scripts.asset_analyzer.yf.download", return_value=df), \
             patch.dict("os.environ", {"MAX_DAILY_CHANGE_ABS": "5"}, clear=False):
            asset = analyze_asset("SPY", period="1mo", interval="1d", ma_windows=[2])

        self.assertIsNotNone(asset)
        self.assertTrue(asset["is_suspect"])
        self.assertIn("daily_change_outlier", asset["quality_flags"])


if __name__ == "__main__":
    unittest.main()
