
import re
import streamlit as st

from src.filing_retrieval import get_company_submissions, ensure_recent_10k_downloaded


PAGES = [
    "Overview",
    "Financial Analysis",
    "Filing Comparison",
    "Thesis Tracker",
    "Research Brief",
    "Investment Memo",
]


def normalize_ticker(value):
    ticker = value.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{1,10}(?:[.-][A-Z0-9]{1,3})?", ticker):
        raise ValueError("Enter a valid US ticker (e.g. AAPL or BRK-B).")
    return ticker


def render_dashboard_sidebar():
    """Return the active SEC-validated ticker and selected page."""
    if "active_research_ticker" not in st.session_state:
        # Existing demo data remains available without a network request on startup.
        st.session_state.active_research_ticker = "NVDA"

    with st.sidebar:
        st.markdown("## Earnings Intelligence")
        st.caption("SEC-grounded equity research")
        st.divider()
        st.markdown("### Company")
        with st.form("ticker_lookup_form", clear_on_submit=False):
            candidate = st.text_input(
                "US Public Company Ticker",
                value=st.session_state.active_research_ticker,
                help="Enter a ticker and select Load Company to validate it with SEC.",
            )
            submitted = st.form_submit_button("Load Company", use_container_width=True)

        if submitted:
            try:
                ticker = normalize_ticker(candidate)
                with st.spinner(f"Validating {ticker} with SEC..."):
                    submissions = get_company_submissions(ticker)
                if not isinstance(submissions, dict) or not submissions.get("cik"):
                    raise ValueError("SEC did not return a valid company identity.")
                # Switch only after SEC validation; failed requests retain the prior company.
                if ticker != st.session_state.active_research_ticker:
                    st.session_state.active_research_ticker = ticker
                    st.session_state.show_filing_diff = False
                    st.session_state.active_filing_ticker = ticker
                st.session_state.active_company_name = submissions.get("name", ticker)
                st.success(f"Loaded: {st.session_state.active_company_name}")
            except (ValueError, KeyError, TypeError) as error:
                st.error(str(error))
            except Exception as error:
                st.error(f"SEC lookup unavailable. Previous company retained. {type(error).__name__}")

        selected_ticker = st.session_state.active_research_ticker
        st.caption(f"Active ticker: **{selected_ticker}**")
        if st.button("Download / Refresh Two 10-Ks", use_container_width=True):
            try:
                with st.spinner(f"Checking {selected_ticker} annual filings..."):
                    paths = ensure_recent_10k_downloaded(selected_ticker, limit=2)
                st.success(f"{len(paths)} annual 10-K documents ready.")
            except Exception as error:
                st.error(f"Filing download unavailable: {error}")

        st.divider()
        st.markdown("### Research Navigation")
        selected_page = st.radio("Navigate", options=PAGES, key="dashboard_navigation")
        st.divider()
        st.caption(
            "Research outputs require human review. "
            "This platform does not provide investment advice."
        )
    return selected_ticker, selected_page


def should_show_section(selected_page, section):
    """
    Decide whether a dashboard section should be visible.

    This function does not fetch data or modify session state.
    """

    page_sections = {
        "Overview": {
            "overview",
        },
        "Financial Analysis": {
            "financial",
        },
        "Filing Comparison": {
            "filing",
        },
        "Thesis Tracker": {
            "thesis",
        },
        "Research Brief": {
            "brief",
        },
        "Investment Memo": {
            "memo",
        },
    }

    return section in page_sections.get(selected_page, set())
