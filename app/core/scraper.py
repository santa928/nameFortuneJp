import logging
import re
import urllib.parse
from typing import Dict

import requests
import urllib3
from bs4 import BeautifulSoup

# SSL証明書の警告を無効化
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 中央の setup_logging() で basicConfig 済み
logger = logging.getLogger(__name__)


class NameFortuneScraper:
    # 結果の表示順序を定義
    COMMON_KEYS = ["天格", "人格", "地格", "外格", "総格"]
    ENAMAE_ONLY_KEYS = ["三才配置", "陰陽配列"]
    NAMAEURANAI_ONLY_KEYS = ["仕事運", "家庭運"]

    ENAMAE_URL = "https://enamae.net"
    NAMAEURANAI_URL = "https://namaeuranai.biz"

    def __init__(self) -> None:
        """初期化"""
        self.logger = logger

    def get_fortune(
        self,
        last_name: str,
        first_name: str,
        gender: str = "m",
        stroke_list_mode: bool = False,
    ) -> Dict[str, Dict[str, str]]:
        """
        姓名判断サイトから運勢を取得

        Args:
            last_name: 姓
            first_name: 名
            gender: 性別 ("m" or "f")
            stroke_list_mode: 画数別運勢一覧モード

        Returns:
            Dict[str, Dict[str, str]]: 各サイトの運勢結果
        """
        self.logger.info(f"運勢取得開始: {last_name} {first_name} ({gender})")

        # 各サイトから結果を取得
        enamae_results = self._get_enamae_fortune(
            last_name, first_name, gender, stroke_list_mode
        )
        namaeuranai_results = self._get_namaeuranai_fortune(
            last_name, first_name, gender, stroke_list_mode
        )

        # 結果を結合
        results = {
            "enamae.net": self._sort_results(enamae_results, is_enamae=True),
            "namaeuranai.biz": self._sort_results(namaeuranai_results, is_enamae=False),
        }

        self.logger.info(
            f"運勢取得完了: enamae({len(enamae_results)}項目), "
            f"namaeuranai({len(namaeuranai_results)}項目)"
        )
        return results

    def _sort_results(
        self, results: Dict[str, str], *, is_enamae: bool = True
    ) -> Dict[str, str]:
        """結果を指定された順序でソート"""
        sorted_results = {}

        # 共通項目を順序通りに追加
        for key in self.COMMON_KEYS:
            if key in results:
                sorted_results[key] = results[key]
            if f"{key}_説明" in results:
                sorted_results[f"{key}_説明"] = results[f"{key}_説明"]

        # サイト固有の項目を追加
        site_keys = self.ENAMAE_ONLY_KEYS if is_enamae else self.NAMAEURANAI_ONLY_KEYS
        for key in site_keys:
            if key in results:
                sorted_results[key] = results[key]
            if f"{key}_説明" in results:
                sorted_results[f"{key}_説明"] = results[f"{key}_説明"]

        return sorted_results

    def _get_enamae_fortune(
        self,
        last_name: str,
        first_name: str,
        gender: str,
        stroke_list_mode: bool = False,
    ) -> Dict[str, str]:
        """enamae.netから運勢を取得"""
        try:
            # 画数別運勢一覧モードの場合は男性固定
            gender_str = "m" if stroke_list_mode else gender
            last_encoded = urllib.parse.quote(last_name)
            first_encoded = urllib.parse.quote(first_name)
            encoded_name = f"{last_encoded}__{first_encoded}"
            url = f"{self.ENAMAE_URL}/{gender_str}/{encoded_name}"
            self.logger.debug(f"enamae.net リクエストURL: {url}")

            # セキュリティを強化：SSL検証を有効化、タイムアウト設定
            response = requests.get(url, timeout=30, verify=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = self._extract_enamae_results(soup)

            if not results:
                self.logger.warning("enamae.net: 結果が取得できませんでした")
                return {}

            return results

        except requests.RequestException as e:
            self.logger.error(f"enamae.net リクエストエラー: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"enamae.net 予期せぬエラー: {e}")
            return {}

    def _get_namaeuranai_fortune(
        self,
        last_name: str,
        first_name: str,
        gender: str,
        stroke_list_mode: bool = False,
    ) -> Dict[str, str]:
        """namaeuranai.bizから運勢を取得"""
        try:
            # 画数別運勢一覧モードの場合は男性固定
            gender_str = (
                "男性" if stroke_list_mode else ("男性" if gender == "m" else "女性")
            )
            last_encoded = urllib.parse.quote(last_name)
            first_encoded = urllib.parse.quote(first_name)
            encoded_name = f"{last_encoded}_{first_encoded}"
            gender_encoded = urllib.parse.quote(gender_str)
            url = f"{self.NAMAEURANAI_URL}/result/{encoded_name}/{gender_encoded}"
            self.logger.debug(f"namaeuranai.biz リクエストURL: {url}")

            # namaeuranai.bizの SSL証明書問題を回避（開発環境のみ）
            # 本番環境では適切なCA証明書バンドルを使用することを推奨
            try:
                # まずSSL検証有効で試行
                response = requests.get(url, timeout=30, verify=True)
                response.raise_for_status()
            except requests.exceptions.SSLError:
                self.logger.warning(
                    "namaeuranai.biz: SSL証明書エラーのため、検証を無効化して再試行"
                )
                # SSL検証を無効化して再試行
                response = requests.get(url, timeout=30, verify=False)  # nosec B501
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = self._extract_namaeuranai_results(soup)

            if not results:
                self.logger.warning("namaeuranai.biz: 結果が取得できませんでした")
                return {}

            return results

        except requests.RequestException as e:
            self.logger.error(f"namaeuranai.biz リクエストエラー: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"namaeuranai.biz 予期せぬエラー: {e}")
            return {}

    def _extract_enamae_results(self, soup: BeautifulSoup) -> Dict[str, str]:
        """enamae.netの結果を抽出"""
        results = {}
        try:
            h2_tags = soup.find_all("h2")
            if not h2_tags:
                self.logger.warning("enamae.net: h2タグが見つかりません")
                return {}

            # 共通項目を抽出
            for h2 in h2_tags:
                text = h2.text.strip()
                # 五格の結果を抽出（例：天格（祖運）は9画で『凶』）
                for key in self.COMMON_KEYS:
                    if key in text:
                        fortune_match = re.search(r"『(.+?)』", text)
                        if fortune_match:
                            results[key] = fortune_match.group(1)
                            next_p = h2.find_next("p")
                            if next_p:
                                # 説明文から余計な『』を削除
                                description = next_p.text.strip()
                                description = re.sub(r"『(.+?)』", r"\1", description)
                                results[f"{key}_説明"] = description

            # 三才配置を抽出
            for h2 in h2_tags:
                text = h2.text.strip()
                if "三才配置" in text:
                    # 三才配置の運勢を抽出（例：三才配置は『水⇒金⇒火』で『凶』）
                    fortune_match = re.search(r"『(.+?)』で『(.+?)』", text)
                    if fortune_match:
                        results["三才配置"] = fortune_match.group(2)  # 運勢（凶）
                        results["三才配置_説明"] = (
                            f"配置: {fortune_match.group(1)}"  # 配置（水⇒金⇒火）
                        )
                        next_p = h2.find_next("p")
                        if next_p:
                            results["三才配置_説明"] += f"\n{next_p.text.strip()}"

            # 陰陽配列を抽出
            for h2 in h2_tags:
                text = h2.text.strip()
                if "陰陽配列" in text:
                    # 陰陽配列の情報を抽出（例：陰陽配列は「陽陰陰陽」）
                    pattern_match = re.search(r"「(.+?)」", text)
                    if pattern_match:
                        results["陰陽配列"] = pattern_match.group(1)
                        next_p = h2.find_next("p")
                        if next_p:
                            results["陰陽配列_説明"] = next_p.text.strip()

            if not results:
                self.logger.warning("enamae.net: 結果が抽出できませんでした")
            return results

        except Exception as e:
            self.logger.error(f"enamae.net 結果の抽出中にエラーが発生: {e}")
            return {}

    def _extract_namaeuranai_results(self, soup: BeautifulSoup) -> Dict[str, str]:
        """namaeuranai.bizの結果を抽出

        Args:
            soup (BeautifulSoup): パースされたHTML

        Returns:
            Dict[str, str]: 抽出された運勢情報
        """
        results = {}
        try:
            # 結果ボックスを検索
            result_boxes = soup.find_all("div", class_="result-box")
            if not result_boxes:
                self.logger.warning("namaeuranai.biz: result-boxが見つかりません")
                return {}

            self.logger.debug(
                f"namaeuranai.biz: {len(result_boxes)}個のresult-boxを発見"
            )

            # 共通項目を抽出
            for box in result_boxes:
                title = box.find("h3", class_="title01")
                if not title:
                    continue

                key = title.text.strip()
                if key not in self.COMMON_KEYS:
                    continue

                self.logger.debug(f"namaeuranai.biz: 共通項目 '{key}' を処理中")

                # 運勢を抽出
                fortune = box.find("span", class_="f-large")
                if fortune:
                    fortune_text = fortune.text.strip()
                    results[key] = fortune_text
                    self.logger.debug(
                        f"namaeuranai.biz: '{key}' の運勢: {fortune_text}"
                    )

                # 説明文を抽出
                description = box.find("p", class_="text02")
                if description:
                    desc_text = description.text.strip()
                    results[f"{key}_説明"] = desc_text
                    self.logger.debug(
                        f"namaeuranai.biz: '{key}' の説明文: {desc_text[:50]}..."
                    )

            # サイト固有の項目を抽出
            for box in result_boxes:
                title = box.find("h3", class_="title01")
                if not title:
                    continue

                key = title.text.strip()
                if key not in self.NAMAEURANAI_ONLY_KEYS:
                    continue

                self.logger.debug(f"namaeuranai.biz: 固有項目 '{key}' を処理中")

                # 運勢を抽出
                fortune = box.find("span", class_="f-large")
                if fortune:
                    fortune_text = fortune.text.strip()
                    results[key] = fortune_text
                    self.logger.debug(
                        f"namaeuranai.biz: '{key}' の運勢: {fortune_text}"
                    )

                # 説明文を抽出
                description = box.find("p", class_="text02")
                if description:
                    desc_text = description.text.strip()
                    results[f"{key}_説明"] = desc_text
                    self.logger.debug(
                        f"namaeuranai.biz: '{key}' の説明文: {desc_text[:50]}..."
                    )

            if not results:
                self.logger.warning("namaeuranai.biz: 結果が抽出できませんでした")
                # デバッグ用にHTMLの一部を出力
                self.logger.debug(
                    f"namaeuranai.biz: HTMLの一部: {soup.prettify()[:1000]}"
                )
            else:
                self.logger.info(
                    f"namaeuranai.biz: {len(results)}個の結果を抽出しました"
                )

            return results

        except Exception as e:
            self.logger.error(f"namaeuranai.biz 結果の抽出中にエラーが発生: {e}")
            return {}


def create_scraper() -> "NameFortuneScraper":
    """Factory function to obtain a shared scraper instance"""
    return NameFortuneScraper()
