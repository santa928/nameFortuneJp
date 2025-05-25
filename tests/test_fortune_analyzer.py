import unittest

from app.core.fortune_analyzer import FortuneAnalyzer


class TestFortuneAnalyzer(unittest.TestCase):
    """FortuneAnalyzerのテスト"""

    def setUp(self) -> None:
        """テスト前の準備"""
        self.analyzer = FortuneAnalyzer()

    def test_calculate_enamae_score(self) -> None:
        """enamae.netのスコア計算をテスト"""
        test_cases = [
            {
                "input": {
                    "天格": "大吉",
                    "人格": "吉",
                    "地格": "特殊格",
                    "外格": "大吉",
                    "総格": "吉",
                    "三才配置": "大吉",
                },
                "expected": 91.67,  # (100 + 80 + 90 + 100 + 80 + 100) / 6 = 91.66666...
            },
            {
                "input": {
                    "天格": "凶",
                    "人格": "大凶",
                    "地格": "吉",
                    "外格": "凶",
                    "総格": "大吉",
                    "三才配置": "吉",
                },
                "expected": 60.0,  # (40 + 20 + 80 + 40 + 100 + 80) / 6 = 60.0
            },
            {
                "input": {
                    "天格": "吉凶混合",
                    "人格": "吉",
                    "地格": "大吉",
                    "外格": "特殊格",
                    "総格": "大吉",
                    "三才配置": "吉",
                },
                "expected": 85.0,  # (60 + 80 + 100 + 90 + 100 + 80) / 6 = 85.0
            },
        ]

        for case in test_cases:
            score = self.analyzer._calculate_enamae_score(case["input"])  # type: ignore
            expected = case["expected"]
            self.assertAlmostEqual(score, expected, places=1)  # type: ignore

    def test_calculate_namaeuranai_score(self) -> None:
        """namaeuranai.bizのスコア計算をテスト"""
        test_cases = [
            {
                "input": {
                    "天格": "大大吉",
                    "人格": "大吉",
                    "地格": "吉",
                    "外格": "大吉",
                    "総格": "吉",
                    "仕事運": "大大吉",
                    "家庭運": "大吉",
                },
                "expected": 90.0,  # (100 + 90 + 80 + 90 + 80 + 100 + 90) / 7 = 90.0
            },
            {
                "input": {
                    "天格": "凶",
                    "人格": "大凶",
                    "地格": "吉",
                    "外格": "凶",
                    "総格": "大吉",
                    "仕事運": "吉",
                    "家庭運": "大凶",
                },
                "expected": 52.86,  # 実際のスコア: 52.857142857142854
            },
            {
                "input": {
                    "天格": "大吉",
                    "人格": "吉",
                    "地格": "大大吉",
                    "外格": "大吉",
                    "総格": "吉",
                    "仕事運": "大吉",
                    "家庭運": "大大吉",
                },
                "expected": 90.0,  # 実際のスコア: 90.0
            },
        ]

        for case in test_cases:
            score = self.analyzer._calculate_namaeuranai_score(case["input"])  # type: ignore
            expected = case["expected"]
            self.assertAlmostEqual(score, expected, places=1)  # type: ignore

    def test_calculate_total_score(self) -> None:
        """総合スコアの計算をテスト"""
        test_cases = [
            {
                "input": {
                    "enamae": {
                        "天格": "大吉",
                        "人格": "吉",
                        "地格": "特殊格",
                        "外格": "大吉",
                        "総格": "吉",
                        "三才配置": "大吉",
                    },
                    "namaeuranai": {
                        "天格": "大大吉",
                        "人格": "大吉",
                        "地格": "吉",
                        "外格": "大吉",
                        "総格": "吉",
                        "仕事運": "大大吉",
                        "家庭運": "大吉",
                    },
                },
                "expected": 90.83,  # (91.67 + 90.0) / 2 = 90.835
            },
            {
                "input": {
                    "enamae": {
                        "天格": "凶",
                        "人格": "大凶",
                        "地格": "吉",
                        "外格": "凶",
                        "総格": "大吉",
                        "三才配置": "吉",
                    },
                    "namaeuranai": {
                        "天格": "凶",
                        "人格": "大凶",
                        "地格": "吉",
                        "外格": "凶",
                        "総格": "大吉",
                        "仕事運": "吉",
                        "家庭運": "大凶",
                    },
                },
                "expected": 56.43,  # (60.0 + 52.86) / 2 = 56.43
            },
        ]

        for case in test_cases:
            score = self.analyzer._calculate_total_score(case["input"])  # type: ignore
            expected = case["expected"]
            self.assertAlmostEqual(score, expected, places=1)  # type: ignore

    def test_analyzer_initialization(self) -> None:
        """FortuneAnalyzerの初期化をテスト"""
        analyzer = FortuneAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertIsNotNone(analyzer.scraper)
        self.assertIsNotNone(analyzer.pattern_generator)


if __name__ == "__main__":
    unittest.main()
