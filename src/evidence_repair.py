
from dataclasses import replace

from src.research_models import ResearchAssessment
from src.research_validation import validate_research_assessment


LABELS = (
    "Old disclosure:",
    "New disclosure:",
    "Before:",
    "After:",
)


def repair_evidence(assessment: ResearchAssessment):
    """
    Repair only clearly identifiable AI-added quotation wrappers.

    Never rewrite, paraphrase, or fabricate SEC evidence.
    """

    source_texts = [
        assessment.old_disclosure or "",
        assessment.new_disclosure or "",
    ]

    repaired_evidence = []

    for original_quote in assessment.evidence:

        if not isinstance(original_quote, str):
            raise ValueError("Evidence must be a string.")

        quote = original_quote.strip()

        # Accept already valid exact quotations.
        if any(quote in source for source in source_texts):
            repaired_evidence.append(quote)
            continue

        # Remove an AI-added label only if present.
        for label in LABELS:
            if quote.startswith(label):
                quote = quote[len(label):].strip()
                break

        # Remove surrounding quotation marks only when
        # they are not part of the SEC source.
        if len(quote) >= 2 and (
            (quote.startswith('"') and quote.endswith('"'))
            or (quote.startswith("'") and quote.endswith("'"))
        ):
            unwrapped = quote[1:-1]

            if any(
                unwrapped in source
                for source in source_texts
            ):
                quote = unwrapped

        # Reject anything that still is not an exact substring.
        if not quote or not any(
            quote in source
            for source in source_texts
        ):
            raise ValueError(
                "Evidence repair failed. "
                "The quotation is not an exact SEC source substring."
            )

        repaired_evidence.append(quote)

    repaired = replace(
        assessment,
        evidence=repaired_evidence,
    )

    # Run the original strict validator again.
    validate_research_assessment(repaired)

    return repaired
