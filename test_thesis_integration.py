
import pandas as pd

from src.thesis_models import InvestmentThesis
from src.thesis_integration import (
    get_latest_financial_signal,
    monitor_company_theses,
)


def make_thesis(ticker, thesis_type):
    return InvestmentThesis(
        thesis_id=f"{ticker}-{thesis_type.upper()}-001",
        ticker=ticker,
        thesis_type=thesis_type,
        statement=f"Example {thesis_type} thesis.",
    )


def run_tests():
    # Deliberately unordered rows to test chronological sorting.
    financial_changes = pd.DataFrame(
        [
            {
                "end": "2026-01-25",
                "Research Signal": "Growth Moderation - Stable Profitability",
            },
            {
                "end": "2025-01-26",
                "Research Signal": "Improving Financial Momentum",
            },
        ]
    )

    latest = get_latest_financial_signal(financial_changes)

    assert latest == "Growth Moderation - Stable Profitability"
    print("PASS: Latest fiscal-year signal selected")

    bull = make_thesis("NVDA", "Bull")
    bear = make_thesis("NVDA", "Bear")

    results = monitor_company_theses(
        ticker="NVDA",
        theses=[bull, bear],
        financial_changes=financial_changes,
    )

    assert len(results) == 2
    assert results[0].impact == "Potential Challenge"
    assert results[1].impact == "Potential Support"

    print("PASS: Bull/Bear monitoring integration")

    amd = make_thesis("AMD", "Bull")

    try:
        monitor_company_theses(
            ticker="NVDA",
            theses=[amd],
            financial_changes=financial_changes,
        )
    except ValueError:
        print("PASS: Cross-company thesis rejected")
    else:
        raise AssertionError("Ticker mismatch was not rejected")

    try:
        get_latest_financial_signal(pd.DataFrame())
    except ValueError:
        print("PASS: Empty financial data rejected")
    else:
        raise AssertionError("Empty data was accepted")

    print("\nALL THESIS INTEGRATION TESTS PASSED")


if __name__ == "__main__":
    run_tests()
