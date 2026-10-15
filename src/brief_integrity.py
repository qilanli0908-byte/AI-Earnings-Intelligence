
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from src.brief_models import ResearchBrief


REQUIRED_SECTIONS = (
    "Company Overview",
    "Financial Momentum",
    "SEC Filing Sources",
    "Research Signals",
    "Investment Theses",
    "Thesis Monitoring",
)

VALID_STATUSES = {
    "Verified",
    "Unverified",
    "Requires Review",
}


@dataclass
class BriefIntegrityReport:
    ticker: str
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_brief_integrity(
    brief: ResearchBrief,
    expected_ticker: str,
) -> BriefIntegrityReport:
    """
    Check structural consistency and evidence metadata.

    This does NOT verify the factual accuracy of SEC claims.
    No network or AI API calls are made.
    """
    errors = []
    warnings = []

    expected = expected_ticker.strip().upper()
    actual = brief.ticker.strip().upper()

    # 1. Company identity
    if not re.fullmatch(r"[A-Z0-9.-]{1,12}", expected):
        errors.append("Invalid expected ticker")

    if actual != expected:
        errors.append(
            f"Company mismatch: expected {expected}, got {actual}"
        )

    if not brief.company_name.strip():
        errors.append("Missing company name")

    if not brief.fiscal_year_end.strip():
        errors.append("Missing fiscal-year end")

    # 2. Required sections
    titles = [section.title for section in brief.sections]

    for title in REQUIRED_SECTIONS:
        if title not in titles:
            errors.append(f"Missing required section: {title}")

    if len(titles) != len(set(titles)):
        errors.append("Duplicate section titles detected")

    # 3. Evidence metadata
    for section in brief.sections:
        if not section.summary.strip():
            warnings.append(
                f"Empty summary: {section.title}"
            )

        if not section.requires_human_review:
            errors.append(
                f"Human review disabled: {section.title}"
            )

        for index, evidence in enumerate(
            section.evidence,
            start=1,
        ):
            label = f"{section.title} / Evidence {index}"

            if not evidence.description.strip():
                errors.append(f"Missing description: {label}")

            if evidence.verification_status not in VALID_STATUSES:
                errors.append(f"Invalid evidence status: {label}")

            if evidence.verification_status == "Verified":
                errors.append(
                    f"Unreviewed brief cannot claim Verified: {label}"
                )

            if evidence.source_url:
                parsed = urlparse(evidence.source_url)

                if (
                    parsed.scheme != "https"
                    or parsed.hostname not in (
                        "sec.gov",
                        "www.sec.gov",
                    )
                ):
                    errors.append(
                        f"Invalid SEC source URL: {label}"
                    )

            if evidence.evidence_type == "SEC Filing":
                if not evidence.source_url:
                    errors.append(
                        f"Missing filing source URL: {label}"
                    )

                if not evidence.citation.strip():
                    errors.append(
                        f"Missing filing citation: {label}"
                    )

            if evidence.evidence_type == "SEC Financial":
                if not evidence.source_url:
                    warnings.append(
                        f"Financial source URL not linked: {label}"
                    )

                if not evidence.citation.strip():
                    warnings.append(
                        f"Financial citation not linked: {label}"
                    )

    # 4. Human review must remain enabled
    if not brief.requires_human_review:
        errors.append("Brief must require human review")

    return BriefIntegrityReport(
        ticker=actual,
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
