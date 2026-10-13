
import yfinance as yf

print("Welcome to AI Equity Research Copilot!")

ticker = input("Enter a stock ticker: ").strip().upper()

stock = yf.Ticker(ticker)

info = stock.info


# Convert large numbers into billions
def to_billions(number):
    if number is None:
        return "N/A"
    return f"${number / 1_000_000_000:,.2f}B"


# Format percentage
def to_percentage(number):
    if number is None:
        return "N/A"
    return f"{number * 100:.2f}%"


# Get company information
company_name = info.get("longName", ticker)

sector = info.get("sector", "N/A")
industry = info.get("industry", "N/A")

market_cap = info.get("marketCap")
revenue = info.get("totalRevenue")
profit_margin = info.get("profitMargins")
pe_ratio = info.get("trailingPE")


# Print report
print("\n===== COMPANY FUNDAMENTALS =====")

print("Company:", company_name)
print("Ticker:", ticker)

print("Sector:", sector)
print("Industry:", industry)

print("Market Cap:", to_billions(market_cap))
print("Total Revenue:", to_billions(revenue))

print("Profit Margin:", to_percentage(profit_margin))

if pe_ratio is not None:
    print(f"P/E Ratio: {pe_ratio:.2f}")
else:
    print("P/E Ratio: N/A")

print("================================")
