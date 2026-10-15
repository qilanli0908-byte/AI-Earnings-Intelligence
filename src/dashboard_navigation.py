
import streamlit as st


SUPPORTED_COMPANIES = {
    "NVDA": "NVIDIA",
    "AMD": "Advanced Micro Devices",
}


def render_dashboard_sidebar():
    """
    Render the global company selector and research navigation.

    Returns:
        selected_ticker: str
        selected_page: str
    """

    with st.sidebar:

        st.markdown("## Earnings Intelligence")

        st.caption("SEC-grounded equity research")

        st.divider()

        st.markdown("### Company")

        selected_ticker = st.selectbox(
            "Select Company",
            options=list(SUPPORTED_COMPANIES.keys()),
            format_func=lambda value: (
                f"{value} — {SUPPORTED_COMPANIES[value]}"
            ),
            key="global_company_selector",
        )

        st.divider()

        st.markdown("### Research Navigation")

        selected_page = st.radio(
            "Navigate",
            options=[
                "Overview",
                "Financial Analysis",
                "Filing Comparison",
                "Thesis Tracker",
                "Research Brief",
                "Investment Memo",
            ],
            key="dashboard_navigation",
        )

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
