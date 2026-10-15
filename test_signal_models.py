
from src.signal_models import (
    FinancialSignal,
    DisclosureSignal,
    CompanyResearchSignals,
)


financial = FinancialSignal(
    ticker="NVDA",
    fiscal_year_end="2026-01-25",
    revenue_growth=65.47,
    growth_change_pp=-48.73,
    growth_trend="Decelerating Growth",
    net_margin=55.60,
    margin_change_pp=-0.25,
    margin_trend="Stable Margin",
    research_signal="Growth Moderation - Stable Profitability",
)

disclosure = DisclosureSignal(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    significance="Low",
    research_priority="Low",
    evidence=[
        "Additional risks related to acquisitions include"
    ],
    rationale="Minor editorial wording change.",
)

company = CompanyResearchSignals(
    ticker="NVDA",
    financial=financial,
    disclosures=[disclosure],
    disclosure_count=1,
    low_priority_count=1,
    overall_research_status="Low Priority",
)

assert company.ticker == "NVDA"

assert company.financial.growth_trend == (
    "Decelerating Growth"
)

assert company.financial.margin_trend == (
    "Stable Margin"
)

assert len(company.disclosures) == 1

assert company.disclosures[0].research_priority == "Low"

assert company.high_priority_count == 0
assert company.low_priority_count == 1

assert company.disclosures[0].requires_human_review is True

print("PASS: FinancialSignal model created.")
print("PASS: DisclosureSignal model created.")
print("PASS: CompanyResearchSignals model created.")
print("PASS: Financial and disclosure signals coexist.")
