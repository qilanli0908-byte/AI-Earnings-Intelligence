
import streamlit as st

from src.brief_integrity import BriefIntegrityReport


def render_integrity_report(
    report: BriefIntegrityReport,
) -> None:
    """
    Display Research Brief integrity results.

    A passed structural check does not mean the
    investment claims have been fact-verified.
    """
    st.subheader("Research Brief Integrity Check")

    if report.passed:
        st.success(
            "Structural integrity check passed. "
            "This does not constitute factual verification."
        )
    else:
        st.error(
            f"Integrity check failed: "
            f"{len(report.errors)} error(s) detected."
        )

    col1, col2 = st.columns(2)

    col1.metric("Errors", len(report.errors))
    col2.metric("Warnings", len(report.warnings))

    if report.errors:
        with st.expander("Integrity Errors", expanded=True):
            for error in report.errors:
                st.write(f"- {error}")

    if report.warnings:
        with st.expander("Integrity Warnings", expanded=False):
            for warning in report.warnings:
                st.write(f"- {warning}")

    st.caption(
        f"Company: {report.ticker} | "
        "Human review remains required."
    )
