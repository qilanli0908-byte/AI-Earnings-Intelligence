
import streamlit as st

from src.company_models import CompanyProfile


def format_number(value, suffix="", decimals=2):
    """Display missing numerical data explicitly."""

    if value is None:
        return "N/A"

    return f"{value:,.{decimals}f}{suffix}"


def format_text(value):
    """Avoid showing Python None in the dashboard."""

    if value is None or str(value).strip() == "":
        return "N/A"

    return str(value)


def render_company_profile(profile):
    """
    Render an existing CompanyProfile.

    This function does not fetch SEC data,
    call an AI model, or modify stored assessments.
    """

    if not isinstance(profile, CompanyProfile):
        raise TypeError(
            "Expected a CompanyProfile object."
        )

    identity = profile.identity
    financial = profile.financial
    signals = profile.research_signals

    st.header("Company Research Profile")

    # ----------------------------------------
    # 1. Company Identity
    # ----------------------------------------

    st.subheader(
        format_text(identity.company_name)
    )

    st.caption(
        f"Ticker: {identity.ticker} | "
        f"Source: {identity.source}"
    )

    identity_col1, identity_col2, identity_col3 = (
        st.columns(3)
    )

    identity_col1.metric(
        "SEC CIK",
        format_text(identity.cik)
    )

    identity_col2.metric(
        "Exchange",
        format_text(identity.exchange)
    )

    identity_col3.metric(
        "Industry",
        format_text(identity.industry)
    )

    # ----------------------------------------
    # 2. Financial Overview
    # ----------------------------------------

    st.subheader("Latest Financial Overview")

    if financial is not None:

        financial_col1, financial_col2 = st.columns(2)

        financial_col1.metric(
            "Revenue",
            format_number(
                financial.revenue_billions,
                suffix=" B USD"
            )
        )

        financial_col2.metric(
            "Net Income",
            format_number(
                financial.net_income_billions,
                suffix=" B USD"
            )
        )

        financial_col3, financial_col4 = st.columns(2)

        financial_col3.metric(
            "Revenue Growth",
            format_number(
                financial.revenue_growth_pct,
                suffix="%"
            )
        )

        financial_col4.metric(
            "Net Margin",
            format_number(
                financial.net_margin_pct,
                suffix="%"
            )
        )

        st.caption(
            "Source: SEC Company Facts | "
            f"Fiscal year end: {financial.fiscal_year_end}"
        )

    else:

        st.warning(
            "Official SEC financial overview is unavailable."
        )

    # ----------------------------------------
    # 3. Integrated Research Signals
    # ----------------------------------------

    st.subheader("Research Signals")

    if signals is not None:

        if signals.financial is not None:

            st.write(
                "**Growth Trend:**",
                signals.financial.growth_trend
            )

            st.write(
                "**Margin Trend:**",
                signals.financial.margin_trend
            )

            st.info(
                signals.financial.research_signal
            )

        else:

            st.caption(
                "Financial research signals are unavailable."
            )

        st.write(
            "**Disclosure Research Status:**",
            signals.overall_research_status
        )

        priority_col1, priority_col2, priority_col3 = (
            st.columns(3)
        )

        priority_col1.metric(
            "High Priority",
            signals.high_priority_count
        )

        priority_col2.metric(
            "Medium Priority",
            signals.medium_priority_count
        )

        priority_col3.metric(
            "Low Priority",
            signals.low_priority_count
        )

        st.caption(
            f"{signals.disclosure_count} validated "
            "disclosure assessments are included. "
            "Priority describes research attention, "
            "not an investment risk rating."
        )

    # ----------------------------------------
    # 4. Official Filing Sources
    # ----------------------------------------

    st.subheader("Official SEC Filing Sources")

    if profile.filing_sources:

        for filing in profile.filing_sources:

            st.markdown(
                f"**{filing.form}** | "
                f"Filed: {filing.filing_date}"
            )

            st.caption(
                "Accession: "
                f"{filing.accession_number} | "
                "Report date: "
                f"{format_text(filing.fiscal_year_end)}"
            )

            st.markdown(
                f"[Open Original SEC Filing]"
                f"({filing.sec_url})"
            )

    else:

        st.caption(
            "No verified SEC 10-K filing sources "
            "are currently available."
        )

    # ----------------------------------------
    # 5. Deterministic Research Summary
    # ----------------------------------------

    st.subheader("Company Research Summary")

    st.write(profile.research_summary)

    if profile.requires_human_review:

        st.caption(
            "Human review required. Financial and "
            "disclosure signals do not establish "
            "causation or constitute investment advice."
        )
