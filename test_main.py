import unittest
from unittest.mock import patch

import requests

import main


class TestApiFailure(unittest.TestCase):
    @patch("main.requests.get", side_effect=requests.ConnectionError("no internet"))
    def test_exits_cleanly_when_offline(self, mock_get):
        with self.assertRaises(SystemExit) as cm:
            main.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("main.requests.get", side_effect=requests.Timeout("too slow"))
    def test_exits_cleanly_on_timeout(self, mock_get):
        with self.assertRaises(SystemExit) as cm:
            main.main()
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()