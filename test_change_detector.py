
from sec_dynamic import get_sec_financials
from src.change_detector import calculate_financial_changes


tickers = ["NVDA", "AMD"]

for ticker in tickers:

    print(f"\n========== {ticker} FINANCIAL CHANGE TEST ==========")

    # Step 1: Retrieve official SEC financial data.
    financial_data = get_sec_financials(ticker)

    if financial_data is None or financial_data.empty:
        print(f"FAIL: No financial data available for {ticker}")
        continue

    # Step 2: Calculate year-over-year changes.
    changes = calculate_financial_changes(financial_data)

    # Step 3: Display the relevant metrics.
    columns = [
        "end",
        "Revenue Growth (%)",
        "Growth Change (pp)",
        "Growth Trend",
        "Net Margin (%)",
        "Margin Change (pp)",
        "Margin Trend",
        "Research Signal"
    ]

    print(changes[columns].round(2).to_string(index=False))

    print(f"\nPASS: Financial changes calculated for {ticker}.")
