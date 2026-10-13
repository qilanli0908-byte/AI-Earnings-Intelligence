
import yfinance as yf

print("Welcome to AI Financial Statement Analyzer!")

ticker = input("Enter a stock ticker: ").strip().upper()

stock = yf.Ticker(ticker)

# Get annual financial statements
income_statement = stock.income_stmt
balance_sheet = stock.balance_sheet
cash_flow = stock.cashflow


# Function: Display financial statement
def show_statement(title, data):

    print(f"\n===== {title} =====")

    if data.empty:
        print("No financial data available.")
    else:
        print(data.to_string())


# Display all three statements
show_statement("INCOME STATEMENT", income_statement)

show_statement("BALANCE SHEET", balance_sheet)

show_statement("CASH FLOW STATEMENT", cash_flow)


# Save statements to CSV files
if not income_statement.empty:
    income_statement.to_csv(f"{ticker}_income_statement.csv")

if not balance_sheet.empty:
    balance_sheet.to_csv(f"{ticker}_balance_sheet.csv")

if not cash_flow.empty:
    cash_flow.to_csv(f"{ticker}_cash_flow.csv")

print("\nFinancial statements downloaded successfully!")
