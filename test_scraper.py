import logging
from scraper import create_scraper
import unittest
from scraper import NameFortuneScraper
from bs4 import BeautifulSoup
import requests
import urllib3

# SSL証明書の警告を無効化
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    scraper = create_scraper()
    results = scraper.get_fortune("田中", "太郎", "m")
    
    logger.info("スクレイピング結果:")
    if not results:
        logger.error("結果が空です")
        exit(1)
        
    if "error" in results:
        logger.error(f"エラー: {results['error']}")
        exit(1)
        
    # 結果を整形して表示
    fortune_types = ["天格", "人格", "地格", "外格", "総格", "三才配置", "陰陽配列"]
    for fortune_type in fortune_types:
        if fortune_type in results:
            logger.info(f"{fortune_type}: {results[fortune_type]}")
            if f"{fortune_type}_説明" in results:
                logger.info(f"説明: {results[f'{fortune_type}_説明']}")
            logger.info("-" * 50)

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

if __name__ == "__main__":
    unittest.main()
    main() 