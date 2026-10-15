
from urllib.parse import urlparse

from src.brief_models import ResearchBrief


def is_sec_url(url: str) -> bool:
    """
    Check whether a URL points to an HTTPS SEC domain.

    This validates URL structure, not the contents of
    the underlying SEC filing.
    """
    if not url:
        return False

    parsed = urlparse(url)

    return (
        parsed.scheme == "https"
        and parsed.hostname in ("sec.gov", "www.sec.gov")
    )


def check_brief_evidence(brief: ResearchBrief) -> ResearchBrief:
    """
    Apply conservative evidence metadata checks.

    Never automatically promote evidence to Verified.
    """
    for section in brief.sections:
        for evidence in section.evidence:

            if evidence.verification_status == "Verified":
                evidence.verification_status = "Requires Review"

            if evidence.evidence_type in (
                "SEC Financial",
                "SEC Filing",
            ):
                if not is_sec_url(evidence.source_url):
                    evidence.verification_status = "Requires Review"

                if not evidence.citation.strip():
                    evidence.verification_status = "Requires Review"

            if evidence.evidence_type == "Investment Thesis":
                if evidence.verification_status == "Verified":
                    evidence.verification_status = "Requires Review"

        section.requires_human_review = True

    brief.requires_human_review = True

    return brief
