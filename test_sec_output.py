
from sec_dynamic import get_sec_financials

# Companies used for initial validation
tickers = ["NVDA", "AMD"]

for ticker in tickers:

    print(f"\n========== {ticker} SEC VALIDATION ==========")

    df = get_sec_financials(ticker)

    if df is None or df.empty:
        print(f"FAIL: No financial data returned for {ticker}")
        continue

    # Check that required provenance columns exist
    required_columns = [
        "start",
        "end",
        "Revenue ($B)",
        "Net Income ($B)",
        "Revenue Growth (%)",
        "Net Margin (%)",
        "Revenue Filing Date",
        "Revenue Accession",
        "Revenue Source Tag",
        "Revenue SEC URL",
        "Net Income Filing Date",
        "Net Income Accession",
        "Net Income Source Tag",
        "Net Income SEC URL"
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        print("FAIL: Missing columns:", missing)
        continue

    print("PASS: All required columns exist.")

    # Check for missing values in essential source fields
    source_columns = [
        "Revenue Accession",
        "Revenue Source Tag",
        "Revenue SEC URL",
        "Net Income Accession",
        "Net Income Source Tag",
        "Net Income SEC URL"
    ]

    if df[source_columns].isna().any().any():
        print("FAIL: Missing SEC source information.")
    else:
        print("PASS: SEC source information is present.")

    # Display financial results
    print("\nFinancial Summary:")

    print(
        df[
            [
                "end",
                "Revenue ($B)",
                "Net Income ($B)",
                "Revenue Growth (%)",
                "Net Margin (%)"
            ]
        ].to_string(index=False)
    )

    # Display filing provenance
    print("\nSEC Filing Sources:")

    print(
        df[
            [
                "end",
                "Revenue Accession",
                "Net Income Accession"
            ]
        ].to_string(index=False)
    )

    print(f"\nCompleted validation for {ticker}.")
