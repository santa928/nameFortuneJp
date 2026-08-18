import unittest
from unittest.mock import patch

import requests

from app.core.fortune_analyzer import FortuneAnalyzer
from app.core.scraper import create_scraper
from app.main import app


class TestProviderFailures(unittest.TestCase):
    """外部姓名判断サイトの障害時挙動を検証する。"""

    @patch("app.core.scraper.requests.get")
    def test_scraper_marks_provider_failures(self, mock_get) -> None:
        mock_get.side_effect = requests.Timeout("upstream timeout")

        result = create_scraper().get_fortune("田中", "太郎", "m")

        for provider in ("enamae.net", "namaeuranai.biz"):
            self.assertFalse(result[provider]["success"])
            self.assertEqual(result[provider]["data"], {})
            self.assertIn("timeout", result[provider]["error"].lower())

    def test_calculate_scores_uses_only_successful_provider(self) -> None:
        analyzer = FortuneAnalyzer()
        fortune_result = {
            "enamae": {
                "天格": "大吉",
                "人格": "大吉",
                "地格": "大吉",
                "外格": "大吉",
                "総格": "大吉",
                "三才配置": "大吉",
            },
            "namaeuranai": {},
        }

        enamae_score, namaeuranai_score, total_score = analyzer._calculate_scores(
            fortune_result,
            provider_success={"enamae": True, "namaeuranai": False},
        )

        self.assertEqual(enamae_score, 100)
        self.assertEqual(namaeuranai_score, 0)
        self.assertEqual(total_score, 100)

    def test_analyze_returns_bad_gateway_when_all_providers_fail(self) -> None:
        failed_result = {
            "enamae.net": {"success": False, "data": {}, "error": "timeout"},
            "namaeuranai.biz": {"success": False, "data": {}, "error": "timeout"},
        }

        with patch("app.main.scraper.get_fortune", return_value=failed_result):
            response = app.test_client().post(
                "/analyze",
                json={"last_name": "田中", "first_name": "太郎", "gender": "m"},
            )

        self.assertEqual(response.status_code, 502)
        self.assertIn("外部サイト", response.get_json()["error"])

    def test_analyze_returns_successful_provider_when_other_provider_fails(
        self,
    ) -> None:
        partial_result = {
            "enamae.net": {
                "success": True,
                "data": {"天格": "吉"},
                "error": None,
            },
            "namaeuranai.biz": {"success": False, "data": {}, "error": "timeout"},
        }

        with patch("app.main.scraper.get_fortune", return_value=partial_result):
            response = app.test_client().post(
                "/analyze",
                json={"last_name": "田中", "first_name": "太郎", "gender": "m"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"enamae": {"天格": "吉"}, "namaeuranai": {}},
        )


if __name__ == "__main__":
    unittest.main()
