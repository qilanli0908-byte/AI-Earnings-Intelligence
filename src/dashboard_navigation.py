
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
        st.markdown('<div class="ei-brand"><span class="ei-brand-mark">↗</span><div><div class="ei-brand-title">Earnings Intelligence</div><div class="ei-brand-subtitle">SEC-grounded equity research</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="ei-sidebar-label">RESEARCH WORKSPACE</div>', unsafe_allow_html=True)
        selected_page = st.radio(
            "Research pages", options=PAGES, key="dashboard_navigation",
            label_visibility="collapsed",
        )
        st.markdown('<div class="ei-sidebar-rule"></div><div class="ei-sidebar-label">COMPANY & DATA</div>', unsafe_allow_html=True)
        with st.form("ticker_lookup_form", clear_on_submit=False):
            candidate = st.text_input(
                "Ticker symbol",
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
        st.markdown('<div class="ei-sidebar-rule"></div><div class="ei-sidebar-label">FILING DOWNLOADS</div>', unsafe_allow_html=True)
        if st.button("↓  Get 10-K Filings", key="get_10k_filings", use_container_width=True,
                     help="Download or refresh the two most recent original annual SEC 10-K filings for the active ticker."):
            try:
                with st.spinner(f"Checking {selected_ticker} annual filings..."):
                    paths = ensure_recent_10k_downloaded(selected_ticker, limit=2)
                st.success(f"{len(paths)} annual 10-K documents ready.")
            except Exception as error:
                st.error(f"Filing download unavailable: {error}")
        st.caption("Download / refresh the latest two annual filings")
        st.markdown(f'<div class="ei-ticker-status"><span class="ei-status-dot"></span> Active ticker: <strong>{selected_ticker}</strong></div>', unsafe_allow_html=True)
        st.markdown('<div class="ei-sidebar-rule"></div>', unsafe_allow_html=True)
        st.caption("SEC-source research · Human review required · Not investment advice")
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
