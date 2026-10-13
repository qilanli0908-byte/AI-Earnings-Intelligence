
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


# 1. Get stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(period="1mo")


# 2. Get company information
def get_company_info(ticker):
    stock = yf.Ticker(ticker)
    return stock.info


# 3. Get financial statements
def get_financials(ticker):
    stock = yf.Ticker(ticker)
    return stock.income_stmt


# 4. Analyze financial performance
def analyze_financials(income):

    if income.empty:
        return None

    required = ["Total Revenue", "Gross Profit", "Net Income"]

    for metric in required:
        if metric not in income.index:
            print("Missing financial metric:", metric)
            return None

    revenue = pd.to_numeric(
        income.loc["Total Revenue"], errors="coerce"
    )

    gross_profit = pd.to_numeric(
        income.loc["Gross Profit"], errors="coerce"
    )

    net_income = pd.to_numeric(
        income.loc["Net Income"], errors="coerce"
    )

    summary = pd.DataFrame({
        "Revenue ($B)": revenue / 1_000_000_000,
        "Gross Margin (%)": gross_profit / revenue * 100,
        "Net Margin (%)": net_income / revenue * 100
    })

    summary.index = pd.to_datetime(summary.index)
    summary = summary.sort_index()

    summary["Revenue Growth (%)"] = (
        summary["Revenue ($B)"].pct_change(fill_method=None) * 100
    )

    return summary


# 5. Generate financial commentary
def generate_commentary(summary):

    if summary is None:
        return "Financial analysis unavailable."

    valid = summary.dropna(subset=["Revenue ($B)"])

    if len(valid) < 2:
        return "Not enough financial data for comparison."

    latest = valid.iloc[-1]
    previous = valid.iloc[-2]

    latest_year = valid.index[-1].year
    previous_year = valid.index[-2].year

    revenue = latest["Revenue ($B)"]
    growth = latest["Revenue Growth (%)"]

    gross_margin = latest["Gross Margin (%)"]
    previous_margin = previous["Gross Margin (%)"]

    net_margin = latest["Net Margin (%)"]

    commentary = (
        f"In FY{latest_year}, the company reported "
        f"revenue of ${revenue:.2f} billion, "
        f"representing {growth:.2f}% year-over-year growth.\n"
        f"Gross margin changed from {previous_margin:.2f}% "
        f"in FY{previous_year} to {gross_margin:.2f}% "
        f"in FY{latest_year}.\n"
        f"Net profit margin was {net_margin:.2f}%."
    )

    return commentary


# 6. Create stock chart
def create_chart(ticker, data):

    if data.empty:
        print("No stock price data available.")
        return

    plt.figure(figsize=(10, 5))

    plt.plot(data.index, data["Close"], marker="o")

    plt.title(f"{ticker} Stock Price - Last Month")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")

    plt.grid(True)
    plt.tight_layout()

    filename = f"{ticker}_stock_chart.png"

    plt.savefig(filename, dpi=300)
    plt.close()

    print("Chart saved:", filename)
