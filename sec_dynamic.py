
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
    """Extract annual data across multiple XBRL tags."""

    records = []

    for tag in tags:

        if tag not in facts:
            continue

        entries = facts[tag]["units"].get("USD", [])

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

            records.append(record)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    df = df.sort_values("filed")

    df = df.drop_duplicates(
        subset=["start", "end"],
        keep="last"
    )

    return df.sort_values("end")


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

    rev = revenue[["end", "val"]].rename(
        columns={"val": "Revenue"}
    )

    net = net_income[["end", "val"]].rename(
        columns={"val": "Net Income"}
    )

    summary = pd.merge(
        rev,
        net,
        on="end",
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

    result = summary[
        [
            "end",
            "Revenue ($B)",
            "Net Income ($B)",
            "Revenue Growth (%)",
            "Net Margin (%)"
        ]
    ].tail(4)

    return result.round(2)


# Test the function
if __name__ == "__main__":

    ticker = input("Enter ticker: ").strip().upper()

    result = get_sec_financials(ticker)

    if result is None:
        print("SEC financial data unavailable.")
    else:
        print("\n===== SEC FINANCIAL ANALYSIS =====")
        print(result.to_string(index=False))
