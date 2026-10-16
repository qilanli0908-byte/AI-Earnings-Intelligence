
import streamlit as st
import pandas as pd

from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text,
    extract_section
)

from src.filing_diff import (
    compare_filing_sections,
    match_revised_disclosures,
    is_formatting_only_change
)

from sec_dynamic import get_sec_financials
from src.change_detector import calculate_financial_changes
from src.signal_dashboard import build_company_dashboard_data
from src.signal_dashboard import load_current_disclosure_assessments

from src.company_builder import build_company_profile

from src.company_profile_ui import render_company_profile

from src.filing_retrieval import get_company_submissions

from src.filing_retrieval import get_recent_10k_with_urls, get_historical_10k_with_urls, download_10k
from src.ai_analyzer import analyze_disclosure
from src.research_engine import assess_research_priority
from src.research_storage import (
    save_assessment,
    load_assessment,
    make_assessment_id,
)
from src.research_ranking import (
    build_ranking_rows,
    rank_assessments,
)

from research import (
    get_stock_data,
    get_company_info,
    get_financials,
    analyze_financials,
    generate_commentary
)
from src.thesis_monitor_ui import render_thesis_monitoring
from src.brief_builder import build_research_brief
from src.brief_evidence import check_brief_evidence
from src.brief_ui import render_research_brief

from src.thesis_storage import load_theses
from src.thesis_integration import monitor_company_theses
from src.brief_integrity import validate_brief_integrity
from src.brief_integrity_ui import render_integrity_report
from src.memo_export import export_investment_memo

from src.dashboard_style import (
    apply_dashboard_style,
    render_dashboard_header,
)
from src.dashboard_navigation import render_dashboard_sidebar

# --------------------------------------------------
# Page Settings
# --------------------------------------------------

st.set_page_config(
    page_title="AI Earnings Intelligence & Thesis Tracker",
    layout="wide"
)
apply_dashboard_style()

@st.cache_data(ttl=3600, show_spinner=False)
def cached_historical_filings(ticker):
    return get_historical_10k_with_urls(ticker)


selected_ticker, selected_page = render_dashboard_sidebar()

render_dashboard_header()

if selected_page == "Overview":
    st.subheader(f"{selected_ticker} | Company Overview")
    try:
        overview_info = get_company_info(selected_ticker)
        st.write("**Company:**", overview_info.get("longName", selected_ticker))
        st.write("**Sector:**", overview_info.get("sector", "N/A"))
        st.write("**Industry:**", overview_info.get("industry", "N/A"))
    except Exception as error:
        st.warning(f"Company identity is temporarily unavailable: {error}")
    st.divider()


if selected_page == "Financial Analysis":

    # --------------------------------------------------
    # Ticker Input
    # --------------------------------------------------

    ticker = selected_ticker

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


