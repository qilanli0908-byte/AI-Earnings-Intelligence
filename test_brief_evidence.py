
from src.brief_models import (
    BriefEvidence,
    BriefSection,
    ResearchBrief,
)
from src.brief_evidence import (
    is_sec_url,
    check_brief_evidence,
)


def run_tests():

    assert is_sec_url(
        "https://www.sec.gov/Archives/example"
    )

    assert not is_sec_url(
        "https://example.com/report"
    )

    assert not is_sec_url(
        "https://www.sec.gov.evil.com/report"
    )

    print("PASS: SEC URL validation")

    brief = ResearchBrief(
        ticker="NVDA",
        company_name="NVIDIA CORP",
        fiscal_year_end="2026-01-25",
        sections=[
            BriefSection(
                title="SEC Filing Sources",
                summary="Illustrative filing source.",
                evidence=[
                    BriefEvidence(
                        description="Example filing.",
                        evidence_type="SEC Filing",
                        verification_status="Verified",
                        source_url=(
                            "https://www.sec.gov/Archives/example"
                        ),
                        citation="Illustrative test citation",
                    )
                ],
            )
        ],
    )

    checked = check_brief_evidence(brief)

    assert (
        checked.sections[0].evidence[0].verification_status
        == "Requires Review"
    )

    assert checked.requires_human_review is True

    print("PASS: Evidence not automatically Verified")
    print("PASS: Human review preserved")

    print("\nALL BRIEF EVIDENCE TESTS PASSED")


if __name__ == "__main__":
    run_tests()
