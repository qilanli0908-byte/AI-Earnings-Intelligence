
from src.thesis_models import InvestmentThesis
from src.thesis_monitor import monitor_thesis


def make_thesis(thesis_type):
    return InvestmentThesis(
        thesis_id=f"NVDA-{thesis_type.upper()}-001",
        ticker="NVDA",
        thesis_type=thesis_type,
        statement=f"Example {thesis_type} thesis.",
    )


def run_tests():
    bull = make_thesis("Bull")
    bear = make_thesis("Bear")

    cases = [
        (bull, "Improving Financial Momentum", "Potential Support"),
        (bull, "Growth Moderation - Stable Profitability", "Potential Challenge"),
        (bear, "Growth Moderation - Stable Profitability", "Potential Support"),
        (bear, "Improving Financial Momentum", "Potential Challenge"),
        (
            bull,
            "Accelerating Growth - Margin Compression",
            "Needs Review",
        ),
        (bull, "Mixed Financial Signals", "Needs Review"),
    ]

    for thesis, signal, expected in cases:
        result = monitor_thesis(thesis, signal)

        assert result.impact == expected, (
            f"{thesis.thesis_type}: {signal} "
            f"expected {expected}, got {result.impact}"
        )

        assert result.ticker == thesis.ticker
        assert result.requires_human_review is True

        print(
            f"PASS: {thesis.thesis_type} | "
            f"{signal} -> {result.impact}"
        )

    print("\nALL THESIS MONITORING TESTS PASSED")


if __name__ == "__main__":
    run_tests()
