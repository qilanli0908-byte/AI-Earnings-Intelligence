
import yfinance as yf

print("Welcome to AI Equity Research Copilot!")

ticker = input("Enter a stock ticker: ").strip().upper()

stock = yf.Ticker(ticker)

data = stock.history(period="5d")

if data.empty:
    print("No stock data found. Please check the ticker.")

else:
    first_price = data["Close"].iloc[0]
    latest_price = data["Close"].iloc[-1]

    price_change = latest_price - first_price

    return_pct = (price_change / first_price) * 100

    print("\n===== STOCK RESEARCH SUMMARY =====")

    print("Ticker:", ticker)

    print(f"First Closing Price: ${first_price:.2f}")

    print(f"Latest Closing Price: ${latest_price:.2f}")

    print(f"Price Change: ${price_change:.2f}")

    print(f"Return: {return_pct:.2f}%")

    print("==================================")
