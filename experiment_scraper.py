import logging
from bs4 import BeautifulSoup
import requests
import urllib3

# SSL証明書の警告を無効化
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def experiment():
    """enamae.netのスクレイピング実験"""
    print("\n=== enamae.netのスクレイピング実験 ===")
    url = "https://enamae.net/m/%E7%94%B0%E4%B8%AD__%E5%A4%AA%E9%83%8E"
    response = requests.get(url, verify=False)
    
    print("\n=== レスポンスステータス ===")
    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンスヘッダー: {dict(response.headers)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    print("\n=== HTMLの構造 ===")
    print(f"title: {soup.title.text if soup.title else 'なし'}")
    
    h2_tags = soup.find_all('h2')
    print(f"\n=== 見つかったh2タグ: {len(h2_tags)}個 ===")
    
    for i, h2 in enumerate(h2_tags, 1):
        print(f"\n[{i}番目のh2タグ]")
        print(f"テキスト: {h2.text.strip()}")
        print(f"親要素: {h2.parent.name}")
        next_p = h2.find_next('p')
        if next_p:
            print(f"説明文: {next_p.text.strip()}")
        else:
            print("説明文なし")

if __name__ == "__main__":
    experiment() 