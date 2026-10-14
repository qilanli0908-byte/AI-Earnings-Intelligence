
from src.filing_retrieval import get_recent_10k_with_urls


tickers = ["NVDA", "AMD"]

for ticker in tickers:

    print(f"\n========== {ticker} 10-K DOCUMENT URL TEST ==========")

    filings = get_recent_10k_with_urls(ticker, limit=2)

    columns = [
        "filingDate",
        "reportDate",
        "accessionNumber",
        "primaryDocument",
        "Document URL"
    ]

    print(filings[columns].to_string(index=False))

    assert len(filings) == 2, (
        f"Expected two filings for {ticker}."
    )

    assert filings["Document URL"].str.startswith(
        "https://www.sec.gov/Archives/edgar/data/"
    ).all()

    print(f"\nPASS: Direct 10-K URLs generated for {ticker}.")
