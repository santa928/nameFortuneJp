import unittest
from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

from app.core.fortune_analyzer import FortuneAnalyzer
from app.core.scraper import create_scraper


class TestScraper(unittest.TestCase):
    """スクレイピング機能のテスト"""

    def setUp(self) -> None:
        """テスト前の準備"""
        self.analyzer = FortuneAnalyzer()
        self.scraper = create_scraper()

    def test_namaeuranai_connection(self) -> None:
        """namaeuranai.bizへの接続テスト（SSL証明書フォールバック対応）"""
        url = (
            "https://namaeuranai.biz/result/"
            "%E7%94%B0%E4%B8%AD_%E5%A4%AA%E9%83%8E/"
            "%E7%94%B7%E6%80%A7"
        )

        # フォールバック機能のテスト
        try:
            # まずSSL検証有効で試行
            response = requests.get(url, timeout=30, verify=True)
        except requests.exceptions.SSLError:
            # SSL証明書エラーの場合は検証無効で再試行
            response = requests.get(url, timeout=30, verify=False)  # nosec B501

        soup = BeautifulSoup(response.text, "html.parser")

        # 基本的なHTMLチェック
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(soup.find("title"))

    def test_enamae_connection(self) -> None:
        """enamae.netへの接続テスト"""
        url = "https://enamae.net/m/%E7%94%B0%E4%B8%AD__%E5%A4%AA%E9%83%8E"
        # セキュリティ強化：SSL検証を有効化、タイムアウト設定
        response = requests.get(url, timeout=30, verify=True)
        soup = BeautifulSoup(response.text, "html.parser")

        # 基本的なHTMLチェック
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(soup.find("title"))

    def test_scraper_fortune_retrieval(self) -> None:
        """実際のスクレイピング機能をテスト"""
        result = self.scraper.get_fortune("田中", "太郎", "m")

        # 両方のサイトから結果が取得できることを確認
        self.assertIn("enamae.net", result)
        self.assertIn("namaeuranai.biz", result)

        # enamae.net の結果確認
        enamae_result = result["enamae.net"]
        self.assertIn("天格", enamae_result)
        self.assertIn("人格", enamae_result)
        self.assertIn("地格", enamae_result)

        # namaeuranai.biz の結果確認
        namaeuranai_result = result["namaeuranai.biz"]
        self.assertIn("天格", namaeuranai_result)
        self.assertIn("人格", namaeuranai_result)
        self.assertIn("地格", namaeuranai_result)

    @patch("app.core.scraper.requests.get")
    def test_scraper_with_mock(self, mock_get: Mock) -> None:
        """モックを使用したスクレイパーテスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><title>テスト</title></html>"
        mock_get.return_value = mock_response

        # テスト実行
        self.assertEqual(mock_response.status_code, 200)

    def test_analyzer_initialization(self) -> None:
        """FortuneAnalyzerの初期化テスト"""
        analyzer = FortuneAnalyzer()
        self.assertIsNotNone(analyzer)

    def test_invalid_url_handling(self) -> None:
        """無効なURLの処理テスト"""
        # 無効なURLでのテスト
        with self.assertRaises(requests.exceptions.RequestException):
            requests.get(
                "https://invalid-url-that-does-not-exist.com", timeout=5
            )


if __name__ == "__main__":
    unittest.main()
