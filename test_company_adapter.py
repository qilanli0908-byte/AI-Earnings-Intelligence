
import pandas as pd

from src.company_adapter import (
    build_company_identity,
    build_financial_overview,
    build_filing_sources,
    validate_sec_url,
)


# ----------------------------------------
# 1. SEC Company Identity
# ----------------------------------------

submissions = {
    "name": "NVIDIA CORPORATION",
    "cik": 1045810,
    "tickers": ["NVDA"],
    "exchanges": ["Nasdaq"],
    "sicDescription": "Semiconductors & Related Devices",
}

identity = build_company_identity(
    "nvda",
    submissions,
)

assert identity.ticker == "NVDA"
assert identity.company_name == "NVIDIA CORPORATION"
assert identity.cik == "0001045810"
assert identity.exchange == "Nasdaq"

print("PASS: SEC company identity mapped.")


# ----------------------------------------
# 2. Financial Overview
# ----------------------------------------

financial_df = pd.DataFrame([
    {
        "end": "2025-01-26",
        "Revenue ($B)": 100.0,
        "Net Income ($B)": 50.0,
        "Revenue Growth (%)": 100.0,
        "Net Margin (%)": 50.0,
    },
    {
        "end": "2026-01-25",
        "Revenue ($B)": 200.0,
        "Net Income ($B)": 110.0,
        "Revenue Growth (%)": 65.47,
        "Net Margin (%)": 55.60,
    },
])

overview = build_financial_overview(
    financial_df
)

assert overview.fiscal_year_end == "2026-01-25"
assert overview.revenue_billions == 200.0
assert overview.net_income_billions == 110.0
assert overview.revenue_growth_pct == 65.47

print("PASS: Latest SEC financial overview mapped.")


# ----------------------------------------
# 3. Filing Sources
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
    },
    {
        "form": "10-Q",
        "filingDate": "2026-05-01",
        "reportDate": "2026-04-01",
        "accessionNumber": "0000000000-26-000002",
        "Document URL": (
            "https://www.sec.gov/Archives/"
            "edgar/data/1045810/test2.htm"
        ),
    },
])

sources = build_filing_sources(
    filings_df
)

assert len(sources) == 1
assert sources[0].form == "10-K"
assert sources[0].fiscal_year_end == "2026-01-25"
assert sources[0].accession_number == (
    "0000000000-26-000001"
)

print("PASS: SEC 10-K filing sources mapped.")
print("PASS: Non-10-K filing excluded.")


# ----------------------------------------
# 4. Missing Data
# ----------------------------------------

assert build_financial_overview(
    pd.DataFrame()
) is None

assert build_filing_sources(
    pd.DataFrame()
) == []

print("PASS: Missing data handled.")


# ----------------------------------------
# 5. Source URL Validation
# ----------------------------------------

assert validate_sec_url(
    "https://www.sec.gov/example"
) == "https://www.sec.gov/example"

try:
    validate_sec_url(
        "https://www.sec.gov.evil.example/file"
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "Invalid SEC domain was not rejected."
    )

print("PASS: SEC source URL validation.")


print("\nALL COMPANY ADAPTER TESTS PASSED.")
