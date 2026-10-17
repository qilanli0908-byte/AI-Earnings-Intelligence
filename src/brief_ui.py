"""Readable Research Brief UI. Presentation only; never changes research data."""
import re
import streamlit as st
from src.brief_models import ResearchBrief


def _summary_lines(summary):
    """Preserve paragraph boundaries without interpreting source text as Markdown."""
    for line in summary.splitlines():
        line = line.strip()
        if line:
            yield line


def _source_id(description):
    match = re.search(r"\b(?:FIN-\d+|FILING-\d+|PASSAGE-\d+-\d+)\b", description)
    return match.group(0) if match else None


def _render_offline_summary(summary):
    """Group the saved five-stage narrative; do not infer new research conclusions."""
    stage = re.compile(r"^([1-5])\. (Thesis Decomposition|SEC Evidence Retrieval|Supporting vs\. Contradicting Evidence|Research Gap Identification|Evidence-linked Assessment)")
    for line in _summary_lines(summary):
        if line == "AI DEEP THESIS ANALYSIS - FIVE-STAGE OFFLINE SCAFFOLD":
            st.markdown("#### Five-stage offline research")
        elif stage.match(line):
            st.markdown(f"**{line}**")
        elif line.startswith(("Research gap:", "Monitor:")):
            st.write("• " + line)
        elif line.startswith(("OFFLINE MOCK DEMO", "Assessment:", "Supporting evidence established", "Contradicting evidence established")):
            st.write(line)
        else:
            st.write(line)


def _render_sources(section):
    offline = section.title == "Offline Research Demo"
    st.markdown("#### Available Research Sources" if offline else "#### Source Documents / Saved Evidence")
    if offline:
        st.caption("FIN = financial context; FILING = metadata; PASSAGE = retrieval candidate. None is verified thesis support or contradiction.")
    st.caption(f"{len(section.evidence)} source item(s). Open any row for its complete saved description, citation, and original link.")
    for index, evidence in enumerate(section.evidence, 1):
        identifier = _source_id(evidence.description)
        heading = (f"{identifier} · {evidence.evidence_type}" if identifier else
                   f"Source {index:02d} · {evidence.evidence_type}")
        with st.expander(heading, expanded=False):
            st.write(evidence.description)  # No slicing: no mid-word truncation.
            st.caption(f"Type: {evidence.evidence_type} | Status: {evidence.verification_status}")
            if evidence.citation:
                st.write("Citation:", evidence.citation)
            if evidence.source_url:
                st.link_button("Open original SEC source", evidence.source_url)


def render_research_brief(brief: ResearchBrief) -> None:
    st.subheader("Research Brief")
    st.caption(f"{brief.company_name} | Fiscal Year End: {brief.fiscal_year_end}")
    st.info("Research workspace · Source-linked context · Human review required. Not investment advice.")
    section_count = len(brief.sections)
    source_count = sum(len(section.evidence) for section in brief.sections)
    a, b = st.columns(2)
    a.metric("Research sections", section_count)
    b.metric("Saved source items", source_count)
    st.caption("Sections are organized for quick reading. Expand individual sources to inspect full text and citations.")

    for section in brief.sections:
        expanded = section.title in ("Financial Momentum", "Investment Theses")
        with st.expander(section.title, expanded=expanded):
            if section.title == "Financial Momentum":
                def extract(pattern):
                    match = re.search(pattern, section.summary)
                    return match.group(1) if match else "N/A"
                values = (
                    ("Revenue", extract(r"Revenue: (\$[\d,.]+B)")),
                    ("Net Income", extract(r"Net income: (\$[\d,.]+B)")),
                    ("Revenue Growth", extract(r"Revenue growth: ([\d.-]+%)")),
                    ("Net Margin", extract(r"Net margin: ([\d.-]+%)")),
                )
                for col, (label, value) in zip(st.columns(4), values):
                    col.metric(label, value)
                st.caption("Company-wide historical context; metric/tag and period mapping require review.")
            elif section.title == "Offline Research Demo":
                _render_offline_summary(section.summary)
            elif section.title == "Investment Theses":
                for line in _summary_lines(section.summary):
                    if line in ("BULL THESIS", "BEAR THESIS"):
                        st.markdown(f"#### {line.title()}")
                    else:
                        st.write(line)
            else:
                for line in _summary_lines(section.summary):
                    st.write(line)
            if section.evidence:
                _render_sources(section)
            if section.requires_human_review:
                st.caption("Human review required")
