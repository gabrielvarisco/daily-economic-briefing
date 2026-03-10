import os
import unittest
from unittest.mock import patch, Mock

import requests

from main import send_telegram


class MainTests(unittest.TestCase):
    def test_send_telegram_returns_false_without_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(send_telegram("msg", run_id="r1"))

    def test_send_telegram_dry_run(self):
        with patch.dict(os.environ, {"DRY_RUN_TELEGRAM": "1"}, clear=True):
            self.assertTrue(send_telegram("msg", run_id="r1"))

    def test_send_telegram_retry_and_success(self):
        responses = [
            Mock(status_code=503, raise_for_status=Mock(side_effect=requests.HTTPError("503"))),
            Mock(status_code=200, raise_for_status=Mock(return_value=None)),
        ]

        with patch.dict(os.environ, {"TELEGRAM_TOKEN": "t", "CHAT_ID": "c"}, clear=True), \
             patch("main.requests.post", side_effect=responses), \
             patch("main.time.sleep", return_value=None):
            self.assertTrue(send_telegram("msg", run_id="r1", retries=2))


if __name__ == "__main__":
    unittest.main()
