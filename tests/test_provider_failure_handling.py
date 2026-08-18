import unittest
from unittest.mock import patch

from app.main import app


class TestProviderFailureHandling(unittest.TestCase):
    def setUp(self) -> None:
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("app.main.scraper.get_fortune")
    def test_analyze_returns_502_when_all_providers_fail(self, get_fortune) -> None:
        get_fortune.return_value = {"enamae.net": {}, "namaeuranai.biz": {}}

        response = self.client.post(
            "/analyze",
            json={"last_name": "田中", "first_name": "太郎", "gender": "m"},
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.get_json()["error_code"], "PROVIDER_UNAVAILABLE")

    @patch("app.main.scraper.get_fortune")
    def test_analyze_returns_partial_result_when_one_provider_succeeds(
        self, get_fortune
    ) -> None:
        get_fortune.return_value = {
            "enamae.net": {"天格": "吉"},
            "namaeuranai.biz": {},
        }

        response = self.client.post(
            "/analyze",
            json={"last_name": "田中", "first_name": "太郎", "gender": "m"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["enamae"], {"天格": "吉"})
        self.assertEqual(response.get_json()["namaeuranai"], {})


if __name__ == "__main__":
    unittest.main()
