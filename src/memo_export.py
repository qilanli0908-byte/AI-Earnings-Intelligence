
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
    Table, TableStyle, PageBreak,
)

from src.brief_models import ResearchBrief
from src.brief_integrity import BriefIntegrityReport
from urllib.parse import urlparse
from xml.sax.saxutils import quoteattr


NAVY = colors.HexColor("#14263D")
MUTED = colors.HexColor("#607086")


def safe_text(value) -> str:
    """
    Escape PDF paragraph markup and normalize characters
    for ReportLab's built-in Helvetica font.
    """
    text = str(value)

    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
    }

    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    # This first version uses the built-in Helvetica font.
    # Avoid silently replacing unsupported non-Latin characters.
    if not text.isascii():
        raise ValueError(
            "PDF contains non-ASCII text. "
            "A Unicode font must be configured before exporting."
        )

    return escape(text)


def export_investment_memo(
    brief: ResearchBrief,
    integrity_report: BriefIntegrityReport,
) -> bytes:
    """
    Export an existing, structurally validated Research Brief.

    Does not call SEC or OpenAI.
    Does not save files or modify the input objects.
    """

    if not integrity_report.passed:
        raise ValueError(
            "Cannot export a Research Brief with integrity errors"
        )

    if integrity_report.ticker != brief.ticker:
        raise ValueError(
            "Integrity report and Research Brief ticker mismatch"
        )

    if not brief.requires_human_review:
        raise ValueError(
            "Research Brief must retain human review status"
        )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48,
        title=f"{brief.ticker} Investment Research Memo",
        author="AI Earnings Intelligence",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="MemoTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=26,
            textColor=NAVY,
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MemoSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=17,
            textColor=NAVY,
            spaceBefore=15,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MemoBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MemoSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=MUTED,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MemoDisclaimer",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            textColor=NAVY,
            alignment=TA_CENTER,
        )
    )

    styles.add(ParagraphStyle(name="MemoKicker", parent=styles["MemoSmall"], fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=5))
    styles.add(ParagraphStyle(name="MemoSource", parent=styles["MemoSmall"], fontSize=7.5, leading=10, spaceAfter=3))
    styles.add(ParagraphStyle(name="MemoMetricLabel", parent=styles["MemoSmall"], fontName="Helvetica-Bold", fontSize=7, leading=10, spaceAfter=3))
    styles.add(ParagraphStyle(name="MemoMetricValue", parent=styles["MemoBody"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=NAVY, spaceAfter=1))
    styles.add(ParagraphStyle(name="MemoThesis", parent=styles["MemoBody"], fontName="Helvetica-Bold", fontSize=10, leading=15, textColor=NAVY, spaceAfter=5))
    styles.add(ParagraphStyle(name="MemoAppendix", parent=styles["MemoSmall"], fontSize=7.2, leading=10, spaceAfter=2))

    story = []

    def add(text, style="MemoBody"):
        story.append(
            Paragraph(safe_text(text), styles[style])
        )

    # Cover / Header
    add("AI EARNINGS INTELLIGENCE  /  EQUITY RESEARCH", "MemoKicker")
    add(
        f"{brief.ticker} | Investment Research Memo",
        "MemoTitle",
    )

    add(
        f"{brief.company_name} | "
        f"Fiscal Year End: {brief.fiscal_year_end}",
        "MemoBody",
    )

    add(
        f"Generated: {brief.generated_at}",
        "MemoSmall",
    )

    story.append(Spacer(1, 10))

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=NAVY,
        )
    )

    story.append(Spacer(1, 12))

    add(
        "RESEARCH STATUS: HUMAN REVIEW REQUIRED",
        "MemoDisclaimer",
    )

    add(
        "This document organizes existing research data. "
        "It is not an investment recommendation.",
        "MemoDisclaimer",
    )

    # Editorial executive summary, using only existing brief content.
    by_title = {section.title: section for section in brief.sections}
    thesis_section = by_title.get("Investment Theses")
    financial_section = by_title.get("Financial Momentum")
    demo_section = by_title.get("Offline Research Demo")
    thesis_statement = "No saved investment thesis."
    if thesis_section:
        for line in thesis_section.summary.splitlines():
            if line.startswith("Core Statement: "):
                thesis_statement = line.partition(": ")[2]
                break
    assessment = "Not assessed"
    if demo_section:
        for line in demo_section.summary.splitlines():
            if line.startswith("Assessment: "):
                assessment = line.partition(": ")[2].split(" (not a verified")[0]
                break
    add("EXECUTIVE RESEARCH SUMMARY", "MemoSection")
    add("INVESTMENT THESIS  /  USER-SAVED, NOT VALIDATED", "MemoMetricLabel")
    add(thesis_statement, "MemoThesis")
    metrics = [
        ("RESEARCH ASSESSMENT", assessment),
        ("VERIFIED BY OFFLINE MOCK", "0 supporting / 0 contradicting" if demo_section else "No offline analysis supplied"),
    ]
    if financial_section:
        import re
        fs = financial_section.summary
        for label, pattern in [
            ("REVENUE", r"Revenue: (\$[\d,.]+B)"),
            ("REVENUE GROWTH", r"Revenue growth: ([\d,.]+%)"),
            ("NET MARGIN", r"Net margin: ([\d,.]+%)"),
        ]:
            match = re.search(pattern, fs)
            if match:
                metrics.append((label, match.group(1)))
    cells = [
        [Paragraph(safe_text(label), styles["MemoMetricLabel"]),
         Paragraph(safe_text(value), styles["MemoMetricValue"])]
        for label, value in metrics
    ]
    metric_rows = []
    for i in range(0, len(cells), 2):
        row = []
        for pair in cells[i:i+2]:
            row.append([pair[0], pair[1]])
        if len(row) == 1:
            row.append("")
        metric_rows.append(row)
    metric_table = Table(metric_rows, colWidths=[247, 247], hAlign="LEFT")
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6FB")),
        ("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#DEE6F0")),
        ("INNERGRID", (0, 0), (-1, -1), .4, colors.HexColor("#DEE6F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 10))
    add("Research status: human review required. Financial figures are company-wide context, not proof of the thesis.", "MemoSmall")
    if demo_section:
        gaps = [line.partition("Research gap: ")[2] for line in demo_section.summary.splitlines()
                if line.startswith("Research gap: ")]
        if gaps:
            add("PRIORITY RESEARCH GAPS", "MemoKicker")
            for i, gap in enumerate(gaps[:3], 1):
                add(f"{i}. {gap}", "MemoSmall")
    add("Offline retrieval identifies candidate SEC passages only; no LLM interpretation or verified investment conclusion.", "MemoSmall")
    story.append(HRFlowable(width="100%", thickness=.7, color=colors.HexColor("#DEE6F0")))
    story.append(Spacer(1, 8))

    # Keep the long offline source inventory separate from the narrative.
    appendix_section = by_title.get("Offline Research Demo")
    # Research sections
    for section in brief.sections:

        # Keep the section heading with its first paragraph,
        # but allow long research sections to flow across pages.
        summary_lines = section.summary.splitlines()

        if not summary_lines:
            summary_lines = [""]

        first_line = summary_lines[0]

        story.append(
            KeepTogether([
                Paragraph(
                    safe_text(section.title),
                    styles["MemoSection"],
                ),
                Paragraph(
                    safe_text(first_line),
                    styles["MemoBody"],
                ),
            ])
        )

        for line in summary_lines[1:]:
            if not line.strip():
                story.append(Spacer(1, 6))
                continue

            if section.title == "Investment Theses" and (
                line.startswith("BULL THESIS")
                or line.startswith("BEAR THESIS")
            ):
                story.append(
                    Paragraph(
                        safe_text(line),
                        styles["MemoSection"],
                    )
                )
            else:
                story.append(
                    Paragraph(
                        safe_text(line),
                        styles["MemoBody"],
                    )
                )


        is_inventory = section.title == "Offline Research Demo"
        if is_inventory:
            continue
        for index, evidence in enumerate(section.evidence, start=1):
            label = "Research Source" if is_inventory else "Source / Saved Evidence"
            description = evidence.description
            if is_inventory and len(description) > 330:
                description = description[:327].rsplit(" ", 1)[0] + "... [excerpt; open SEC source for full context]"
            add(f"{label} {index}: {description}", "MemoSource" if is_inventory else "MemoBody")

            add(
                f"Type: {evidence.evidence_type} | "
                f"Status: {evidence.verification_status}",
                "MemoSource" if is_inventory else "MemoSmall",
            )

            if evidence.citation:
                add(
                    f"Citation: {evidence.citation}",
                    "MemoSource" if is_inventory else "MemoSmall",
                )

            if evidence.source_url:
                source_url = evidence.source_url.strip()
                parsed = urlparse(source_url)

                # Only create clickable links to approved SEC hosts.
                if (
                    parsed.scheme == "https"
                    and parsed.hostname in (
                        "sec.gov",
                        "www.sec.gov",
                        "data.sec.gov",
                    )
                ):
                    link_markup = (
                        f'<link href={quoteattr(source_url)} '
                        f'color="#245A81">'
                        f'{safe_text(source_url)}'
                        f'</link>'
                    )

                    story.append(
                        Paragraph(
                            "SEC Source: " + link_markup,
                            styles["MemoSource" if is_inventory else "MemoSmall"],
                        )
                    )
                else:
                    add(
                        f"Source URL requires review: {source_url}",
                        "MemoSmall",
                    )


        if section.requires_human_review:
            add("Human review required.", "MemoSmall")

    # Separate compact appendix. Source labels and clickable SEC links are retained.
    if appendix_section and appendix_section.evidence:
        story.append(PageBreak())
        add("APPENDIX  /  AVAILABLE SEC RESEARCH SOURCES", "MemoSection")
        add("FIN = consolidated financial context; FILING = filing metadata; PASSAGE = keyword-ranked candidate text. None establishes verified support or contradiction.", "MemoSmall")
        for index, evidence in enumerate(appendix_section.evidence, 1):
            description = evidence.description
            if len(description) > 270:
                description = description[:267].rsplit(" ", 1)[0] + "... [excerpt; open SEC source for full context]"
            story.append(KeepTogether([
                Paragraph(safe_text(f"RESEARCH SOURCE {index:02d}  /  {description}"), styles["MemoAppendix"]),
                Paragraph(safe_text(f"{evidence.evidence_type} | {evidence.verification_status}"), styles["MemoAppendix"]),
            ]))
            if evidence.citation:
                add(f"Citation: {evidence.citation}", "MemoAppendix")
            if evidence.source_url:
                source_url = evidence.source_url.strip()
                parsed = urlparse(source_url)
                if parsed.scheme == "https" and parsed.hostname in ("sec.gov", "www.sec.gov", "data.sec.gov"):
                    markup = f'<link href={quoteattr(source_url)} color="#245A81">Open original SEC source</link>'
                    story.append(Paragraph(markup, styles["MemoAppendix"]))
                else:
                    add(f"Source URL requires review: {source_url}", "MemoAppendix")
            story.append(Spacer(1, 5))
        add("Human review required. Candidate excerpts are not verified investment evidence.", "MemoSmall")

    # Integrity summary
    story.append(Spacer(1, 12))

    add("Research Integrity Summary", "MemoSection")

    add(
        f"Structural Errors: {len(integrity_report.errors)} | "
        f"Warnings: {len(integrity_report.warnings)}"
    )

    for warning in integrity_report.warnings:
        add(f"Warning: {warning}", "MemoSmall")

    story.append(Spacer(1, 14))

    add(
        "Structural integrity does not establish factual "
        "accuracy. Verify financial figures, source documents, "
        "research assessments, and assumptions independently "
        "before relying on this memorandum.",
        "MemoSmall",
    )

    def footer(canvas, doc):
        canvas.saveState()
        width, _ = A4
        canvas.setStrokeColor(colors.HexColor("#DEE6F0"))
        canvas.line(48, 37, width - 48, 37)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(48, 26, f"{brief.ticker}  /  AI Earnings Intelligence  /  Human review required")
        canvas.drawRightString(width - 48, 26, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)

    return buffer.getvalue()
