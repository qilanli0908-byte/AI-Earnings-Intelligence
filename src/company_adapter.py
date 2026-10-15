
import math
from urllib.parse import urlparse

import pandas as pd

from src.company_models import (
    CompanyIdentity,
    CompanyFinancialOverview,
    FilingSource,
)


def optional_text(value):
    """Return clean text, or None for missing values."""

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    result = str(value).strip()

    if not result or result.lower() in (
        "nan", "none", "nat"
    ):
        return None

    return result


def optional_number(value):
    """Return a finite float, or None."""

    if value is None:
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(result):
        return None

    return result


def normalize_cik(value):
    """Preserve the SEC's standard 10-digit CIK format."""

    text = optional_text(value)

    if text is None:
        return None

    if not text.isdigit():
        raise ValueError("SEC CIK must contain digits only.")

    return text.zfill(10)


def validate_sec_url(value):
    """
    Accept an official SEC HTTPS URL only.

    Missing URLs remain None.
    Unexpected URLs are rejected rather than displayed.
    """

    url = optional_text(value)

    if url is None:
        return None

    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or parsed.hostname not in (
            "www.sec.gov",
            "sec.gov",
            "data.sec.gov",
        )
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(
            f"Unexpected SEC source URL: {url}"
        )

    return url


def build_company_identity(ticker, submissions):
    """
    Build company identity from SEC Submissions metadata.
    No company information is invented.
    """

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker cannot be empty.")

    if not isinstance(submissions, dict):
        raise TypeError(
            "SEC submissions must be a dictionary."
        )

    sec_tickers = submissions.get("tickers", [])

    if sec_tickers and ticker not in [
        str(item).upper() for item in sec_tickers
    ]:
        raise ValueError(
            "Selected ticker does not match SEC submissions."
        )

    exchanges = submissions.get("exchanges") or []

    exchange = None

    if ticker in [
        str(item).upper() for item in sec_tickers
    ]:
        index = [
            str(item).upper() for item in sec_tickers
        ].index(ticker)

        if index < len(exchanges):
            exchange = optional_text(exchanges[index])

    return CompanyIdentity(
        ticker=ticker,
        company_name=(
            optional_text(submissions.get("name"))
            or "Name Unavailable"
        ),
        cik=normalize_cik(submissions.get("cik")),
        exchange=exchange,
        industry=optional_text(
            submissions.get("sicDescription")
        ),
    )


def build_financial_overview(financial_df):
    """
    Build the latest annual financial overview from
    the existing get_sec_financials() DataFrame.
    """

    if financial_df is None or financial_df.empty:
        return None

    required_columns = [
        "end",
        "Revenue ($B)",
        "Net Income ($B)",
        "Revenue Growth (%)",
        "Net Margin (%)",
    ]

    missing = [
        column
        for column in required_columns
        if column not in financial_df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing SEC financial columns: {missing}"
        )

    latest = (
        financial_df
        .sort_values("end")
        .iloc[-1]
    )

    fiscal_year_end = optional_text(latest["end"])

    if fiscal_year_end is None:
        raise ValueError(
            "Latest financial period has no end date."
        )

    # Pandas Timestamp -> YYYY-MM-DD
    fiscal_year_end = pd.to_datetime(
        fiscal_year_end
    ).strftime("%Y-%m-%d")

    return CompanyFinancialOverview(
        fiscal_year_end=fiscal_year_end,
        revenue_billions=optional_number(
            latest["Revenue ($B)"]
        ),
        net_income_billions=optional_number(
            latest["Net Income ($B)"]
        ),
        revenue_growth_pct=optional_number(
            latest["Revenue Growth (%)"]
        ),
        net_margin_pct=optional_number(
            latest["Net Margin (%)"]
        ),
    )


def build_filing_sources(filings_df):
    """
    Convert get_recent_10k_with_urls() output
    into structured FilingSource objects.

    The SEC reportDate is used as fiscal_year_end.
    """

    if filings_df is None or filings_df.empty:
        return []

    required_columns = [
        "form",
        "filingDate",
        "reportDate",
        "accessionNumber",
        "Document URL",
    ]

    missing = [
        column
        for column in required_columns
        if column not in filings_df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing SEC filing columns: {missing}"
        )

    sources = []

    for _, row in filings_df.iterrows():

        form = optional_text(row["form"])

        if form != "10-K":
            continue

        filing_date = optional_text(
            row["filingDate"]
        )

        accession = optional_text(
            row["accessionNumber"]
        )

        sec_url = validate_sec_url(
            row["Document URL"]
        )

        # Do not create a filing source if essential
        # provenance fields are missing.
        if not all((
            filing_date,
            accession,
            sec_url,
        )):
            continue

        sources.append(
            FilingSource(
                form=form,
                filing_date=filing_date,
                accession_number=accession,
                sec_url=sec_url,
                fiscal_year_end=optional_text(
                    row["reportDate"]
                ),
            )
        )

    return sorted(
        sources,
        key=lambda item: item.filing_date,
        reverse=True,
    )
