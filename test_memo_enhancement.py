
from io import BytesIO

from reportlab.pdfbase import pdfdoc
from src.brief_builder import build_research_brief
from src.brief_evidence import check_brief_evidence
from src.brief_integrity import validate_brief_integrity
from src.memo_export import export_investment_memo

from src.thesis_models import (
    InvestmentThesis,
    ThesisHypothesis,
)

from test_brief_builder import make_profile


def build_test_memo(ticker="NVDA"):
    profile = make_profile()

    thesis = InvestmentThesis(
        thesis_id="NVDA-BULL-TEST",
        ticker="NVDA",
        thesis_type="Bull",
        statement=(
            "AI infrastructure spending may support "
            "future revenue growth."
        ),
        hypotheses=[
            ThesisHypothesis(
                description=(
                    "AI infrastructure demand remains strong."
                )
            )
        ],
    )

    brief = build_research_brief(
        profile=profile,
        theses=[thesis],
        monitoring_results=[],
    )

    # A saved thesis requires a matching monitoring result.
    # This fixture intentionally supplies no monitoring results,
    # so it must be rejected by the builder.


def run_tests():
    profile = make_profile()

    thesis = InvestmentThesis(
        thesis_id="NVDA-BULL-TEST",
        ticker="NVDA",
        thesis_type="Bull",
        statement="AI demand may support future growth.",
        hypotheses=[
            ThesisHypothesis(
                description="Future demand remains strong."
            )
        ],
    )

    from src.thesis_monitor import monitor_thesis

    monitoring = monitor_thesis(
        thesis,
        "Growth Moderation - Stable Profitability",
    )

    brief = build_research_brief(
        profile=profile,
        theses=[thesis],
        monitoring_results=[monitoring],
    )

    thesis_section = next(
        section for section in brief.sections
        if section.title == "Investment Theses"
    )

    assert "Core Statement:" in thesis_section.summary
    assert "Supporting Evidence:" in thesis_section.summary
    assert "Hypothesis Details:" in thesis_section.summary
    assert "Research Limitation:" in thesis_section.summary

    print("PASS: Structured thesis content")

    brief = check_brief_evidence(brief)

    report = validate_brief_integrity(
        brief,
        expected_ticker="NVDA",
    )

    assert report.passed, report.errors

    pdf_bytes = export_investment_memo(brief, report)

    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000

    from pathlib import Path

    Path("memo_enhanced_preview.pdf").write_bytes(pdf_bytes)

    print("PASS: Enhanced PDF generated")

    print("\nALL MEMO ENHANCEMENT TESTS PASSED")


if __name__ == "__main__":
    run_tests()
