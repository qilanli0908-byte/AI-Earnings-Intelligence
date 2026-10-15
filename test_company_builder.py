
import pandas as pd

from src.company_builder import build_company_profile
from src.research_models import ResearchAssessment


# ----------------------------------------
# 1. Simulated SEC identity
# ----------------------------------------

submissions = {
    "name": "NVIDIA CORPORATION",
    "cik": 1045810,
    "tickers": ["NVDA"],
    "exchanges": ["Nasdaq"],
    "sicDescription": "Semiconductors & Related Devices",
}


# ----------------------------------------
# 2. Simulated SEC financial data
# ----------------------------------------

financial_df = pd.DataFrame([
    {
        "end": "2026-01-25",
        "Revenue ($B)": 200.0,
        "Net Income ($B)": 110.0,
        "Revenue Growth (%)": 65.47,
        "Net Margin (%)": 55.60,
    }
])

financial_changes = pd.DataFrame([
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


# ----------------------------------------
# 3. Simulated SEC filing sources
# ----------------------------------------

filings_df = pd.DataFrame([
    {
        "form": "10-K",
        "filingDate": "2026-02-25",
        "reportDate": "2026-01-25",
        "accessionNumber": "0000000000-26-000001",
        "Document URL": (
            "https://www.sec.gov/Archives/"
            "edgar/data/1045810/test.htm"
        ),
    }
])


# ----------------------------------------
# 4. Validated disclosure assessment
# ----------------------------------------

assessment = ResearchAssessment(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure=(
        "Old disclosure about supply chain."
    ),
    new_disclosure=(
        "Updated disclosure about supply chain."
    ),
    significance="Medium",
    research_priority="High",
    evidence=[
        "Updated disclosure about supply chain."
    ],
    rationale=(
        "The revised wording merits further research."
    ),
    research_questions=[
        "What changed in the supply chain disclosure?"
    ],
    model_name="offline-test",
)


# ----------------------------------------
# 5. Build complete Company Profile
# ----------------------------------------

profile = build_company_profile(
    ticker="NVDA",
    submissions=submissions,
    financial_df=financial_df,
    financial_changes=financial_changes,
    filings_df=filings_df,
    assessments=[assessment],
    total_changes=3,
)

assert profile.identity.ticker == "NVDA"
assert profile.identity.cik == "0001045810"

print("PASS: SEC company identity integrated.")


assert profile.financial is not None
assert profile.financial.revenue_growth_pct == 65.47

print("PASS: Financial overview integrated.")


assert len(profile.filing_sources) == 1
assert profile.filing_sources[0].form == "10-K"

print("PASS: SEC filing provenance preserved.")


assert profile.research_signals is not None
assert profile.research_signals.disclosure_count == 1
assert profile.research_signals.high_priority_count == 1

print("PASS: Day 9 research signals integrated.")


assert "1 of 3" in profile.research_summary
assert "no causal relationship" in (
    profile.research_summary
)

print("PASS: Deterministic research summary generated.")


assert profile.requires_human_review is True

print("PASS: Human review requirement preserved.")


# ----------------------------------------
# 6. Missing-data behavior
# ----------------------------------------

empty_profile = build_company_profile(
    ticker="NVDA",
    submissions=submissions,
    financial_df=pd.DataFrame(),
    financial_changes=pd.DataFrame(),
    filings_df=pd.DataFrame(),
    assessments=[],
    total_changes=0,
)

assert empty_profile.financial is None
assert empty_profile.filing_sources == []
assert empty_profile.research_signals.disclosure_count == 0
assert "Financial overview is unavailable." in (
    empty_profile.research_summary
)

print("PASS: Missing-data scenario handled.")


# ----------------------------------------
# 7. Invalid assessment count
# ----------------------------------------

try:
    build_company_profile(
        ticker="NVDA",
        submissions=submissions,
        financial_df=financial_df,
        financial_changes=financial_changes,
        filings_df=filings_df,
        assessments=[assessment],
        total_changes=0,
    )

except ValueError:
    print("PASS: Invalid assessment count rejected.")

else:
    raise AssertionError(
        "Builder accepted an invalid assessment count."
    )


print("\nALL COMPANY BUILDER TESTS PASSED.")