elif selected_page in (
    "Overview",
    "Filing Comparison",
    "Thesis Tracker",
    "Research Brief",
    "Investment Memo",
):

    # ============================================================
    # SEC Filing Diff Explorer
    # ============================================================

    if selected_page == "Filing Comparison":
        st.divider()
        st.subheader("SEC Filing Diff Explorer")

        st.caption(
            "Compare Risk Factors across two annual SEC 10-K filings. "
            "Results are rule-based textual differences, not investment advice."
        )

    diff_ticker = selected_ticker

    filing_folder = Path("data/filings") / diff_ticker

    filing_files = sorted(
        filing_folder.glob("*_10K.html")
    )

    if len(filing_files) < 2 and selected_page != "Filing Comparison":

        st.info(
            "Two downloaded 10-K filings are required. "
            "Please download the filings first."
        )

    else:


        # Track the active Filing Comparison ticker.
        if "active_filing_ticker" not in st.session_state:
            st.session_state.active_filing_ticker = diff_ticker

        # Hide the previous company's comparison on ticker change.
        if st.session_state.active_filing_ticker != diff_ticker:
            st.session_state.active_filing_ticker = diff_ticker
            st.session_state.show_filing_diff = False

        if "show_filing_diff" not in st.session_state:
            st.session_state.show_filing_diff = False

        if selected_page == "Filing Comparison":
            st.caption("Choose any two available original annual 10-K filings. Fiscal years use SEC reportDate.")
            try:
                historical = cached_historical_filings(diff_ticker)
                if len(historical) < 2:
                    st.warning("SEC lists fewer than two original annual 10-K filings.")
                    st.stop()
                options = historical["accessionNumber"].tolist()
                by_accession = {
                    row["accessionNumber"]: row
                    for _, row in historical.iterrows()
                }
                def filing_label(accession):
                    row = by_accession[accession]
                    return (
                        f"FY{row['Fiscal Year']} | Period ended {row['reportDate']} "
                        f"| Filed {row['filingDate']} | {accession}"
                    )
                with st.form(key=f"historical_compare_{diff_ticker}"):
                    left, right = st.columns(2)
                    with left:
                        previous_accession = st.selectbox(
                            "Previous 10-K", options, index=1,
                            format_func=filing_label,
                        )
                    with right:
                        latest_accession = st.selectbox(
                            "Comparison 10-K", options, index=0,
                            format_func=filing_label,
                        )
                    submitted = st.form_submit_button("Compare Selected 10-Ks")
                if submitted:
                    previous = by_accession[previous_accession]
                    latest = by_accession[latest_accession]
                    if previous["reportDate"] >= latest["reportDate"]:
                        st.error("Choose two distinct filings in chronological order (previous → comparison).")
                        st.session_state.show_filing_diff = False
                    else:
                        with st.spinner("Downloading selected SEC 10-Ks if needed..."):
                            selected_old = download_10k(diff_ticker, previous)
                            selected_new = download_10k(diff_ticker, latest)
                        st.session_state[f"filing_pair_{diff_ticker}"] = (
                            str(selected_old), str(selected_new),
                            previous.to_dict(), latest.to_dict(),
                        )
                        st.session_state.show_filing_diff = True
                pair = st.session_state.get(f"filing_pair_{diff_ticker}")
                if pair and st.session_state.show_filing_diff:
                    old_meta, new_meta = pair[2], pair[3]
                    st.markdown(
                        f"**{diff_ticker}: FY{old_meta['Fiscal Year']} → "
                        f"FY{new_meta['Fiscal Year']}**"
                    )
                    st.caption(
                        f"Previous period ended {old_meta['reportDate']} "
                        f"(filed {old_meta['filingDate']}) · "
                        f"Comparison period ended {new_meta['reportDate']} "
                        f"(filed {new_meta['filingDate']})"
                    )
                    st.markdown(
                        f"[Previous SEC 10-K]({old_meta['Document URL']}) · "
                        f"[Comparison SEC 10-K]({new_meta['Document URL']})"
                    )
            except Exception as error:
                st.error(f"Unable to load historical SEC filings: {error}")
                st.stop()

        # Research pages use local SEC filings; AI remains button-triggered only.
        run_comparison = (
            (st.session_state.show_filing_diff and bool(
                st.session_state.get(f"filing_pair_{diff_ticker}")
            ))
            if selected_page == "Filing Comparison"
            else True
        )

        if run_comparison:


            with st.spinner("Comparing SEC filings..."):

                try:

                    def load_risk_factors(filepath):

                        raw_text = extract_filing_text(filepath)
                        clean_text = clean_filing_text(raw_text)

                        return extract_section(
                            clean_text,
                            "1A",
                            "1B"
                        )

                    # Historical selections apply ONLY to Filing Comparison.
                    # Other research pages retain their existing default pair.
                    if selected_page == "Filing Comparison":
                        pair = st.session_state.get(f"filing_pair_{diff_ticker}")
                        if not pair:
                            st.info("Select two annual filings and click Compare Selected 10-Ks.")
                            st.stop()
                        old_file, new_file = Path(pair[0]), Path(pair[1])
                    else:
                        recent_pair = get_recent_10k_with_urls(diff_ticker, limit=2)
                        if len(recent_pair) < 2:
                            st.warning("Two recent annual SEC 10-Ks are required.")
                            st.stop()
                        old_row, new_row = recent_pair.iloc[1], recent_pair.iloc[0]
                        old_file = download_10k(diff_ticker, old_row)
                        new_file = download_10k(diff_ticker, new_row)

                    old_text = load_risk_factors(old_file)
                    new_text = load_risk_factors(new_file)

                    diff_result = compare_filing_sections(
                        old_text,
                        new_text
                    )

                    matched = match_revised_disclosures(
                        diff_result,
                        threshold=0.75
                    )

                    formatting_only = []
                    wording_changes = []

                    for item in matched["revised"]:

                        if is_formatting_only_change(
                            item["old"],
                            item["new"]
                        ):
                            formatting_only.append(item)

                        else:
                            wording_changes.append(item)

                    if selected_page == "Filing Comparison":
                        st.success("Filing comparison completed.")

                        st.write("**Older filing:**", old_file.name)
                        st.write("**Newer filing:**", new_file.name)

                        col1, col2, col3, col4 = st.columns(4)

                        col1.metric(
                            "Wording Changes",
                            len(wording_changes)
                        )

                        col2.metric(
                            "Added",
                            matched["added_count"]
                        )

                        col3.metric(
                            "Removed",
                            matched["removed_count"]
                        )

                        col4.metric(
                            "Formatting-only",
                            len(formatting_only)
                        )

                        st.caption(
                            "Counts represent comparison units, "
                            "not confirmed material risk events."
                        )

                        st.markdown("### Revised Disclosures")

                        for index, item in enumerate(
                            wording_changes,
                            start=1
                        ):

                            with st.expander(
                                f"Revision {index} | "
                                f"Similarity: {item['similarity']:.1%}"
                            ):

                                st.markdown("**Previous disclosure**")
                                st.write(item["old"])

                                st.markdown("**Updated disclosure**")
                                st.write(item["new"])

                                if st.button(
                                    "Analyze with AI",
                                    key=f"ai_revision_{index}"
                                ):
                                    with st.spinner("Analyzing disclosure..."):
                                        try:
                                            analysis = analyze_disclosure(
                                                ticker=diff_ticker,
                                                section="Item 1A - Risk Factors",
                                                change_type="Revised",
                                                old_disclosure=item["old"],
                                                new_disclosure=item["new"]
                                            )
                                            st.session_state[
                                                f"ai_result_{diff_ticker}_{old_file.name}_{new_file.name}_{index}"
                                            ] = analysis


                                        except Exception as error:
                                            st.error(
                                                f"AI analysis failed: "
                                                f"{type(error).__name__}"
                                            )

                                research_key = (
                                    f"research_result_{diff_ticker}_"
                                    f"{old_file.name}_{new_file.name}_{index}"
                                )

                                if research_key not in st.session_state:

                                    cached_assessment = load_assessment(
                                        ticker=diff_ticker,
                                        section="Item 1A - Risk Factors",
                                        change_type="Revised",
                                        old_disclosure=item["old"],
                                        new_disclosure=item["new"]
                                    )

                                    if cached_assessment is not None:
                                        st.session_state[
                                            research_key
                                        ] = cached_assessment

                                if st.button(
                                    "Assess Research Priority",
                                    key=research_key + "_button"
                                ):
                                    with st.spinner(
                                        "Assessing research significance..."
                                    ):
                                        try:
                                            assessment = assess_research_priority(
                                                ticker=diff_ticker,
                                                section="Item 1A - Risk Factors",
                                                change_type="Revised",
                                                old_disclosure=item["old"],
                                                new_disclosure=item["new"]
                                            )

                                            st.session_state[
                                                research_key
                                            ] = assessment
                                            save_assessment(assessment)
                                        except Exception as error:
                                            st.error(
                                                "Research assessment failed: "
                                                f"{type(error).__name__}: {error}"
                                            )

                                if research_key in st.session_state:

                                    assessment = st.session_state[research_key]

                                    st.markdown("#### Research Assessment")

                                    col_a, col_b = st.columns(2)

                                    col_a.metric(
                                        "Change Significance",
                                        assessment.significance
                                    )

                                    col_b.metric(
                                        "Research Priority",
                                        assessment.research_priority
                                    )

                                    st.markdown("**Evidence from Disclosure**")

                                    for quote in assessment.evidence:
                                        st.code(quote, language=None)

                                    st.markdown("**Research Rationale**")
                                    st.write(assessment.rationale)

                                    st.markdown("**Follow-up Research Questions**")

                                    for question in assessment.research_questions:
                                        st.write(f"- {question}")

                                    st.caption(
                                        "Research priority reflects the importance "
                                        "of further investigation, not confirmed "
                                        "financial materiality or investment advice. "
                                        "Evidence quotations are checked against "
                                        "the supplied disclosure text. "
                                        "Human review remains required."
                                    )



                                result_key = (
                                    f"ai_result_{diff_ticker}_"
                                    f"{old_file.name}_{new_file.name}_{index}"
                                )

                                if result_key in st.session_state:

                                    analysis = st.session_state[result_key]

                                    st.markdown("#### AI Analysis")

                                    st.markdown("**Change Summary**")
                                    st.write(analysis.change_summary)

                                    st.markdown(
                                        "**Potential Business Implications**"
                                    )
                                    st.write(
                                        analysis.potential_business_implications
                                    )

                                    st.markdown("**Research Questions**")

                                    for question in analysis.research_questions:
                                        st.write(f"- {question}")

                                    st.caption(
                                        "AI-generated research assistance. "
                                        "Requires human review against "
                                        "the original SEC filing."
                                    )


                        st.markdown("### Research Priority Ranking")

                    # ==========================================
                    # DAY 9: COMPANY RESEARCH SIGNALS
                    # ==========================================

                    if selected_page == "Overview":
                        st.divider()

                        st.header("Company Research Signals")

                        st.caption(
                            "Integrated financial and disclosure research "
                            "signals for the selected company."
                        )


                    try:
                        # Retrieve financial data for the selected company.
                        company_financials = get_sec_financials(
                            diff_ticker
                        )

                        if (
                            company_financials is not None
                            and not company_financials.empty
                        ):
                            company_changes = (
                                calculate_financial_changes(
                                    company_financials
                                )
                            )
                        else:
                            company_changes = None


                        # Load only the current filing comparison's
                        # validated disclosure assessments.
                        dashboard_data = (
                            build_company_dashboard_data(
                                ticker=diff_ticker,
                                financial_changes=company_changes,
                                wording_changes=wording_changes,
                            )
                        )

                        company_signals = dashboard_data["company"]

                        if selected_page == "Overview":
                            # --------------------------------------
                            # Research overview
                            # --------------------------------------

                            st.subheader(
                                f"{diff_ticker} Research Overview"
                            )

                            overview_col1, overview_col2, overview_col3 = (
                                st.columns(3)
                            )

                            overview_col1.metric(
                                "Disclosure Changes",
                                dashboard_data["total_changes"]
                            )

                            overview_col2.metric(
                                "Assessed",
                                dashboard_data["assessed_count"]
                            )

                            overview_col3.metric(
                                "Not Assessed",
                                dashboard_data["not_assessed_count"]
                            )

                            # --------------------------------------
                            # Financial + disclosure signals
                            # --------------------------------------

                            financial_col, disclosure_col = (
                                st.columns(2)
                            )

                            with financial_col:

                                st.markdown(
                                    "#### Financial Signals"
                                )

                                financial = company_signals.financial

                                if financial is not None:

                                    st.metric(
                                        "Revenue Growth",
                                        (
                                            f"{financial.revenue_growth:.2f}%"
                                            if financial.revenue_growth
                                            is not None
                                            else "N/A"
                                        )
                                    )

                                    st.write(
                                        "**Growth Trend:**",
                                        financial.growth_trend
                                    )

                                    st.write(
                                        "**Margin Trend:**",
                                        financial.margin_trend
                                    )

                                    st.info(
                                        financial.research_signal
                                    )

                                    st.caption(
                                        "Source: SEC Company Facts | "
                                        f"Fiscal year end: "
                                        f"{financial.fiscal_year_end}"
                                    )

                                else:

                                    st.warning(
                                        "Financial data is unavailable."
                                    )

                            with disclosure_col:

                                st.markdown(
                                    "#### Disclosure Signals"
                                )

                                st.metric(
                                    "High Priority",
                                    company_signals.high_priority_count
                                )

                                st.metric(
                                    "Medium Priority",
                                    company_signals.medium_priority_count
                                )

                                st.metric(
                                    "Low Priority",
                                    company_signals.low_priority_count
                                )

                                st.write(
                                    "**Research Status:**",
                                    company_signals.overall_research_status
                                )

                                st.caption(
                                    "Source: validated SEC 10-K "
                                    "disclosure assessments."
                                )

                            # --------------------------------------
                            # Combined research interpretation
                            # --------------------------------------

                            st.subheader(
                                "Combined Research Interpretation"
                            )

                            st.info(
                                "Financial trends and disclosure "
                                "research priorities are presented "
                                "together for investigation. "
                                "Their coexistence does not establish "
                                "causation or imply an investment "
                                "recommendation."
                            )

                            # --------------------------------------
                            # Validated disclosure evidence
                            # --------------------------------------

                            if company_signals.disclosures:

                                with st.expander(
                                    "View Validated Disclosure Evidence"
                                ):

                                    for index, disclosure in enumerate(
                                        company_signals.disclosures,
                                        start=1
                                    ):

                                        st.markdown(
                                            f"**Assessment {index}**"
                                        )

                                        st.write(
                                            "Priority:",
                                            disclosure.research_priority
                                        )

                                        st.write(
                                            "Significance:",
                                            disclosure.significance
                                        )

                                        st.write(
                                            "Rationale:",
                                            disclosure.rationale
                                        )

                                        for quote in disclosure.evidence:
                                            st.code(
                                                quote,
                                                language=None
                                            )

                                        st.divider()

                            else:

                                st.caption(
                                    "No validated disclosure assessments "
                                    "are available for this comparison."
                                )

                            st.caption(
                                "Research signals require human review. "
                                "The system does not establish "
                                "financial causation or provide "
                                "investment advice."
                            )


                        # ======================================
                        # DAY 10: COMPANY RESEARCH PROFILE
                        # ======================================

                        if selected_page == "Overview":
                            st.divider()

                        # Always use the Filing Comparison ticker.
                        profile_ticker = diff_ticker.strip().upper()

                        # Official SEC company identity.
                        profile_submissions = (
                            get_company_submissions(
                                profile_ticker
                            )
                        )

                        # Official SEC 10-K sources.
                        profile_filings = (
                            get_recent_10k_with_urls(
                                profile_ticker,
                                limit=2
                            )
                        )

                        # Only load assessments belonging
                        # to the selected company and
                        # current filing comparison.
                        profile_assessments = (
                            load_current_disclosure_assessments(
                                ticker=profile_ticker,
                                wording_changes=wording_changes,
                            )
                        )

                        # Build the unified profile.
                        profile = build_company_profile(
                            ticker=profile_ticker,
                            submissions=profile_submissions,
                            financial_df=company_financials,
                            financial_changes=company_changes,
                            filings_df=profile_filings,
                            assessments=profile_assessments,
                            total_changes=len(wording_changes),
                        )

                        # Prevent accidental cross-company display.
                        if profile.identity.ticker != profile_ticker:
                            raise ValueError(
                                "Company Profile ticker mismatch."
                            )
                        if selected_page == "Overview":
                            render_company_profile(profile)
                        if selected_page == "Thesis Tracker":
                            render_thesis_monitoring(
                                ticker=profile_ticker,
                                financial_changes=company_changes,
                            )

                        # Day 13: Evidence-Linked Research Brief
                        if selected_page == "Research Brief":
                            st.divider()

                        brief_theses = load_theses(profile_ticker)

                        brief_monitoring = monitor_company_theses(
                            ticker=profile_ticker,
                            theses=brief_theses,
                            financial_changes=company_changes,
                        )

                        brief = build_research_brief(
                            profile=profile,
                            theses=brief_theses,
                            monitoring_results=brief_monitoring,
                        )

                        brief = check_brief_evidence(brief)

                        # Day 14: Validate the completed Research Brief.
                        integrity_report = validate_brief_integrity(
                            brief=brief,
                            expected_ticker=profile_ticker,
                        )

                        # Do not display a failed brief as a normal result.
                        if selected_page == "Research Brief":

                            if integrity_report.passed:
                                render_research_brief(brief)

                            else:
                                st.error(
                                    "Research Brief integrity check failed. "
                                    "Please review the errors below."
                                )

                        # Full integrity report belongs to Investment Memo only.
                        if selected_page == "Investment Memo":
                            render_integrity_report(integrity_report)

                        # Day 15: Investment Memo PDF Export
                        if selected_page == "Investment Memo":
                            st.divider()

                        if selected_page == "Investment Memo":
                            st.subheader("Investment Memo Export")

                            st.caption(
                                "Download an evidence-linked research memorandum "
                                "containing financial data, SEC filing sources, "
                                "investment theses, and integrity warnings."
                            )

                            if integrity_report.passed:

                                try:
                                    memo_pdf = export_investment_memo(
                                        brief=brief,
                                        integrity_report=integrity_report,
                                    )

                                    st.download_button(
                                        label="Download Investment Memo (PDF)",
                                        data=memo_pdf,
                                        file_name=(
                                            f"{profile_ticker}_Investment_Memo.pdf"
                                        ),
                                        mime="application/pdf",
                                        key=f"download_memo_{profile_ticker}",
                                        use_container_width=True,
                                    )

                                    st.caption(
                                        "Research memorandum generated from "
                                        "the currently selected company. "
                                        "Human review remains required."
                                    )

                                except ValueError as error:
                                    st.error(
                                        f"PDF export unavailable: {error}"
                                    )

                            else:
                                st.warning(
                                    "PDF export is disabled because the "
                                    "Research Brief did not pass its "
                                    "structural integrity check."
                                )


                    except Exception as error:

                        st.error(
                            "Unable to build Company Research Signals: "
                            f"{error}"
                        )

                    saved_assessments = []

                    # Save existing session results to persistent storage.
                    for index, item in enumerate(
                        wording_changes,
                        start=1
                    ):
                        session_key = (
                            f"research_result_{diff_ticker}_"
                            f"{old_file.name}_{new_file.name}_{index}"
                        )

                        if session_key in st.session_state:
                            save_assessment(
                                st.session_state[session_key]
                            )

                    for index, item in enumerate(
                        wording_changes,
                        start=1
                    ):

                        assessment = load_assessment(
                            ticker=diff_ticker,
                            section="Item 1A - Risk Factors",
                            change_type="Revised",
                            old_disclosure=item["old"],
                            new_disclosure=item["new"]
                        )

                        if assessment is not None:
                            saved_assessments.append(assessment)

                    # Build ranking rows with real disclosure numbers.
                    # Unassessed disclosures remain identifiable.

                    ranked_assessments = rank_assessments(
                        saved_assessments
                    )

                    ranking_rows = []

                    for rank, assessment in enumerate(
                        ranked_assessments,
                        start=1
                    ):

                        assessment_id = make_assessment_id(
                            assessment.ticker,
                            assessment.section,
                            assessment.change_type,
                            assessment.old_disclosure,
                            assessment.new_disclosure
                        )

                        revision_number = None

                        for index, item in enumerate(
                            wording_changes,
                            start=1
                        ):

                            current_id = make_assessment_id(
                                diff_ticker,
                                "Item 1A - Risk Factors",
                                "Revised",
                                item["old"],
                                item["new"]
                            )

                            if current_id == assessment_id:
                                revision_number = index
                                break

                        ranking_rows.append({
                            "Rank": rank,
                            "Revision": revision_number,
                            "Significance": assessment.significance,
                            "Research Priority": assessment.research_priority,
                            "Evidence Count": len(assessment.evidence),
                            "Rationale": assessment.rationale,
                            "Status": "Assessed"
                        })

                    assessed_revision_numbers = {
                        row["Revision"]
                        for row in ranking_rows
                    }

                    for index, item in enumerate(
                        wording_changes,
                        start=1
                    ):

                        if index not in assessed_revision_numbers:

                            ranking_rows.append({
                                "Rank": None,
                                "Revision": index,
                                "Significance": "Not Assessed",
                                "Research Priority": "Not Assessed",
                                "Evidence Count": 0,
                                "Rationale": "",
                                "Status": "Pending"
                            })



                    assessed_count = len(saved_assessments)

                    if selected_page == "Filing Comparison":
                        col_a, col_b, col_c = st.columns(3)

                        col_a.metric(
                            "Total Wording Changes",
                            len(wording_changes)
                        )

                        col_b.metric(
                            "Assessed",
                            assessed_count
                        )

                        col_c.metric(
                            "Not Assessed",
                            len(wording_changes) - assessed_count
                        )

                        st.caption(
                            "Only saved AI assessments are ranked. "
                            "Unassessed disclosures are not automatically "
                            "classified as Low Priority."
                        )


                        if ranking_rows:

                            priority_filter = st.selectbox(
                                "Filter by Research Priority",
                                [
                                    "All",
                                    "High",
                                    "Medium",
                                    "Low",
                                    "Not Assessed"
                                ],
                                key="research_priority_filter"
                            )

                            if priority_filter == "All":
                                filtered_rows = ranking_rows
                            else:
                                filtered_rows = [
                                    row for row in ranking_rows
                                    if row["Research Priority"]
                                    == priority_filter
                                ]

                            st.dataframe(
                                filtered_rows,
                                use_container_width=True,
                                hide_index=True
                            )

                            st.caption(
                                f"Showing {len(filtered_rows)} of "
                                f"{len(ranking_rows)} disclosure changes."
                            )


                        else:
                            st.info(
                                "No wording changes available for ranking."
                            )

                        with st.expander(
                            f"Unmatched Added ({matched['added_count']})"
                        ):

                            for item in matched["added"]:
                                st.write(item)
                                st.divider()

                        with st.expander(
                            f"Unmatched Removed ({matched['removed_count']})"
                        ):

                            for item in matched["removed"]:
                                st.write(item)
                                st.divider()

                        with st.expander(
                            f"Formatting-only ({len(formatting_only)})"
                        ):

                            for item in formatting_only:
                                st.write("OLD:", item["old"])
                                st.write("NEW:", item["new"])
                                st.divider()

                except Exception as error:

                    st.error(
                        f"Filing comparison failed: {error}"
                    )
