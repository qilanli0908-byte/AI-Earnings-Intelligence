
import unittest
import pandas as pd

from src.change_detector import (
    calculate_financial_changes,
    classify_growth_trend,
    classify_margin_trend,
    generate_research_signal
)


class TestFinancialChangeDetector(unittest.TestCase):

    def test_growth_acceleration(self):
        result = classify_growth_trend(34.34, 20.65)
        self.assertEqual(result, "Accelerating Growth")

    def test_growth_deceleration(self):
        result = classify_growth_trend(65.47, -48.73)
        self.assertEqual(result, "Decelerating Growth")

    def test_revenue_contraction(self):
        result = classify_growth_trend(-3.90, -47.51)
        self.assertEqual(result, "Revenue Contraction")

    def test_stable_growth(self):
        result = classify_growth_trend(10.0, 0.5)
        self.assertEqual(result, "Stable Growth")

    def test_missing_growth_data(self):
        result = classify_growth_trend(float("nan"), 2.0)
        self.assertEqual(result, "Insufficient Data")

    def test_margin_expansion(self):
        result = classify_margin_trend(6.15)
        self.assertEqual(result, "Margin Expansion")

    def test_margin_compression(self):
        result = classify_margin_trend(-1.82)
        self.assertEqual(result, "Margin Compression")

    def test_stable_margin(self):
        result = classify_margin_trend(-0.25)
        self.assertEqual(result, "Stable Margin")

    def test_improving_financial_momentum(self):
        result = generate_research_signal(
            "Accelerating Growth",
            "Margin Expansion"
        )
        self.assertEqual(
            result,
            "Improving Financial Momentum"
        )

    def test_growth_moderation(self):
        result = generate_research_signal(
            "Decelerating Growth",
            "Stable Margin"
        )
        self.assertEqual(
            result,
            "Growth Moderation — Stable Profitability"
        )

    def test_revenue_and_profitability_deterioration(self):
        result = generate_research_signal(
            "Revenue Contraction",
            "Margin Compression"
        )
        self.assertEqual(
            result,
            "Revenue and Profitability Deterioration"
        )

    def test_full_calculation(self):

        # Synthetic data: no SEC API required.
        sample = pd.DataFrame({
            "end": ["2024-12-31", "2025-12-31"],
            "Revenue Growth (%)": [10.0, 20.0],
            "Net Margin (%)": [5.0, 8.0]
        })

        result = calculate_financial_changes(sample)

        self.assertAlmostEqual(
            result.iloc[1]["Growth Change (pp)"],
            10.0
        )

        self.assertAlmostEqual(
            result.iloc[1]["Margin Change (pp)"],
            3.0
        )

        self.assertEqual(
            result.iloc[1]["Research Signal"],
            "Improving Financial Momentum"
        )


if __name__ == "__main__":
    unittest.main()
