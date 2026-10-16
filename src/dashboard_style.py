
import streamlit as st


def apply_dashboard_style():
    """Apply the global dashboard design system."""

    st.markdown(
        """
        <style>

        /* ==========================================
           GLOBAL DASHBOARD
        ========================================== */

        .stApp {
            background-color: #F6F8FC;
            color: #14263D;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1320px;
        }

        /* ==========================================
           TYPOGRAPHY
        ========================================== */

        h1, h2, h3 {
            color: #14263D;
            letter-spacing: -0.025em;
        }

        h1 {
            font-weight: 750;
        }

        h2 {
            margin-top: 1.4rem;
            font-weight: 700;
        }

        /* ==========================================
           SIDEBAR
        ========================================== */

        section[data-testid="stSidebar"] {
            background-color: #14263D;
            color: #F8FAFC;
        }

        /* Sidebar headings and ordinary text */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label {
            color: #F8FAFC;
        }

        /* Keep regular sidebar text white, without overriding button text */
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stCaption {
            color: #F8FAFC;
        }

        /* ==========================================
           DAY 17: TICKER SEARCH INPUT
        ========================================== */

        section[data-testid="stSidebar"]
        div[data-testid="stTextInput"] input {
            background-color: #FFFFFF !important;
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
            caret-color: #111827 !important;
            border-radius: 8px !important;
        }

        /* Input text must remain dark even when nested
           inside Streamlit's sidebar components */

        section[data-testid="stSidebar"] input[type="text"] {
            color: #111827 !important;
            -webkit-text-fill-color: #111827 !important;
        }

        /* Placeholder */

        section[data-testid="stSidebar"]
        div[data-testid="stTextInput"] input::placeholder {
            color: #6B7280 !important;
            -webkit-text-fill-color: #6B7280 !important;
            opacity: 1 !important;
        }

        /* Input focus */

        section[data-testid="stSidebar"]
        div[data-testid="stTextInput"] input:focus {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 1px #2563EB !important;
        }

        /* ==========================================
           LOAD COMPANY BUTTON
        ========================================== */

        section[data-testid="stSidebar"]
        div[data-testid="stFormSubmitButton"] button {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border: 1px solid #2563EB !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stFormSubmitButton"] button * {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"]
        div[data-testid="stFormSubmitButton"] button:hover {
            background-color: #1D4ED8 !important;
            border-color: #1D4ED8 !important;
        }

        /* Other sidebar buttons */

        section[data-testid="stSidebar"]
        div[data-testid="stButton"] button {
            background-color: #FFFFFF !important;
            color: #14263D !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        /* Ensure nested button text is dark */

        section[data-testid="stSidebar"]
        div[data-testid="stButton"] button * {
            color: #14263D !important;
        }

        /* Hover effect */

        section[data-testid="stSidebar"]
        div[data-testid="stButton"] button:hover {
            background-color: #E8EEF8 !important;
            border-color: #2563EB !important;
        }

        /* ==========================================
           METRIC CARDS
        ========================================== */

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 3px 12px rgba(20, 38, 61, 0.04);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B;
            font-size: 0.85rem;
        }

        div[data-testid="stMetricValue"] {
            color: #14263D;
            font-weight: 750;
        }

        /* ==========================================
           MAIN PAGE BUTTONS
        ========================================== */

        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background-color: #2563EB;
            color: #FFFFFF;
            border-radius: 10px;
            border: none;
            font-weight: 600;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
        }

        /* ==========================================
           EXPANDERS
        ========================================== */

        div[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            overflow: hidden;
        }

        /* ==========================================
           DATA TABLES
        ========================================== */

        div[data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            overflow: hidden;
        }

        /* ==========================================
           DIVIDERS & CAPTIONS
        ========================================== */

        hr {
            border-color: #E2E8F0;
        }

        .stCaption {
            color: #64748B;
        }

        /* ==========================================
           MOBILE RESPONSIVENESS
        ========================================== */

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }

            h1 {
                font-size: 1.8rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_header():
    """Render the dashboard title and description."""

    st.title("AI Earnings Intelligence & Thesis Tracker")

    st.caption(
        "An SEC-grounded equity research platform combining "
        "financial analysis, filing comparison, investment thesis "
        "monitoring, and evidence-linked research."
    )

    st.divider()
