import unittest
from unittest.mock import Mock, patch

import requests

from app.core.fortune_analyzer import FortuneAnalyzer
from app.core.scraper import create_scraper


class TestScraper(unittest.TestCase):
    """スクレイピング機能のテスト"""

    ENAMAE_HTML = """
    <html>
      <title>姓名判断</title>
      <h2>天格（祖運）は9画で『吉』</h2><p>天格の説明</p>
      <h2>人格（主運）は12画で『大吉』</h2><p>人格の説明</p>
      <h2>地格（初運）は15画で『吉』</h2><p>地格の説明</p>
    </html>
    """

    NAMAEURANAI_HTML = """
    <html>
      <title>姓名判断</title>
      <div class="result-box">
        <h3 class="title01">天格</h3>
        <span class="f-large">吉</span>
        <p class="text02">天格の説明</p>
      </div>
      <div class="result-box">
        <h3 class="title01">人格</h3>
        <span class="f-large">大吉</span>
        <p class="text02">人格の説明</p>
      </div>
      <div class="result-box">
        <h3 class="title01">地格</h3>
        <span class="f-large">吉</span>
        <p class="text02">地格の説明</p>
      </div>
    </html>
    """

    def setUp(self) -> None:
        """テスト前の準備"""
        self.analyzer = FortuneAnalyzer()
        self.scraper = create_scraper()

    @staticmethod
    def _response(html: str) -> Mock:
        response = Mock()
        response.status_code = 200
        response.text = html
        response.raise_for_status.return_value = None
        return response

    @patch("app.core.scraper.requests.get")
    def test_enamae_retrieval(self, mock_get: Mock) -> None:
        """enamae.net のHTTP応答から運勢を抽出できること"""
        mock_get.return_value = self._response(self.ENAMAE_HTML)

        result = self.scraper._get_enamae_fortune("田中", "太郎", "m")

        self.assertEqual(result["天格"], "吉")
        self.assertEqual(result["人格"], "大吉")
        self.assertEqual(result["地格"], "吉")
        mock_get.assert_called_once_with(
            "https://enamae.net/m/%E7%94%B0%E4%B8%AD__%E5%A4%AA%E9%83%8E",
            timeout=30,
            verify=True,
        )

    @patch("app.core.scraper.requests.get")
    def test_namaeuranai_retrieval(self, mock_get: Mock) -> None:
        """namaeuranai.biz のHTTP応答から運勢を抽出できること"""
        mock_get.return_value = self._response(self.NAMAEURANAI_HTML)

        result = self.scraper._get_namaeuranai_fortune("田中", "太郎", "m")

        self.assertEqual(result["天格"], "吉")
        self.assertEqual(result["人格"], "大吉")
        self.assertEqual(result["地格"], "吉")
        mock_get.assert_called_once_with(
            "https://namaeuranai.biz/result/"
            "%E7%94%B0%E4%B8%AD_%E5%A4%AA%E9%83%8E/%E7%94%B7%E6%80%A7",
            timeout=30,
            verify=True,
        )

    @patch("app.core.scraper.requests.get")
    def test_scraper_fortune_retrieval(self, mock_get: Mock) -> None:
        """固定HTMLを使って両プロバイダーの取得処理を一通り検証"""
        mock_get.side_effect = [
            self._response(self.ENAMAE_HTML),
            self._response(self.NAMAEURANAI_HTML),
        ]

        result = self.scraper.get_fortune("田中", "太郎", "m")

        self.assertEqual(result["enamae.net"]["天格"], "吉")
        self.assertEqual(result["enamae.net"]["人格"], "大吉")
        self.assertEqual(result["enamae.net"]["地格"], "吉")
        self.assertEqual(result["namaeuranai.biz"]["天格"], "吉")
        self.assertEqual(result["namaeuranai.biz"]["人格"], "大吉")
        self.assertEqual(result["namaeuranai.biz"]["地格"], "吉")
        self.assertEqual(mock_get.call_count, 2)

    @patch("app.core.scraper.requests.get")
    def test_namaeuranai_ssl_fallback(self, mock_get: Mock) -> None:
        """SSLエラー時に namaeuranai.biz だけ検証無効で再試行すること"""
        mock_get.side_effect = [
            requests.exceptions.SSLError("certificate error"),
            self._response(self.NAMAEURANAI_HTML),
        ]

        result = self.scraper._get_namaeuranai_fortune("田中", "太郎", "m")

        self.assertEqual(result["天格"], "吉")
        self.assertEqual(mock_get.call_count, 2)
        self.assertTrue(mock_get.call_args_list[0].kwargs["verify"])
        self.assertFalse(mock_get.call_args_list[1].kwargs["verify"])

    def test_analyzer_initialization(self) -> None:
        """FortuneAnalyzerの初期化テスト"""
        analyzer = FortuneAnalyzer()
        self.assertIsNotNone(analyzer)

    @patch(
        "app.core.scraper.requests.get",
        side_effect=requests.exceptions.RequestException("network down"),
    )
    def test_request_failure_returns_empty_results(self, mock_get: Mock) -> None:
        """外部サイトへの通信失敗時は両プロバイダーを空結果として返すこと"""
        result = self.scraper.get_fortune("田中", "太郎", "m")

        self.assertEqual(
            result,
            {
                "enamae.net": {},
                "namaeuranai.biz": {},
            },
        )
        self.assertEqual(mock_get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
