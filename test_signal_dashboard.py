
from unittest.mock import patch

import pandas as pd

from src.research_models import ResearchAssessment
from src.signal_dashboard import (
    load_current_disclosure_assessments,
    build_company_dashboard_data,
)


def make_assessment(ticker, label, priority):

    old_text = f"Old disclosure about {label}."
    new_text = f"Updated disclosure about {label}."

    return ResearchAssessment(
        ticker=ticker,
        section="Item 1A - Risk Factors",
        change_type="Revised",
        old_disclosure=old_text,
        new_disclosure=new_text,
        significance=priority,
        research_priority=priority,
        evidence=[new_text],
        rationale=f"Assessment for {label}.",
        research_questions=[
            f"What should be investigated about {label}?"
        ],
        model_name="offline-test",
    )


nvda_assessment = make_assessment(
    "NVDA",
    "Supply Chain",
    "High",
)

wording_changes = [
    {
        "old": nvda_assessment.old_disclosure,
        "new": nvda_assessment.new_disclosure,
    },
    {
        "old": "Old disclosure about Competition.",
        "new": "Updated disclosure about Competition.",
    },
]


def fake_load_assessment(
    ticker,
    section,
    change_type,
    old_disclosure,
    new_disclosure,
):
    if (
        ticker == "NVDA"
        and old_disclosure == nvda_assessment.old_disclosure
        and new_disclosure == nvda_assessment.new_disclosure
    ):
        return nvda_assessment

    return None


financial_df = pd.DataFrame([
    {
        "end": "2026-01-25",
        "Revenue Growth (%)": 65.47,
        "Growth Change (pp)": -48.73,
        "Growth Trend": "Decelerating Growth",
        "Net Margin (%)": 55.60,
        "Margin Change (pp)": -0.25,
        "Margin Trend": "Stable Margin",
        "Research Signal": (
            "Growth Moderation - Stable Profitability"
        ),
    }
])


with patch(
    "src.signal_dashboard.load_assessment",
    side_effect=fake_load_assessment,
):

    assessments = load_current_disclosure_assessments(
        ticker="NVDA",
        wording_changes=wording_changes,
    )

    assert len(assessments) == 1

    print("PASS: Current disclosure cache loaded.")


    dashboard = build_company_dashboard_data(
        ticker="NVDA",
        financial_changes=financial_df,
        wording_changes=wording_changes,
    )

    assert dashboard["total_changes"] == 2
    assert dashboard["assessed_count"] == 1
    assert dashboard["not_assessed_count"] == 1

    company = dashboard["company"]

    assert company.ticker == "NVDA"
    assert company.financial is not None
    assert company.disclosure_count == 1
    assert company.high_priority_count == 1

    print("PASS: Financial and disclosure data integrated.")
    print("PASS: Assessed and unassessed counts are correct.")


    amd_dashboard = build_company_dashboard_data(
        ticker="AMD",
        financial_changes=pd.DataFrame(),
        wording_changes=wording_changes,
    )

    assert amd_dashboard["company"].disclosure_count == 0
    assert amd_dashboard["company"].financial is None

    print("PASS: NVDA assessment excluded from AMD.")
    print("PASS: No API calls required.")
