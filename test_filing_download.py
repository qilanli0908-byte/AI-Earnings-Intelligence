
from src.filing_retrieval import (
    get_recent_10k_with_urls,
    download_10k
)


ticker = "NVDA"

print(f"\n========== {ticker} 10-K DOWNLOAD TEST ==========")

# Retrieve the latest annual filing.
filings = get_recent_10k_with_urls(
    ticker,
    limit=1
)

assert not filings.empty, "No 10-K filing found."

latest_filing = filings.iloc[0]

print("Filing Date:", latest_filing["filingDate"])
print("Report Date:", latest_filing["reportDate"])
print("Document URL:", latest_filing["Document URL"])

# Download the actual filing document.
saved_path = download_10k(
    ticker,
    latest_filing
)

assert saved_path.exists(), "Downloaded file does not exist."

assert saved_path.stat().st_size > 0, "Downloaded file is empty."

print("\nPASS: SEC 10-K successfully downloaded.")
print("Saved to:", saved_path)
