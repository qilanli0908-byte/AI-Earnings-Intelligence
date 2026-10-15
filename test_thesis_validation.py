
from src.thesis_models import (
    InvestmentThesis,
    ThesisEvidence,
    ThesisHypothesis,
)
from src.thesis_validation import validate_thesis


def expect_invalid(thesis, label):
    try:
        validate_thesis(thesis)
    except ValueError:
        print(f"PASS: {label}")
    else:
        raise AssertionError(f"Expected validation failure: {label}")


def run_tests():
    valid = InvestmentThesis(
        thesis_id="NVDA-BULL-001",
        ticker="NVDA",
        thesis_type="Bull",
        statement="AI infrastructure spending may support growth.",
        evidence=[
            ThesisEvidence(
                description="Historical revenue reported in SEC filing.",
                source_url="https://www.sec.gov/Archives/example",
                status="Verified",
                citation="Illustrative test citation only",
            )
        ],
        hypotheses=[
            ThesisHypothesis(
                description="AI demand remains strong."
            )
        ],
    )

    validate_thesis(valid)
    print("PASS: Valid thesis structure")

    missing_citation = InvestmentThesis(
        thesis_id="NVDA-BULL-002",
        ticker="NVDA",
        thesis_type="Bull",
        statement="Example thesis.",
        evidence=[
            ThesisEvidence(
                description="Example evidence.",
                source_url="https://www.sec.gov/",
                status="Verified",
                citation="",
            )
        ],
    )

    expect_invalid(
        missing_citation,
        "Verified evidence without citation rejected",
    )

    external_source = InvestmentThesis(
        thesis_id="NVDA-BULL-003",
        ticker="NVDA",
        thesis_type="Bull",
        statement="Example thesis.",
        evidence=[
            ThesisEvidence(
                description="Example evidence.",
                source_url="https://example.com/report",
                status="Verified",
                citation="Example",
            )
        ],
    )

    expect_invalid(
        external_source,
        "Non-SEC URL rejected for Verified SEC evidence",
    )

    invalid_ticker = InvestmentThesis(
        thesis_id="INVALID-001",
        ticker="../NVDA",
        thesis_type="Bull",
        statement="Example thesis.",
    )

    expect_invalid(
        invalid_ticker,
        "Invalid ticker rejected",
    )

    print("\nALL THESIS VALIDATION TESTS PASSED")


if __name__ == "__main__":
    run_tests()
