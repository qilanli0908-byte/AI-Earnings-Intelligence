
import pandas as pd

from sec_financials import revenue, net_income


# Prepare revenue data
rev = revenue[["end", "val"]].copy()

rev = rev.rename(
    columns={"val": "Revenue"}
)

# Prepare net income data
net = net_income[["end", "val"]].copy()

net = net.rename(
    columns={"val": "Net Income"}
)

# Merge both datasets by fiscal year end
summary = pd.merge(
    rev,
    net,
    on="end",
    how="inner"
)

# Remove duplicate reporting periods
summary = summary.drop_duplicates(
    subset=["end"],
    keep="last"
)

summary = summary.sort_values("end")

# Convert USD into billions
summary["Revenue ($B)"] = (
    summary["Revenue"] / 1_000_000_000
)

summary["Net Income ($B)"] = (
    summary["Net Income"] / 1_000_000_000
)

# Calculate year-over-year revenue growth
summary["Revenue Growth (%)"] = (
    summary["Revenue"].pct_change() * 100
)

# Calculate net profit margin
summary["Net Margin (%)"] = (
    summary["Net Income"] / summary["Revenue"] * 100
)

# Display results
result = summary[
    [
        "end",
        "Revenue ($B)",
        "Net Income ($B)",
        "Revenue Growth (%)",
        "Net Margin (%)"
    ]
].tail(4)

print("\n===== SEC FINANCIAL ANALYSIS =====")

print(
    result.round(2).to_string(index=False)
)

# Save results
result.to_csv(
    "NVDA_SEC_financial_analysis.csv",
    index=False
)

print("\nSEC financial analysis saved successfully!")

print("\n===== DATA COVERAGE CHECK =====")

print("Revenue latest date:")
print(revenue["end"].max())

print("Net Income latest date:")
print(net_income["end"].max())
