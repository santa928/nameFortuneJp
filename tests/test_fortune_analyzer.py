import unittest

from app.core.fortune_analyzer import FortuneAnalyzer


class TestFortuneAnalyzer(unittest.TestCase):
    """FortuneAnalyzerのテスト"""

    def setUp(self) -> None:
        self.analyzer = FortuneAnalyzer()

    def test_calculate_enamae_score(self) -> None:
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
                "expected": 91.67,
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
                "expected": 60.0,
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
                "expected": 85.0,
            },
        ]
        for case in test_cases:
            score = self.analyzer._calculate_enamae_score(case["input"])  # type: ignore
            self.assertAlmostEqual(score, case["expected"], places=1)  # type: ignore

    def test_calculate_namaeuranai_score(self) -> None:
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
                "expected": 90.0,
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
                "expected": 52.86,
            },
        ]
        for case in test_cases:
            score = self.analyzer._calculate_namaeuranai_score(case["input"])  # type: ignore
            self.assertAlmostEqual(score, case["expected"], places=1)  # type: ignore

    def test_calculate_total_score_uses_both_available_providers(self) -> None:
        result = {
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
        }
        self.assertAlmostEqual(self.analyzer._calculate_total_score(result), 90.83, places=1)

    def test_calculate_total_score_does_not_treat_missing_provider_as_zero(self) -> None:
        result = {
            "enamae": {
                "天格": "大吉",
                "人格": "吉",
                "地格": "特殊格",
                "外格": "大吉",
                "総格": "吉",
                "三才配置": "大吉",
            },
            "namaeuranai": {},
        }
        expected = self.analyzer._calculate_enamae_score(result["enamae"])
        self.assertAlmostEqual(self.analyzer._calculate_total_score(result), expected)

    def test_calculate_total_score_is_zero_when_all_providers_are_missing(self) -> None:
        self.assertEqual(
            self.analyzer._calculate_total_score({"enamae": {}, "namaeuranai": {}}),
            0,
        )

    def test_analyzer_initialization(self) -> None:
        analyzer = FortuneAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertIsNotNone(analyzer.scraper)
        self.assertIsNotNone(analyzer.pattern_generator)


if __name__ == "__main__":
    unittest.main()
