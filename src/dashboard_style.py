
import streamlit as st


def apply_dashboard_style():
    """
    Apply consistent styling to the Streamlit dashboard.

    Presentation-only:
    no changes to SEC data, research logic, or AI calls.
    /* Metric card readability */
[data-testid="stMetric"] {
    min-width: 0;
}

[data-testid="stMetricLabel"] {
    white-space: normal;
    overflow-wrap: anywhere;
}

[data-testid="stMetricValue"] {
    font-size: clamp(1.15rem, 2vw, 1.65rem);
}

[data-testid="stMetricValue"] > div {
    white-space: normal;
    overflow-wrap: anywhere;
    line-height: 1.3;
}
    """

    st.markdown(
        """
        <style>
        /* Main app background and spacing */
        .stApp {
            background-color: #F6F8FC;
            color: #14263D;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1320px;
        }

        /* Typography */
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

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #14263D;
        }

        section[data-testid="stSidebar"] * {
            color: #F8FAFC;
        }

        /* Metric cards */
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

        /* Buttons */
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {
            background-color: #2563EB;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: 600;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
        }

        /* Expanders */
        div[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            overflow: hidden;
        }

        /* Tables */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            overflow: hidden;
        }

        /* Horizontal dividers */
        hr {
            border-color: #E2E8F0;
        }

        /* Captions */
        .stCaption {
            color: #64748B;
        }

        /* Mobile responsiveness */
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
    """
    Render a clean dashboard header using native Streamlit
    components instead of multiline HTML.
    """

    st.markdown(
        """
        <div style="
            color: #2563EB;
            font-size: 12px;
            font-weight: 750;
            letter-spacing: 2px;
            margin-bottom: 8px;
        ">EQUITY RESEARCH PLATFORM</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h1 style="
            color: #14263D;
            font-size: 34px;
            font-weight: 750;
            letter-spacing: -1px;
            margin-bottom: 8px;
        ">Earnings Intelligence</h1>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "SEC-grounded financial analysis, "
        "disclosure intelligence and investment thesis tracking."
    )

    st.divider()
