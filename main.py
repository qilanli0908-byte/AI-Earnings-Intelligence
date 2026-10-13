
from research import (
    get_stock_data,
    get_company_info,
    get_financials,
    analyze_financials,
    generate_commentary,
    create_chart
)


print("====================================")
print("     AI EQUITY RESEARCH COPILOT")
print("====================================")

ticker = input("\nEnter a stock ticker: ").strip().upper()

if not ticker:
    print("Please enter a valid ticker.")

else:
    print("\nStarting research on", ticker, "...")

    # Step 1: Stock data
    data = get_stock_data(ticker)

    if data.empty:
        print("No stock price data found.")

    else:
        first_price = data["Close"].iloc[0]
        latest_price = data["Close"].iloc[-1]

        stock_return = (
            (latest_price - first_price) / first_price
        ) * 100

        print("\n===== STOCK PERFORMANCE =====")
        print(f"Latest Closing Price: ${latest_price:.2f}")
        print(f"Period Return: {stock_return:.2f}%")

        # Step 2: Company information
        info = get_company_info(ticker)

        print("\n===== COMPANY OVERVIEW =====")
        print("Company:", info.get("longName", ticker))
        print("Sector:", info.get("sector", "N/A"))
        print("Industry:", info.get("industry", "N/A"))

        # Step 3: Financial analysis
        income = get_financials(ticker)

        summary = analyze_financials(income)

        print("\n===== FINANCIAL PERFORMANCE =====")

        if summary is not None:
            print(summary.round(2).to_string())

            summary.to_csv(
                f"{ticker}_financial_summary.csv"
            )

        # Step 4: Commentary
        commentary = generate_commentary(summary)

        print("\n===== FINANCIAL COMMENTARY =====")
        print(commentary)

        # Step 5: Chart
        create_chart(ticker, data)

        print("\nResearch completed successfully!")
