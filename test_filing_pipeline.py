
from src.filing_retrieval import (
    get_recent_10k_with_urls,
    download_10k
)


tickers = ["NVDA", "AMD"]

for ticker in tickers:

    print(f"\n========== {ticker} FILING PIPELINE TEST ==========")

    # Retrieve the two most recent annual filings.
    filings = get_recent_10k_with_urls(
        ticker,
        limit=2
    )

    assert len(filings) == 2, (
        f"Expected two 10-K filings for {ticker}."
    )

    # Download and verify each document.
    for _, filing in filings.iterrows():

        print("\n------------------------------")
        print("Ticker:", ticker)
        print("Filing Date:", filing["filingDate"])
        print("Report Date:", filing["reportDate"])
        print("Accession:", filing["accessionNumber"])

        saved_path = download_10k(
            ticker,
            filing
        )

        assert saved_path.exists(), (
            f"Downloaded file not found: {saved_path}"
        )

        assert saved_path.stat().st_size > 0, (
            f"Downloaded file is empty: {saved_path}"
        )

        print("Verified:", saved_path)

    print(f"\nPASS: Two 10-K documents verified for {ticker}.")


print("\nALL FILING PIPELINE TESTS PASSED.")
