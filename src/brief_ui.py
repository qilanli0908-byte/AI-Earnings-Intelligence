
import streamlit as st

from src.brief_models import ResearchBrief


def render_research_brief(brief: ResearchBrief) -> None:
    """
    Display a structured, evidence-linked research brief.
    """
    st.header(f"{brief.ticker} Research Brief")

    st.caption(
        f"{brief.company_name} | "
        f"Fiscal Year End: {brief.fiscal_year_end}"
    )

    st.warning(
        "This research brief organizes existing data and "
        "research signals. It is not an investment recommendation. "
        "Human review is required."
    )

    for section in brief.sections:
        with st.expander(section.title, expanded=True):
            if section.title == "Financial Momentum":
                import re

                summary = section.summary

                def extract(pattern):
                    match = re.search(pattern, summary)
                    return match.group(1) if match else "N/A"

                revenue = extract(r"Revenue: \$([\d.]+)B")
                net_income = extract(r"Net income: \$([\d.]+)B")
                growth = extract(r"Revenue growth: ([\d.-]+)%")
                margin = extract(r"Net margin: ([\d.-]+)%")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Revenue",
                    f"${revenue}B" if revenue != "N/A" else "N/A",
                )
                col2.metric(
                    "Net Income",
                    f"${net_income}B" if net_income != "N/A" else "N/A",
                )
                col3.metric(
                    "Revenue Growth",
                    f"{growth}%" if growth != "N/A" else "N/A",
                )
                col4.metric(
                    "Net Margin",
                    f"{margin}%" if margin != "N/A" else "N/A",
                )

            elif section.title == "Research Signals":
                for line in section.summary.splitlines():
                    if ": " in line:
                        label, value = line.split(": ", 1)
                        st.markdown(f"**{label}:** {value}")
                    else:
                        st.write(line)

            else:
                st.write(section.summary)


            if section.evidence:
                st.markdown("**Supporting Evidence / Sources**")

                for index, evidence in enumerate(
                    section.evidence,
                    start=1,
                ):
                    st.markdown(
                        f"**Evidence {index}:** "
                        f"{evidence.description}"
                    )

                    st.caption(
                        f"Type: {evidence.evidence_type} | "
                        f"Status: {evidence.verification_status}"
                    )

                    if evidence.citation:
                        st.write(
                            f"**Citation:** {evidence.citation}"
                        )

                    if evidence.source_url:
                        st.markdown(
                            f"[Open source document]"
                            f"({evidence.source_url})"
                        )

                    st.divider()

            if section.requires_human_review:
                st.caption("Human review required")
