
import pandas as pd

# Read the financial statement
df = pd.read_csv(
    "NVDA_income_statement.csv",
    index_col=0
)

# Display available financial metrics
print("Available financial metrics:")
print(df.index.tolist())

# Get financial data
revenue = df.loc["Total Revenue"]
gross_profit = df.loc["Gross Profit"]
net_income = df.loc["Net Income"]

# Convert data to numbers
revenue = pd.to_numeric(revenue, errors="coerce")
gross_profit = pd.to_numeric(gross_profit, errors="coerce")
net_income = pd.to_numeric(net_income, errors="coerce")

# Calculate financial ratios
gross_margin = gross_profit / revenue * 100
net_margin = net_income / revenue * 100

# Revenue growth (oldest to newest)
revenue_growth = revenue.pct_change(fill_method=None) * 100

# Create a summary table
summary = pd.DataFrame({
    "Revenue ($B)": revenue / 1_000_000_000,
    "Gross Margin (%)": gross_margin,
    "Net Margin (%)": net_margin,
    "Revenue Growth (%)": revenue_growth
})

# Sort financial years chronologically
summary.index = pd.to_datetime(summary.index)
summary = summary.sort_index()

# Recalculate growth in chronological order
summary["Revenue Growth (%)"] = (
    summary["Revenue ($B)"].pct_change(fill_method=None) * 100
)

summary.index = summary.index.strftime("%Y-%m-%d")

print("\n===== FINANCIAL PERFORMANCE SUMMARY =====")
print(summary.round(2).to_string())

# Save the report
summary.to_csv("NVDA_financial_summary.csv")

print("\nFinancial analysis completed successfully!")
