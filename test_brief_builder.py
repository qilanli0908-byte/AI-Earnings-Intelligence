from src.signal_models import CompanyResearchSignals, FinancialSignal
from src.brief_builder import build_research_brief
from src.company_models import (
    CompanyIdentity,
    CompanyFinancialOverview,
    CompanyProfile,
)
from src.thesis_models import (
    InvestmentThesis,
    ThesisEvidence,
)
from src.thesis_monitor import monitor_thesis


def make_profile():
    return CompanyProfile(
        identity=CompanyIdentity(
            ticker="NVDA",
            company_name="NVIDIA CORP",
            cik="0001045810",
            exchange="Nasdaq",
            industry="Semiconductors",
        ),
        financial=CompanyFinancialOverview(
            fiscal_year_end="2026-01-25",
            revenue_billions=215.94,
            net_income_billions=120.07,
            revenue_growth_pct=65.47,
            net_margin_pct=55.60,
        ),

        research_signals=CompanyResearchSignals(
            ticker="NVDA",
            financial=FinancialSignal(
                ticker="NVDA",
                fiscal_year_end="2026-01-25",
                revenue_growth=65.47,
                growth_change_pp=-48.73,
                growth_trend="Decelerating Growth",
                net_margin=55.60,
                margin_change_pp=-0.25,
                margin_trend="Stable Margin",
                research_signal="Growth Moderation - Stable Profitability",
                source="SEC Company Facts",
            ),
            disclosures=[],
        ),

        filing_sources=[],
        research_summary="Existing research summary.",
        requires_human_review=True,
    )


def run_tests():
    profile = make_profile()

    thesis = InvestmentThesis(
        thesis_id="NVDA-BULL-001",
        ticker="NVDA",
        thesis_type="Bull",
        statement="AI infrastructure spending may sustain growth.",
        evidence=[
            ThesisEvidence(
                description="Example historical SEC evidence.",
                source_url="https://www.sec.gov/",
                status="Verified",
                citation="Illustrative test citation",
            )
        ],
    )

    monitoring = monitor_thesis(
        thesis,
        "Growth Moderation - Stable Profitability",
    )

    brief = build_research_brief(
        profile=profile,
        theses=[thesis],
        monitoring_results=[monitoring],
    )

    assert brief.ticker == "NVDA"
    assert len(brief.sections) == 6
    assert brief.requires_human_review is True

    titles = [section.title for section in brief.sections]

    assert "Financial Momentum" in titles
    assert "Investment Theses" in titles
    assert "Thesis Monitoring" in titles

    thesis_section = next(
        section
        for section in brief.sections
        if section.title == "Investment Theses"
    )

    assert (
        thesis_section.evidence[0].verification_status
        == "Requires Review"
    )

    print("PASS: Company profile integrated")
    print("PASS: Thesis and monitoring integrated")
    print("PASS: Evidence not automatically promoted to Verified")

    wrong_company = InvestmentThesis(
        thesis_id="AMD-BULL-001",
        ticker="AMD",
        thesis_type="Bull",
        statement="Example AMD thesis.",
    )

    try:
        build_research_brief(
            profile=profile,
            theses=[wrong_company],
            monitoring_results=[],
        )
    except ValueError:
        print("PASS: Cross-company thesis rejected")
    else:
        raise AssertionError("Cross-company thesis was accepted")

    print("\nALL BRIEF BUILDER TESTS PASSED")


if __name__ == "__main__":
    run_tests()
