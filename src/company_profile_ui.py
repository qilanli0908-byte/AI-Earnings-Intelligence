import streamlit as st
from html import escape
from urllib.parse import urlparse
from src.company_models import CompanyProfile


def _text(value):
    return "N/A" if value is None or not str(value).strip() else str(value)


def _number(value, suffix="", decimals=2):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):,.{decimals}f}{suffix}"
    except (ValueError, TypeError):
        return "N/A"


def _card(label, value, note="", tone="blue"):
    return (
        f'<div class="ei-kpi ei-kpi-{tone}">'
        f'<div class="ei-kpi-label">{escape(str(label))}</div>'
        f'<div class="ei-kpi-value">{escape(str(value))}</div>'
        f'<div class="ei-kpi-note">{escape(str(note))}</div></div>'
    )


def render_company_profile(profile):
    """Present an existing validated profile; no fetching, AI calls or persistence."""
    if not isinstance(profile, CompanyProfile):
        raise TypeError("Expected a CompanyProfile object.")

    identity = profile.identity
    financial = profile.financial
    signals = profile.research_signals

    # Identity is intentionally a single horizontal card rather than three large metrics.
    st.markdown(
        '<div class="ei-profile-identity">'
        '<div class="ei-identity-primary"><div class="ei-identity-kicker">SEC COMPANY PROFILE</div>'
        f'<div class="ei-identity-name">{escape(_text(identity.company_name))}</div>'
        f'<div class="ei-identity-meta">{escape(_text(identity.ticker))} · {escape(_text(identity.source))}</div></div>'
        '<div class="ei-identity-detail"><span>SEC CIK</span>'
        f'<strong>{escape(_text(identity.cik))}</strong></div>'
        '<div class="ei-identity-detail"><span>Exchange</span>'
        f'<strong>{escape(_text(identity.exchange))}</strong></div>'
        '<div class="ei-identity-detail"><span>Industry</span>'
        f'<strong>{escape(_text(identity.industry))}</strong></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ei-section-title">Latest Financial Overview</div>', unsafe_allow_html=True)
    if financial is None:
        st.info("Official SEC financial overview is unavailable.")
    else:
        cards = [
            _card("Revenue", _number(financial.revenue_billions, " B USD"), "Latest fiscal year", "blue"),
            _card("Net Income", _number(financial.net_income_billions, " B USD"), "Latest fiscal year", "green"),
            _card("Revenue Growth", _number(financial.revenue_growth_pct, "%"), "Year over year", "purple"),
            _card("Net Margin", _number(financial.net_margin_pct, "%"), "Latest fiscal year", "amber"),
        ]
        st.markdown('<div class="ei-kpi-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)
        st.caption(f"Source: SEC Company Facts · Fiscal year end: {_text(financial.fiscal_year_end)}")

    st.markdown('<div class="ei-section-title">Integrated Research Signals</div>', unsafe_allow_html=True)
    if signals is None:
        st.info("Research signals are not available for this company.")
    else:
        left, right = st.columns([1.4, 1], gap="medium")
        with left:
            with st.container(border=True):
                st.markdown("**Financial Signals**")
                if signals.financial is None:
                    st.caption("Financial research signals are unavailable.")
                else:
                    a, b = st.columns(2)
                    a.markdown(f"**Growth trend**  \n{_text(signals.financial.growth_trend)}")
                    b.markdown(f"**Margin trend**  \n{_text(signals.financial.margin_trend)}")
                    st.info(_text(signals.financial.research_signal))
        with right:
            with st.container(border=True):
                st.markdown("**Disclosure Research**")
                st.caption(f"Status: {_text(signals.overall_research_status)}")
                st.markdown(
                    '<div class="ei-priority-row">'
                    + _card("High", signals.high_priority_count, "Priority", "amber")
                    + _card("Medium", signals.medium_priority_count, "Priority", "blue")
                    + _card("Low", signals.low_priority_count, "Priority", "green")
                    + '</div>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"{signals.disclosure_count} validated disclosure assessments. "
                    "Priority indicates research attention, not an investment risk rating."
                )

    st.markdown('<div class="ei-section-title">Recent SEC 10-K Filings</div>', unsafe_allow_html=True)
    if profile.filing_sources:
        with st.container(border=True):
            for index, filing in enumerate(profile.filing_sources):
                if index:
                    st.divider()
                label = f"{_text(filing.form)} · Filed {_text(filing.filing_date)}"
                st.markdown(f"**{label}**")
                st.caption(
                    f"Report date: {_text(filing.fiscal_year_end)} · "
                    f"Accession: {_text(filing.accession_number)}"
                )
                url = _text(filing.sec_url)
                parsed = urlparse(url)
                if parsed.scheme == "https" and parsed.hostname in {"sec.gov", "www.sec.gov"}:
                    st.link_button("View original filing ↗", url)
                else:
                    st.caption("Official filing link unavailable.")
    else:
        st.info("No verified SEC 10-K filing sources are currently available.")

    st.markdown('<div class="ei-section-title">Company Research Summary</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.write(profile.research_summary)
        if profile.requires_human_review:
            st.caption(
                "Human review required. Financial and disclosure signals do not establish "
                "causation or constitute investment advice."
            )
