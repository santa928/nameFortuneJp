import unittest
from fortune_analyzer import FortuneAnalyzer

class TestFortuneAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = FortuneAnalyzer()

    def test_calculate_enamae_score(self):
        """enamae.netのスコア計算をテスト"""
        test_cases = [
            {
                "input": {"総合運": "大吉", "恋愛運": "吉", "仕事運": "特殊格"},
                "expected": 90.0  # (100 + 80 + 90) / 3
            },
            {
                "input": {"総合運": "凶", "金運": "大凶", "仕事運": "吉"},
                "expected": 46.67  # (40 + 20 + 80) / 3
            },
            {
                "input": {"総合運": "吉凶混合", "健康運": "吉", "仕事運": "大吉"},
                "expected": 80.0  # (60 + 80 + 100) / 3
            }
        ]

        for case in test_cases:
            score = self.analyzer._calculate_enamae_score(case["input"])
            self.assertAlmostEqual(score, case["expected"], places=2,
                msg=f"enamae score failed for input {case['input']}")

    def test_calculate_namaeuranai_score(self):
        """namaeuranai.bizのスコア計算をテスト"""
        test_cases = [
            {
                "input": {"総合運": "大大吉", "恋愛運": "大吉", "仕事運": "吉"},
                "expected": 90.0  # (100 + 90 + 80) / 3
            },
            {
                "input": {"総合運": "凶", "金運": "大凶", "仕事運": "吉"},
                "expected": 46.67  # (40 + 20 + 80) / 3
            },
            {
                "input": {"総合運": "大吉", "健康運": "吉", "仕事運": "大大吉"},
                "expected": 90.0  # (90 + 80 + 100) / 3
            }
        ]

        for case in test_cases:
            score = self.analyzer._calculate_namaeuranai_score(case["input"])
            self.assertAlmostEqual(score, case["expected"], places=2,
                msg=f"namaeuranai score failed for input {case['input']}")

    def test_calculate_total_score(self):
        """総合スコアの計算をテスト"""
        test_cases = [
            {
                "input": {
                    "enamae": {"総合運": "大吉", "恋愛運": "吉", "仕事運": "特殊格"},
                    "namaeuranai": {"総合運": "大大吉", "恋愛運": "大吉", "仕事運": "吉"}
                },
                "expected": 90.0  # (90.0 + 90.0) / 2
            },
            {
                "input": {
                    "enamae": {"総合運": "凶", "金運": "大凶", "仕事運": "吉"},
                    "namaeuranai": {"総合運": "凶", "金運": "大凶", "仕事運": "吉"}
                },
                "expected": 46.67  # (46.67 + 46.67) / 2
            }
        ]

        for case in test_cases:
            score = self.analyzer._calculate_total_score({
                "enamae": case["input"]["enamae"],
                "namaeuranai": case["input"]["namaeuranai"]
            })
            self.assertAlmostEqual(score, case["expected"], places=2,
                msg=f"total score failed for input {case['input']}")

if __name__ == '__main__':
    unittest.main() 