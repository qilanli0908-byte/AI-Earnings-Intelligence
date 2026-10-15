
from src.brief_models import (
    BriefEvidence,
    BriefSection,
    ResearchBrief,
)


def run_tests():
    evidence = BriefEvidence(
        description="Historical revenue data from SEC filing.",
        evidence_type="SEC Financial",
        verification_status="Unverified",
        source_url="https://www.sec.gov/",
        citation="Illustrative test citation only",
    )

    section = BriefSection(
        title="Financial Momentum",
        summary="Historical financial performance summary.",
        evidence=[evidence],
    )

    brief = ResearchBrief(
        ticker="NVDA",
        company_name="NVIDIA CORP",
        fiscal_year_end="2026-01-25",
        sections=[section],
    )

    assert brief.ticker == "NVDA"
    assert brief.company_name == "NVIDIA CORP"
    assert len(brief.sections) == 1

    assert brief.sections[0].title == "Financial Momentum"
    assert brief.sections[0].evidence[0].evidence_type == "SEC Financial"

    assert (
        brief.sections[0].evidence[0].verification_status
        == "Unverified"
    )

    assert brief.requires_human_review is True
    assert brief.sections[0].requires_human_review is True
    assert brief.generated_at

    print("PASS: Research Brief models")
    print("PASS: Evidence metadata")
    print("PASS: Human review defaults")
    print("\nALL BRIEF MODEL TESTS PASSED")


if __name__ == "__main__":
    run_tests()
