
import pandas as pd

# Read financial summary
df = pd.read_csv(
    "NVDA_financial_summary.csv",
    index_col=0
)

# Remove years without revenue data
df = df.dropna(subset=["Revenue ($B)"])

# Sort financial years
df.index = pd.to_datetime(df.index)
df = df.sort_index()

# Get latest and previous year
latest = df.iloc[-1]
previous = df.iloc[-2]

latest_year = df.index[-1].year
previous_year = df.index[-2].year

# Get financial metrics
revenue = latest["Revenue ($B)"]
revenue_growth = latest["Revenue Growth (%)"]

gross_margin = latest["Gross Margin (%)"]
previous_gross_margin = previous["Gross Margin (%)"]

net_margin = latest["Net Margin (%)"]

# Analyze revenue growth
if revenue_growth > 20:
    growth_comment = "strong revenue growth"

elif revenue_growth > 5:
    growth_comment = "moderate revenue growth"

elif revenue_growth >= 0:
    growth_comment = "relatively stable revenue"

else:
    growth_comment = "a decline in revenue"


# Analyze gross margin trend
margin_change = gross_margin - previous_gross_margin

if margin_change > 1:
    margin_comment = "Gross margin improved"

elif margin_change < -1:
    margin_comment = "Gross margin declined"

else:
    margin_comment = "Gross margin remained relatively stable"


# Generate commentary
print("\n===== FINANCIAL PERFORMANCE COMMENTARY =====")

print(
    f"In FY{latest_year}, the company reported "
    f"revenue of ${revenue:.2f} billion, "
    f"representing {revenue_growth:.2f}% year-over-year growth."
)

print(
    f"This indicates {growth_comment}."
)

print(
    f"{margin_comment} from "
    f"{previous_gross_margin:.2f}% in FY{previous_year} "
    f"to {gross_margin:.2f}% in FY{latest_year}."
)

print(
    f"The company reported a net profit margin "
    f"of {net_margin:.2f}%."
)

print("==========================================")
