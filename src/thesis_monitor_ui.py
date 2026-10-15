
import streamlit as st

from src.thesis_integration import monitor_company_theses
from src.thesis_storage import load_theses


def render_thesis_monitoring(ticker, financial_changes):
    """
    Display saved investment theses and their latest
    rule-based financial monitoring results.
    """
    ticker = ticker.strip().upper()

    st.subheader(f"{ticker} Investment Thesis Tracker")

    st.caption(
        "Rule-based research monitoring using SEC financial signals. "
        "Results are not investment recommendations."
    )

    theses = load_theses(ticker)

    if not theses:
        st.info(
            f"No saved investment theses for {ticker} yet. "
            "Thesis creation UI will be added in a later stage."
        )
        return

    results = monitor_company_theses(
        ticker=ticker,
        theses=theses,
        financial_changes=financial_changes,
    )

    result_map = {
        result.thesis_id: result
        for result in results
    }

    for thesis in theses:
        result = result_map[thesis.thesis_id]

        with st.expander(
            f"{thesis.thesis_type} | {thesis.statement}",
            expanded=True,
        ):
            st.write(f"**Thesis ID:** {thesis.thesis_id}")

            st.write(f"**Latest Financial Signal:** {result.financial_signal}")

            st.write(f"**Monitoring Impact:** {result.impact}")

            st.write(result.explanation)

            st.write(
                "**Human Review Required:** "
                f"{'Yes' if result.requires_human_review else 'No'}"
            )

            if thesis.evidence:
                st.markdown("**Evidence**")

                for evidence in thesis.evidence:
                    st.write(
                        f"- {evidence.description} "
                        f"({evidence.status})"
                    )

                    if evidence.source_url:
                        st.caption(evidence.source_url)

            if thesis.hypotheses:
                st.markdown("**Hypotheses**")

                for hypothesis in thesis.hypotheses:
                    st.write(
                        f"- {hypothesis.description} "
                        f"({hypothesis.status})"
                    )
