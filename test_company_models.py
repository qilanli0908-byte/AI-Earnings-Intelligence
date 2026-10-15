
from src.company_models import (
    CompanyIdentity,
    FilingSource,
    CompanyFinancialOverview,
    CompanyProfile,
)

from src.signal_models import CompanyResearchSignals


identity = CompanyIdentity(
    ticker="NVDA",
    company_name="NVIDIA Corporation",
)

assert identity.ticker == "NVDA"
assert identity.cik is None

print("PASS: CompanyIdentity created.")


financial = CompanyFinancialOverview(
    fiscal_year_end="2026-01-25",
    revenue_billions=130.5,
    net_income_billions=72.9,
    revenue_growth_pct=65.47,
    net_margin_pct=55.60,
)

assert financial.revenue_growth_pct == 65.47

print("PASS: CompanyFinancialOverview created.")


filing = FilingSource(
    form="10-K",
    filing_date="2026-02-01",
    accession_number="TEST-ACCESSION",
    sec_url="https://www.sec.gov/",
)

assert filing.form == "10-K"

print("PASS: FilingSource created.")


signals = CompanyResearchSignals(
    ticker="NVDA",
    overall_research_status="Low Research Priority",
)

profile = CompanyProfile(
    identity=identity,
    financial=financial,
    research_signals=signals,
    filing_sources=[filing],
    research_summary="Offline model test.",
)

assert profile.identity.ticker == "NVDA"
assert profile.research_signals is signals
assert len(profile.filing_sources) == 1
assert profile.requires_human_review is True

print("PASS: CompanyProfile assembled.")
print("PASS: Day 9 signals reused successfully.")
