
from src.thesis_models import (
    InvestmentThesis,
    ThesisEvidence,
    ThesisHypothesis,
)


def test_investment_thesis():
    thesis = InvestmentThesis(
        thesis_id="NVDA-BULL-001",
        ticker="NVDA",
        thesis_type="Bull",
        statement=(
            "AI infrastructure spending will sustain NVIDIA's "
            "growth over the next three years."
        ),
        evidence=[
            ThesisEvidence(
                description="NVIDIA reported historical revenue growth.",
                source_url="https://www.sec.gov/",
                status="Verified",
                citation="Placeholder for a specific SEC filing citation",
            )
        ],
        hypotheses=[
            ThesisHypothesis(
                description="AI infrastructure demand will remain strong."
            )
        ],
    )

    assert thesis.ticker == "NVDA"
    assert thesis.thesis_type == "Bull"
    assert thesis.evidence[0].status == "Verified"
    assert thesis.hypotheses[0].status == "Unverified"
    assert thesis.requires_human_review is True
    assert thesis.created_at
    assert thesis.updated_at

    print("PASS: Investment Thesis model")


if __name__ == "__main__":
    test_investment_thesis()
