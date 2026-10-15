
import re
from urllib.parse import urlparse

from src.thesis_models import InvestmentThesis


def validate_thesis(thesis: InvestmentThesis) -> None:
    """
    Validate thesis structure and evidence metadata.

    This checks source attribution, not factual accuracy.
    """
    if not re.fullmatch(r"[A-Z0-9.-]{1,12}", thesis.ticker):
        raise ValueError("Invalid thesis ticker")

    if not thesis.thesis_id.strip():
        raise ValueError("Thesis ID cannot be empty")

    if thesis.thesis_type not in ("Bull", "Bear"):
        raise ValueError("Thesis type must be Bull or Bear")

    if not thesis.statement.strip():
        raise ValueError("Thesis statement cannot be empty")

    for evidence in thesis.evidence:
        if not evidence.description.strip():
            raise ValueError("Evidence description cannot be empty")

        if evidence.status not in ("Verified", "Unverified"):
            raise ValueError("Invalid evidence status")

        if evidence.status == "Verified":
            parsed = urlparse(evidence.source_url)

            if (
                parsed.scheme != "https"
                or parsed.hostname not in ("sec.gov", "www.sec.gov")
            ):
                raise ValueError(
                    "Verified SEC evidence requires an HTTPS SEC URL"
                )

            if not evidence.citation.strip():
                raise ValueError(
                    "Verified evidence requires a specific citation"
                )

    for hypothesis in thesis.hypotheses:
        if not hypothesis.description.strip():
            raise ValueError("Hypothesis description cannot be empty")

        if hypothesis.status not in (
            "Unverified",
            "Supported",
            "Contradicted",
        ):
            raise ValueError("Invalid hypothesis status")
