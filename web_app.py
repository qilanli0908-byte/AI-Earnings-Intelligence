from sec_dynamic import get_sec_financials
import streamlit as st
import pandas as pd

from research import (
    get_stock_data,
    get_company_info,
    get_financials,
    analyze_financials,
    generate_commentary
)

# Page settings
st.set_page_config(
    page_title="AI Equity Research Copilot",
    layout="wide"
)

st.title("AI Equity Research Copilot")
st.write("Your AI-powered investment research assistant.")

# Stock ticker input
ticker = st.text_input(
    "Enter a stock ticker:",
    value="NVDA"
)

if st.button("Analyze"):

    ticker = ticker.strip().upper()

    if not ticker:
        st.warning("Please enter a valid ticker.")

    else:
        with st.spinner(f"Analyzing {ticker}..."):

            # 1. Get stock data
            data = get_stock_data(ticker)

            if data.empty:
                st.error("No stock data found. Please check the ticker.")
                st.stop()

            # 2. Get company information
            info = get_company_info(ticker)

            # 3. Calculate stock performance
            first_price = data["Close"].iloc[0]
            latest_price = data["Close"].iloc[-1]

            stock_return = (
                (latest_price - first_price) / first_price
            ) * 100

            # 4. Company Overview
            st.header("Company Overview")

            st.write("Company:", info.get("longName", ticker))
            st.write("Sector:", info.get("sector", "N/A"))
            st.write("Industry:", info.get("industry", "N/A"))

            # 5. Stock Performance
            st.header("Stock Performance")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Latest Closing Price",
                    f"${latest_price:.2f}"
                )

            with col2:
                st.metric(
                    "Period Return",
                    f"{stock_return:.2f}%"
                )

            # 6. Stock Chart
            st.subheader("Stock Price Chart")

            st.line_chart(data["Close"])

            # 7. Financial Analysis
            income = get_financials(ticker)
            summary = analyze_financials(income)

            st.header("Financial Performance")

            if summary is not None:

                st.dataframe(
                    summary.round(2),
                    use_container_width=True
                )

                # 8. Financial Commentary
                commentary = generate_commentary(summary)

                st.header("Financial Commentary")
                st.write(commentary)

            else:
                st.warning("Financial data is unavailable.")

            st.success("Research completed successfully!")
            
            # 9. SEC Official Financial Analysis
            
            # 9. Dynamic SEC Financial Analysis
            st.header("SEC Official Financial Analysis")

            try:
                sec_summary = get_sec_financials(ticker)

                if sec_summary is not None and not sec_summary.empty:

                    st.dataframe(
                        sec_summary,
                        use_container_width=True
                    )

                    st.caption(
                        f"Source: SEC EDGAR Company Facts | Ticker: {ticker}"
                    )

                else:
                    st.warning(
                        f"SEC financial data unavailable for {ticker}."
                    )

            except Exception as error:
                st.error(
                    f"Unable to retrieve SEC data: {error}"
                )


