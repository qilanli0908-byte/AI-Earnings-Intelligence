
import yfinance as yf
import matplotlib.pyplot as plt


# Function 1: Get stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1mo")
    return data


# Function 2: Analyze stock performance
def analyze_stock(ticker, data):

    first_price = data["Close"].iloc[0]
    latest_price = data["Close"].iloc[-1]

    price_change = latest_price - first_price
    return_pct = (price_change / first_price) * 100

    print("\n===== STOCK RESEARCH SUMMARY =====")
    print("Ticker:", ticker)
    print(f"First Closing Price: ${first_price:.2f}")
    print(f"Latest Closing Price: ${latest_price:.2f}")
    print(f"Price Change: ${price_change:.2f}")
    print(f"Period Return: {return_pct:.2f}%")
    print("==================================")


# Function 3: Create stock chart
def create_chart(ticker, data):

    plt.figure(figsize=(10, 5))

    plt.plot(data.index, data["Close"], marker="o")

    plt.title(f"{ticker} Stock Price - Last Month")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig("stock_chart.png", dpi=300)
    plt.show()

    print("\nChart saved successfully!")


# Main Program
print("Welcome to AI Equity Research Copilot!")

ticker = input("Enter a stock ticker: ").strip().upper()

if not ticker:
    print("Please enter a stock ticker.")

else:
    data = get_stock_data(ticker)

    if data.empty:
        print("No stock data found. Please check the ticker.")

    else:
        analyze_stock(ticker, data)
        create_chart(ticker, data)
