
import pandas as pd

from src.research_models import ResearchAssessment

from src.signal_integration import (
    safe_float,
    build_financial_signal,
    build_disclosure_signals,
    integrate_company_signals,
)


# ----------------------------------------
# 1. Financial test data
# ----------------------------------------

financial_df = pd.DataFrame([
    {
        "end": "2025-01-26",
        "Revenue Growth (%)": 114.20,
        "Growth Change (pp)": -11.65,
        "Growth Trend": "Decelerating Growth",
        "Net Margin (%)": 55.85,
        "Margin Change (pp)": 7.00,
        "Margin Trend": "Margin Expansion",
        "Research Signal": (
            "Growth Moderation - Margin Improvement"
        ),
    },
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
    },
])


# ----------------------------------------
# 2. Disclosure test data
# ----------------------------------------

def make_assessment(
    ticker,
    label,
    significance,
    priority,
):

    old_text = f"Old disclosure about {label}."
    new_text = f"Updated disclosure about {label}."

    return ResearchAssessment(
        ticker=ticker,
        section="Item 1A - Risk Factors",
        change_type="Revised",
        old_disclosure=old_text,
        new_disclosure=new_text,
        significance=significance,
        research_priority=priority,
        evidence=[new_text],
        rationale=f"Assessment for {label}.",
        research_questions=[
            f"What should be investigated about {label}?"
        ],
        model_name="offline-test",
    )


assessments = [
    make_assessment(
        "NVDA", "Acquisitions", "Low", "Low"
    ),
    make_assessment(
        "NVDA", "Supply Chain", "High", "High"
    ),
    make_assessment(
        "NVDA", "Competition", "Medium", "Medium"
    ),
    make_assessment(
        "AMD", "Product Demand", "High", "High"
    ),
]


# ----------------------------------------
# 3. Integration tests
# ----------------------------------------

company = integrate_company_signals(
    ticker="NVDA",
    financial_changes=financial_df,
    assessments=assessments,
)

assert company.ticker == "NVDA"

assert company.financial is not None

assert company.financial.fiscal_year_end == "2026-01-25"

assert company.financial.revenue_growth == 65.47

assert company.financial.growth_trend == (
    "Decelerating Growth"
)

print("PASS: Latest financial signal integrated.")


assert company.disclosure_count == 3

assert company.high_priority_count == 1
assert company.medium_priority_count == 1
assert company.low_priority_count == 1

assert [
    item.research_priority
    for item in company.disclosures
] == [
    "High",
    "Medium",
    "Low",
]

print("PASS: Disclosure signals ranked correctly.")


assert all(
    item.ticker == "NVDA"
    for item in company.disclosures
)

print("PASS: Other-company assessments excluded.")


assert company.overall_research_status == (
    "High Research Priority"
)

print("PASS: Overall research status calculated.")


# ----------------------------------------
# 4. Missing-data tests
# ----------------------------------------

assert safe_float(float("nan")) is None

assert safe_float(float("inf")) is None

assert safe_float(None) is None

assert build_financial_signal(
    "NVDA",
    pd.DataFrame(),
) is None

empty_company = integrate_company_signals(
    ticker="NVDA",
    financial_changes=pd.DataFrame(),
    assessments=[],
)

assert empty_company.financial is None

assert empty_company.disclosure_count == 0

assert empty_company.overall_research_status == (
    "Not Assessed"
)

print("PASS: Missing financial and disclosure data handled.")
