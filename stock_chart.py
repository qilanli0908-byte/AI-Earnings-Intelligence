
import yfinance as yf
import matplotlib.pyplot as plt

print("Welcome to AI Equity Research Copilot!")

ticker = input("Enter a stock ticker: ").strip().upper()

stock = yf.Ticker(ticker)

# Get historical stock prices
data = stock.history(period="1mo")

if data.empty:
    print("No stock data found.")

else:
    # Create a chart
    plt.figure(figsize=(10, 5))

    plt.plot(data.index, data["Close"], marker="o")

    plt.title(f"{ticker} Stock Price - Last Month")

    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")

    plt.grid(True)

    plt.tight_layout()

    # Save the chart
    plt.savefig("stock_chart.png", dpi=300)

    # Display the chart
    plt.show()

    print("Chart saved successfully!")
