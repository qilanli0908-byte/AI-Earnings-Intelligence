
import requests
import pandas as pd
import time

# Replace with your own contact information
HEADERS = {
    "User-Agent": "EquityResearchStudent qilanli0908@gmail.com"
}


def get_cik(ticker):
    """Find a company's SEC CIK using its ticker."""

    url = "https://www.sec.gov/files/company_tickers.json"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    companies = response.json()

    for company in companies.values():
        if company["ticker"].upper() == ticker.upper():
            return str(company["cik_str"]).zfill(10)

    return None


def extract_annual(facts, tags):
    """
    Extract annual financial facts from SEC XBRL data.

    Preserve filing provenance and prioritize the supplied
    XBRL tags when multiple tags cover the same period.
    """

    records = []

    for priority, tag in enumerate(tags):

        if tag not in facts:
            continue

        entries = facts[tag].get("units", {}).get("USD", [])

        for item in entries:

            if item.get("form") != "10-K":
                continue

            if "start" not in item or "end" not in item:
                continue

            start = pd.to_datetime(item["start"])
            end = pd.to_datetime(item["end"])

            days = (end - start).days

            if not 300 <= days <= 380:
                continue

            record = item.copy()

            record["source_tag"] = tag
            record["tag_priority"] = priority

            records.append(record)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Prefer the first available tag for the same period.
    # Within that tag, retain the latest filed value.
    df = df.sort_values(
        ["tag_priority", "filed"],
        ascending=[True, False]
    )

    df = df.drop_duplicates(
        subset=["start", "end"],
        keep="first"
    )

    return df.sort_values("end").reset_index(drop=True)


def build_sec_filing_url(cik, accession_number):
    """
    Build a link to the SEC filing directory.

    Example:
    https://www.sec.gov/Archives/edgar/data/...
    """

    if not accession_number:
        return None

    cik_number = str(int(cik))

    accession_clean = accession_number.replace("-", "")

    return (
        "https://www.sec.gov/Archives/edgar/data/"
        f"{cik_number}/{accession_clean}/"
    )

def get_sec_financials(ticker):

    ticker = ticker.strip().upper()

    cik = get_cik(ticker)

    if cik is None:
        return None

    time.sleep(0.2)

    url = (
        "https://data.sec.gov/api/xbrl/companyfacts/"
        f"CIK{cik}.json"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()

    facts = data["facts"]["us-gaap"]

    revenue = extract_annual(
        facts,
        [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet"
        ]
    )

    net_income = extract_annual(
        facts,
        ["NetIncomeLoss"]
    )

    if revenue.empty or net_income.empty:
        return None
    
   
    # Preserve the original SEC source for each metric.

    rev = revenue[
        ["start", "end", "val", "filed", "accn", "source_tag"]
    ].rename(
        columns={
            "val": "Revenue",
            "filed": "Revenue Filing Date",
            "accn": "Revenue Accession",
            "source_tag": "Revenue Source Tag"
        }
    )

    net = net_income[
        ["start", "end", "val", "filed", "accn", "source_tag"]
    ].rename(
        columns={
            "val": "Net Income",
            "filed": "Net Income Filing Date",
            "accn": "Net Income Accession",
            "source_tag": "Net Income Source Tag"
        }
    )

   
    summary = pd.merge(
        rev,
        net,
        on=["start", "end"],
        how="inner"
    )


    summary = summary.drop_duplicates(
        subset=["end"],
        keep="last"
    )

    summary = summary.sort_values("end")

    summary["Revenue ($B)"] = (
        summary["Revenue"] / 1_000_000_000
    )

    summary["Net Income ($B)"] = (
        summary["Net Income"] / 1_000_000_000
    )

    summary["Revenue Growth (%)"] = (
        summary["Revenue"].pct_change() * 100
    )

    summary["Net Margin (%)"] = (
        summary["Net Income"] / summary["Revenue"] * 100
    )

   
    # Generate SEC source links for each financial metric.

    summary["Revenue SEC URL"] = summary[
        "Revenue Accession"
    ].apply(
        lambda accn: build_sec_filing_url(cik, accn)
    )

    summary["Net Income SEC URL"] = summary[
        "Net Income Accession"
    ].apply(
        lambda accn: build_sec_filing_url(cik, accn)
    )

    # Keep financial metrics and original SEC provenance.

    result = summary[
        [
            "start",
            "end",
            "Revenue ($B)",
            "Net Income ($B)",
            "Revenue Growth (%)",
            "Net Margin (%)",
            "Revenue Filing Date",
            "Revenue Accession",
            "Revenue Source Tag",
            "Revenue SEC URL",
            "Net Income Filing Date",
            "Net Income Accession",
            "Net Income Source Tag",
            "Net Income SEC URL"
        ]
    ].tail(4).copy()

    # Round only numerical financial metrics.
    numeric_columns = [
        "Revenue ($B)",
        "Net Income ($B)",
        "Revenue Growth (%)",
        "Net Margin (%)"
    ]

    result[numeric_columns] = result[numeric_columns].round(2)

    return result



# Test the function
if __name__ == "__main__":

    ticker = input("Enter ticker: ").strip().upper()

    result = get_sec_financials(ticker)

    if result is None:
        print("SEC financial data unavailable.")
    else:
        print("\n===== SEC FINANCIAL ANALYSIS =====")
        print(result.to_string(index=False))
