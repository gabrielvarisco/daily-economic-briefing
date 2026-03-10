import unittest
from unittest.mock import patch

import pandas as pd

from Scripts.asset_analyzer import _safe_download


class AssetAnalyzerTests(unittest.TestCase):
    def test_safe_download_returns_series_when_data_available(self):
        idx = pd.date_range("2024-01-01", periods=2)
        df = pd.DataFrame({"Close": [10.0, 11.0]}, index=idx)

        with patch("Scripts.asset_analyzer.yf.download", return_value=df):
            close = _safe_download("SPY", retries=1)

        self.assertEqual(len(close), 2)
        self.assertAlmostEqual(float(close.iloc[-1]), 11.0)


if __name__ == "__main__":
    unittest.main()
