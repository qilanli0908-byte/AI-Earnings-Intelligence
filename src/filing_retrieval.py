import pandas as pd
import requests

from sec_dynamic import get_cik, HEADERS


def get_company_submissions(ticker):
    """
    Retrieve a company's SEC filing history.

    Returns the SEC Submissions API response as a dictionary.
    """

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker cannot be empty.")

    # Convert ticker to its 10-digit SEC CIK.
    cik = get_cik(ticker)

    if not cik:
        raise ValueError(f"CIK not found for ticker: {ticker}")

    # SEC official Submissions API.
    url = (
        f"https://data.sec.gov/submissions/"
        f"CIK{cik}.json"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_recent_10k_filings(ticker, limit=2):
    """
    Retrieve the most recent annual 10-K filings.

    Parameters:
        ticker: Stock ticker, e.g. NVDA
        limit: Number of 10-K filings to return

    Returns:
        A pandas DataFrame.
    """

    submissions = get_company_submissions(ticker)

    recent = submissions["filings"]["recent"]

    filings = pd.DataFrame(recent)

    # Keep annual 10-K filings only.
    annual_filings = filings[
        filings["form"] == "10-K"
    ].copy()

    # Most recent filing first.
    annual_filings = annual_filings.sort_values(
        "filingDate",
        ascending=False
    )

    columns = [
        "form",
        "filingDate",
        "reportDate",
        "accessionNumber",
        "primaryDocument"
    ]

    return annual_filings[columns].head(limit).reset_index(drop=True)

def build_filing_document_url(cik, accession_number, primary_document):
    """
    Build the direct SEC URL for a filing's primary document.
    """

    cik = str(int(cik))

    accession_clean = accession_number.replace("-", "")

    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik}/{accession_clean}/{primary_document}"
    )


def get_recent_10k_with_urls(ticker, limit=2):
    """
    Retrieve recent 10-K filings and attach direct document URLs.
    """

    filings = get_recent_10k_filings(ticker, limit=limit)

    cik = get_cik(ticker.strip().upper())

    filings["Document URL"] = filings.apply(
        lambda row: build_filing_document_url(
            cik,
            row["accessionNumber"],
            row["primaryDocument"]
        ),
        axis=1
    )

    return filings

from pathlib import Path
import time


def download_10k(ticker, filing, output_dir="data/filings"):
    """
    Download one SEC 10-K primary document.

    Parameters:
        ticker: Company ticker.
        filing: One row from get_recent_10k_with_urls().
        output_dir: Local folder for downloaded filings.

    Returns:
        Path to the saved document.
    """

    ticker = ticker.strip().upper()

    url = filing["Document URL"]

    # Create the destination folder if necessary.
    folder = Path(output_dir) / ticker
    folder.mkdir(parents=True, exist_ok=True)

    # Use accession number to create a unique filename.
    accession = filing["accessionNumber"].replace("-", "")

    filename = f"{ticker}_{accession}_10K.html"

    filepath = folder / filename

    # Avoid downloading the same document repeatedly.
    if filepath.exists() and filepath.stat().st_size > 0:
        print(f"Already downloaded: {filepath}")
        return filepath

    # Respectful request pacing for SEC servers.
    time.sleep(0.3)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    # Basic validation: do not save an empty response.
    if not response.content:
        raise ValueError(
            f"SEC returned an empty document: {url}"
        )

    # The primary document is normally HTML, but check
    # its actual response type before saving it as HTML.
    content_type = response.headers.get(
        "Content-Type", ""
    ).lower()

    if (
        "html" not in content_type
        and "xhtml" not in content_type
    ):
        raise ValueError(
            f"Unexpected document type: {content_type}"
        )

    filepath.write_bytes(response.content)

    print(f"Downloaded: {filepath}")
    print(f"File size: {filepath.stat().st_size:,} bytes")

    return filepath



def ensure_recent_10k_downloaded(ticker, limit=2, output_dir="data/filings"):
    """Download recent annual filings into a ticker-specific directory.

    Raises if SEC lists fewer than the requested number; existing files are reused.
    Does not call any paid AI API.
    """
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer.")
    ticker = ticker.strip().upper()
    filings = get_recent_10k_with_urls(ticker, limit=limit)
    if len(filings) < limit:
        raise ValueError(f"SEC lists only {len(filings)} recent 10-K(s) for {ticker}; {limit} required.")
    paths = []
    # Download older filing first; comparison still sorts accession filenames.
    for _, filing in filings.iloc[::-1].iterrows():
        paths.append(download_10k(ticker, filing, output_dir=output_dir))
    return paths
