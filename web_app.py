
import streamlit as st
import pandas as pd

from sec_dynamic import get_sec_financials
from src.change_detector import calculate_financial_changes
from src.filing_retrieval import get_recent_10k_with_urls

from research import (
    get_stock_data,
    get_company_info,
    get_financials,
    analyze_financials,
    generate_commentary
)


# --------------------------------------------------
# Page Settings
# --------------------------------------------------

st.set_page_config(
    page_title="AI Earnings Intelligence & Thesis Tracker",
    layout="wide"
)

st.title("AI Earnings Intelligence & Thesis Tracker")

st.write(
    "An evidence-driven financial research platform "
    "powered by SEC financial data and structured analysis."
)


# --------------------------------------------------
# Ticker Input
# --------------------------------------------------

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

            # ------------------------------------------
            # 1. Stock Data
            # ------------------------------------------

            data = get_stock_data(ticker)

            if data.empty:
                st.error(
                    "No stock data found. Please check the ticker."
                )
                st.stop()

            # ------------------------------------------
            # 2. Company Information
            # ------------------------------------------

            info = get_company_info(ticker)

            first_price = data["Close"].iloc[0]
            latest_price = data["Close"].iloc[-1]

            stock_return = (
                (latest_price - first_price) / first_price
            ) * 100

            # ------------------------------------------
            # 3. Company Overview
            # ------------------------------------------

            st.header("Company Overview")

            st.write(
                "Company:",
                info.get("longName", ticker)
            )

            st.write(
                "Sector:",
                info.get("sector", "N/A")
            )

            st.write(
                "Industry:",
                info.get("industry", "N/A")
            )

            # ------------------------------------------
            # 4. Stock Performance
            # ------------------------------------------

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

            st.subheader("Stock Price Chart")

            st.line_chart(data["Close"])

            # ------------------------------------------
            # 5. Financial Performance
            # ------------------------------------------

            income = get_financials(ticker)

            summary = analyze_financials(income)

            st.header("Financial Performance")

            if summary is not None:

                st.dataframe(
                    summary.round(2),
                    width="stretch"
                )

                commentary = generate_commentary(summary)

                st.header("Financial Commentary")

                st.write(commentary)

            else:
                st.warning(
                    "Financial data is unavailable."
                )

            # ------------------------------------------
            # 6. Official SEC Financial Analysis
            # ------------------------------------------

            st.header("SEC Official Financial Analysis")

            try:

                sec_summary = get_sec_financials(ticker)

                if sec_summary is not None and not sec_summary.empty:

                    # Show the core financial metrics.
                    financial_columns = [
                        "end",
                        "Revenue ($B)",
                        "Net Income ($B)",
                        "Revenue Growth (%)",
                        "Net Margin (%)"
                    ]

                    st.dataframe(
                        sec_summary[financial_columns],
                        width="stretch",
                        hide_index=True
                    )

                    st.caption(
                        f"Source: SEC EDGAR Company Facts | "
                        f"Ticker: {ticker}"
                    )

                    # ----------------------------------
                    # 7. Financial Change Detector
                    # ----------------------------------

                    st.header("Financial Change Detector")

                    changes = calculate_financial_changes(
                        sec_summary
                    )

                    if not changes.empty:

                        latest = changes.iloc[-1]

                        st.subheader("Latest Research Signals")

                        signal_col1, signal_col2 = st.columns(2)

                        with signal_col1:

                            st.metric(
                                "Revenue Growth Trend",
                                latest["Growth Trend"]
                            )

                        with signal_col2:

                            st.metric(
                                "Net Margin Trend",
                                latest["Margin Trend"]
                            )

                        st.info(
                            f"Research Signal: "
                            f"{latest['Research Signal']}"
                        )

                        st.subheader("Financial Change History")

                        change_columns = [
                            "end",
                            "Revenue Growth (%)",
                            "Growth Change (pp)",
                            "Growth Trend",
                            "Net Margin (%)",
                            "Margin Change (pp)",
                            "Margin Trend",
                            "Research Signal"
                        ]

                        st.dataframe(
                            changes[change_columns].round(2),
                            width="stretch",
                            hide_index=True
                        )

                        st.caption(
                            "Research signals are rule-based "
                            "interpretations of historical SEC "
                            "financial data. They are not "
                            "investment recommendations."
                        )

                    # ----------------------------------
                    # 8. SEC Source Information
                    # ----------------------------------

                    with st.expander("View SEC Filing Sources"):

                        source_columns = [
                            "end",
                            "Revenue Filing Date",
                            "Revenue Accession",
                            "Revenue Source Tag",
                            "Revenue SEC URL",
                            "Net Income Filing Date",
                            "Net Income Accession",
                            "Net Income Source Tag",
                            "Net Income SEC URL"
                        ]

                        st.dataframe(
                            sec_summary[source_columns],
                            width="stretch",
                            hide_index=True
                        )
                    
                    # ----------------------------------
                    # 9. SEC Filing Explorer
                    # ----------------------------------

                    st.subheader("SEC Filing Explorer")

                    st.write(
                        "Access the two most recent annual "
                        "10-K filings directly from SEC EDGAR."
                    )

                    try:

                        recent_filings = get_recent_10k_with_urls(
                            ticker,
                            limit=2
                        )

                        if not recent_filings.empty:

                            filing_columns = [
                                "form",
                                "filingDate",
                                "reportDate",
                                "accessionNumber",
                                "Document URL"
                            ]

                            st.dataframe(
                                recent_filings[filing_columns],
                                width="stretch",
                                hide_index=True,
                                column_config={
                                    "Document URL": st.column_config.LinkColumn(
                                        "Official SEC Filing",
                                        display_text="Open 10-K"
                                    )
                                }
                            )

                            st.caption(
                                "Source: SEC EDGAR Submissions API. "
                                "Links point to the filing's primary document."
                            )

                        else:

                            st.warning(
                                "No recent 10-K filings were found."
                            )

                    except Exception as filing_error:

                        st.warning(
                            f"Unable to retrieve filing history: "
                            f"{filing_error}"
                        )

        
                else:

                    st.warning(
                        f"SEC financial data unavailable for {ticker}."
                    )

            except Exception as error:

                st.error(
                    f"Unable to retrieve or analyze SEC data: {error}"
                )

            st.success("Research process completed.")
