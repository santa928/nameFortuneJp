import logging
from scraper import create_scraper
import unittest
from scraper import NameFortuneScraper
from bs4 import BeautifulSoup
import requests
import urllib3
from fortune_analyzer import FortuneAnalyzer

# SSL証明書の警告を無効化
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestNameFortuneScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = NameFortuneScraper()

    def test_namaeuranai_scraping(self):
        """namaeuranai.bizのスクレイピングテスト"""
        url = "https://namaeuranai.biz/result/%E7%94%B0%E4%B8%AD_%E5%A4%AA%E9%83%8E/%E7%94%B7%E6%80%A7"
        response = requests.get(url, verify=False)  # SSL検証を無効化
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 結果ボックスを取得
        result_boxes = soup.find_all('div', class_='result-box')
        self.assertGreater(len(result_boxes), 0, "結果ボックスが見つかりません")
        
        # 各運勢の要素を確認
        for box in result_boxes:
            title = box.find('h3', class_='title01')
            if title:
                print(f"Found title: {title.text}")
                fortune = box.find('span', class_='f-large')
                if fortune:
                    print(f"Found fortune: {fortune.text}")
                description = box.find('p', class_='text02')
                if description:
                    print(f"Found description: {description.text}")

    def test_enamae_scraping(self):
        """enamae.netのスクレイピングテスト"""
        url = "https://enamae.net/m/%E7%94%B0%E4%B8%AD__%E5%A4%AA%E9%83%8E"
        response = requests.get(url, verify=False)  # SSL検証を無効化
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # h2タグを検索
        h2_tags = soup.find_all('h2')
        self.assertGreater(len(h2_tags), 0, "h2タグが見つかりません")
        
        for h2 in h2_tags:
            print(f"Found h2: {h2.text}")
            next_p = h2.find_next('p')
            if next_p:
                print(f"Found description: {next_p.text}")

class TestScraperAndScoring(unittest.TestCase):
    def setUp(self):
        self.scraper = create_scraper()
        self.analyzer = FortuneAnalyzer()

    def test_tanaka_taro(self):
        """田中太郎のケースをテスト"""
        # スクレイピング結果を取得
        fortune_result = self.scraper.get_fortune("田中", "太郎", "m")
        
        # 結果をログ出力
        logger.info("=== enamae.net の結果 ===")
        for key, value in fortune_result["enamae"].items():
            if not key.endswith("_説明"):
                logger.info(f"{key}: {value}")
        
        logger.info("\n=== namaeuranai.biz の結果 ===")
        for key, value in fortune_result["namaeuranai"].items():
            if not key.endswith("_説明"):
                logger.info(f"{key}: {value}")

        # スコア計算
        enamae_score = self.analyzer._calculate_enamae_score(fortune_result["enamae"])
        namaeuranai_score = self.analyzer._calculate_namaeuranai_score(fortune_result["namaeuranai"])
        total_score = (enamae_score + namaeuranai_score) / 2

        logger.info("\n=== スコア計算結果 ===")
        logger.info(f"enamae スコア: {enamae_score}")
        logger.info(f"namaeuranai スコア: {namaeuranai_score}")
        logger.info(f"総合スコア: {total_score}")

        # スコアが0でないことを確認
        self.assertGreater(enamae_score, 0, "enamae スコアが0です")
        self.assertGreater(namaeuranai_score, 0, "namaeuranai スコアが0です")

if __name__ == '__main__':
    unittest.main() 