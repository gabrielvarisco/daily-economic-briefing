import unittest
from unittest.mock import patch

from Scripts.drivers_of_day import drivers_of_day


class DriversOfDayTests(unittest.TestCase):
    def test_drivers_output_contains_core_lines(self):
        fake = {
            "^IRX": {"price": 4.5, "daily_change": 0.1},
            "^TNX": {"price": 4.2, "daily_change": -0.2},
            "^VIX": {"price": 14.0, "daily_change": 1.0},
            "DX-Y.NYB": {"price": 103.1, "daily_change": -0.1},
            "HYG": {"price": 78.4, "daily_change": 0.3},
        }

        def _mock_analyze_asset(ticker, **kwargs):
            return fake.get(ticker)

        with patch("Scripts.drivers_of_day.analyze_asset", side_effect=_mock_analyze_asset):
            text = drivers_of_day()

        self.assertIn("Drivers do Dia", text)
        self.assertIn("Curva 2s10s", text)
        self.assertIn("VIX:", text)
        self.assertIn("DXY:", text)
        self.assertIn("HYG:", text)


if __name__ == "__main__":
    unittest.main()
