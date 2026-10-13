
import requests
import pandas as pd

# NVIDIA SEC identifier
cik = "0001045810"

url = (
    "https://data.sec.gov/api/xbrl/companyfacts/"
    f"CIK{cik}.json"
)

# Replace with your actual contact email
headers = {
    "User-Agent": "EquityResearchStudent qilanli0908@gmail.com"
}

response = requests.get(
    url,
    headers=headers,
    timeout=30
)

response.raise_for_status()
data = response.json()

print("Company:", data["entityName"])

# Access US GAAP financial data
facts = data["facts"]["us-gaap"]


# Function: extract annual financial data

def get_annual_data(tags):

    all_records = []

    # Check every possible financial tag
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

            # Keep full-year reporting periods
            if not 300 <= days <= 380:
                continue

            record = item.copy()
            record["source_tag"] = tag

            all_records.append(record)

    if not all_records:
        return pd.DataFrame()

    df = pd.DataFrame(all_records)

    # Prefer the latest filing for each reporting period
    df = df.sort_values("filed")

    df = df.drop_duplicates(
        subset=["start", "end"],
        keep="last"
    )

    df = df.sort_values("end")

    return df


# 1. Revenue
revenue = get_annual_data([
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues"
])

# 2. Net Income
net_income = get_annual_data([
    "NetIncomeLoss"
])


# Display results
def display_results(name, df):

    print(f"\n===== {name} =====")

    if df.empty:
        print("Data unavailable.")
        return

    result = df[["end", "val", "accn"]].copy()

    result["Value ($B)"] = (
        result["val"] / 1_000_000_000
    )

    result = result.tail(4)

    print(
        result[["end", "Value ($B)", "accn"]]
        .round(2)
        .to_string(index=False)
    )


display_results("ANNUAL REVENUE", revenue)

display_results("ANNUAL NET INCOME", net_income)
