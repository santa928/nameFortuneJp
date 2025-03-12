import requests
from bs4 import BeautifulSoup
import urllib.parse
import logging
import re
import urllib3

# SSL証明書の警告を無効化
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NameFortuneScraper:
    # 結果の表示順序を定義
    COMMON_KEYS = ["天格", "人格", "地格", "外格", "総格"]
    ENAMAE_ONLY_KEYS = ["三才配置", "陰陽配列"]
    NAMAEURANAI_ONLY_KEYS = ["仕事運", "家庭運"]

    def __init__(self):
        self.ENAMAE_URL = "https://enamae.net"
        self.NAMAEURANAI_URL = "https://namaeuranai.biz"

    def get_fortune(self, last_name, first_name, gender='m'):
        """両サイトから運勢を取得"""
        try:
            # enamae.netの結果を取得
            enamae_results = self._get_enamae_fortune(last_name, first_name, gender)
            
            # namaeuranai.bizの結果を取得
            namaeuranai_results = self._get_namaeuranai_fortune(last_name, first_name, gender)
            
            # 結果を整理して統合
            return {
                "enamae": self._sort_results(enamae_results, is_enamae=True),
                "namaeuranai": self._sort_results(namaeuranai_results, is_enamae=False)
            }
            
        except Exception as e:
            logger.error(f"予期せぬエラーが発生: {e}")
            return {"error": "予期せぬエラーが発生しました"}

    def _sort_results(self, results, is_enamae=True):
        """結果を定義された順序に並び替え"""
        sorted_results = {}
        
        # 共通項目を先に追加
        for key in self.COMMON_KEYS:
            if key in results:
                sorted_results[key] = results[key]
                if f"{key}_説明" in results:
                    sorted_results[f"{key}_説明"] = results[f"{key}_説明"]
        
        # サイト固有の項目を追加
        specific_keys = self.ENAMAE_ONLY_KEYS if is_enamae else self.NAMAEURANAI_ONLY_KEYS
        for key in specific_keys:
            if key in results:
                sorted_results[key] = results[key]
                if f"{key}_説明" in results:
                    sorted_results[f"{key}_説明"] = results[f"{key}_説明"]
        
        return sorted_results

    def _get_enamae_fortune(self, last_name, first_name, gender):
        """enamae.netから運勢を取得"""
        try:
            encoded_name = f"{urllib.parse.quote(last_name)}__{urllib.parse.quote(first_name)}"
            url = f"{self.ENAMAE_URL}/{gender}/{encoded_name}#result"
            logger.debug(f"enamae.net リクエストURL: {url}")

            response = requests.get(url, verify=False)  # SSL検証を無効化
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_enamae_results(soup)

        except requests.RequestException as e:
            logger.error(f"enamae.net リクエストエラー: {e}")
            return {"error": "通信エラーが発生しました"}

    def _get_namaeuranai_fortune(self, last_name, first_name, gender):
        """namaeuranai.bizから運勢を取得"""
        try:
            gender_str = "男性" if gender == "m" else "女性"
            encoded_name = f"{urllib.parse.quote(last_name)}_{urllib.parse.quote(first_name)}"
            url = f"{self.NAMAEURANAI_URL}/result/{encoded_name}/{urllib.parse.quote(gender_str)}"
            logger.debug(f"namaeuranai.biz リクエストURL: {url}")

            response = requests.get(url, verify=False)  # SSL検証を無効化
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_namaeuranai_results(soup)

        except requests.RequestException as e:
            logger.error(f"namaeuranai.biz リクエストエラー: {e}")
            return {"error": "通信エラーが発生しました"}

    def _extract_enamae_results(self, soup):
        """enamae.netの結果を抽出"""
        results = {}
        try:
            h2_tags = soup.find_all('h2')
            
            # 共通項目を先に抽出
            for h2 in h2_tags:
                text = h2.text.strip()
                for key in self.COMMON_KEYS:
                    if key in text:
                        fortune_match = re.search(r'『(.+?)』', text)
                        if fortune_match:
                            results[key] = fortune_match.group(1)
                            next_p = h2.find_next('p')
                            if next_p:
                                results[f"{key}_説明"] = next_p.text.strip()
            
            # サイト固有の項目を後で抽出
            for h2 in h2_tags:
                text = h2.text.strip()
                if "三才配置" in text:
                    # 三才配置の運勢を抽出（例：「三才配置は『水⇒金⇒火』で『凶』」）
                    fortune_match = re.search(r'『(.+?)』で『(.+?)』', text)
                    if fortune_match:
                        results["三才配置"] = fortune_match.group(2)  # 運勢（凶）
                        results["三才配置_説明"] = f"配置: {fortune_match.group(1)}"  # 配置（水⇒金⇒火）
                        next_p = h2.find_next('p')
                        if next_p:
                            results["三才配置_説明"] += f"\n{next_p.text.strip()}"
                elif "陰陽配列" in text:
                    # 陰陽配列の情報を抽出
                    pattern_match = re.search(r'「(.+?)」', text)
                    if pattern_match:
                        results["陰陽配列"] = pattern_match.group(1)
                        next_p = h2.find_next('p')
                        if next_p:
                            results["陰陽配列_説明"] = next_p.text.strip()

            return results

        except Exception as e:
            logger.error(f"enamae.net 結果の抽出中にエラーが発生: {e}")
            return {}

    def _extract_namaeuranai_results(self, soup):
        """namaeuranai.bizの結果を抽出"""
        results = {}
        try:
            result_boxes = soup.find_all('div', class_='result-box')
            
            # 共通項目を先に抽出
            for box in result_boxes:
                title = box.find('h3', class_='title01')
                if title:
                    key = title.text.strip()
                    if key in self.COMMON_KEYS:
                        fortune = box.find('span', class_='f-large')
                        description = box.find('p', class_='text02')
                        
                        if fortune:
                            results[key] = fortune.text.strip()
                        if description:
                            results[f"{key}_説明"] = description.text.strip()
            
            # サイト固有の項目を後で抽出
            for box in result_boxes:
                title = box.find('h3', class_='title01')
                if title:
                    key = title.text.strip()
                    if key in self.NAMAEURANAI_ONLY_KEYS:
                        fortune = box.find('span', class_='f-large')
                        description = box.find('p', class_='text02')
                        
                        if fortune:
                            results[key] = fortune.text.strip()
                        if description:
                            results[f"{key}_説明"] = description.text.strip()

            return results

        except Exception as e:
            logger.error(f"namaeuranai.biz 結果の抽出中にエラーが発生: {e}")
            return {}

def create_scraper():
    return NameFortuneScraper() 