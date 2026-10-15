
from src.brief_builder import build_research_brief
from src.brief_evidence import check_brief_evidence
from src.brief_integrity import validate_brief_integrity
from src.thesis_models import InvestmentThesis, ThesisHypothesis
from src.thesis_monitor import monitor_thesis

# Reuse the existing offline Company Profile fixture.
from test_brief_builder import make_profile


def run_tests():
    profile = make_profile()

    thesis = InvestmentThesis(
        thesis_id="NVDA-BULL-001",
        ticker="NVDA",
        thesis_type="Bull",
        statement=(
            "AI infrastructure spending may sustain "
            "NVIDIA's growth over the next three years."
        ),
        hypotheses=[
            ThesisHypothesis(
                description="Future AI demand remains strong."
            )
        ],
    )

    # 1. Existing thesis -> monitoring
    monitoring = monitor_thesis(
        thesis,
        "Growth Moderation - Stable Profitability",
    )

    assert monitoring.impact == "Potential Challenge"
    print("PASS: Thesis monitoring")

    # 2. Company Profile + Thesis -> Research Brief
    brief = build_research_brief(
        profile=profile,
        theses=[thesis],
        monitoring_results=[monitoring],
    )

    assert brief.ticker == "NVDA"
    assert len(brief.sections) == 6

    print("PASS: Research Brief integration")

    # 3. Evidence metadata checks
    brief = check_brief_evidence(brief)

    assert brief.requires_human_review is True

    print("PASS: Evidence review preserved")

    # 4. Final integrity validation
    report = validate_brief_integrity(
        brief=brief,
        expected_ticker="NVDA",
    )

    assert report.passed is True, report.errors
    assert len(report.errors) == 0
    assert len(report.warnings) == 2

    print("PASS: Complete NVDA research pipeline")

    # 5. Cross-company protection
    wrong_company = validate_brief_integrity(
        brief=brief,
        expected_ticker="AMD",
    )

    assert wrong_company.passed is False
    assert any(
        "Company mismatch" in error
        for error in wrong_company.errors
    )

    print("PASS: NVDA/AMD company isolation")

    # 6. Empty thesis state
    empty_brief = build_research_brief(
        profile=profile,
        theses=[],
        monitoring_results=[],
    )

    empty_brief = check_brief_evidence(empty_brief)

    empty_report = validate_brief_integrity(
        brief=empty_brief,
        expected_ticker="NVDA",
    )

    assert empty_report.passed is True
    assert len(empty_brief.sections) == 6

    print("PASS: Empty thesis state")

    print("\nALL END-TO-END INTEGRATION TESTS PASSED")


if __name__ == "__main__":
    run_tests()
