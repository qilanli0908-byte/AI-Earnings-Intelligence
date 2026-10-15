
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
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

    story = []

    def add(text, style="MemoBody"):
        story.append(
            Paragraph(safe_text(text), styles[style])
        )

    # Cover / Header
    add("AI EARNINGS INTELLIGENCE", "MemoSmall")
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

    story.append(Spacer(1, 16))

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


        for index, evidence in enumerate(
            section.evidence,
            start=1,
        ):
            add(
                f"Evidence {index}: {evidence.description}",
                "MemoBody",
            )

            add(
                f"Type: {evidence.evidence_type} | "
                f"Status: {evidence.verification_status}",
                "MemoSmall",
            )

            if evidence.citation:
                add(
                    f"Citation: {evidence.citation}",
                    "MemoSmall",
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
                            styles["MemoSmall"],
                        )
                    )
                else:
                    add(
                        f"Source URL requires review: {source_url}",
                        "MemoSmall",
                    )


        if section.requires_human_review:
            add("Human review required.", "MemoSmall")

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

    document.build(story)

    return buffer.getvalue()
