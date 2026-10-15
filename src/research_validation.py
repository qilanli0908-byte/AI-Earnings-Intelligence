
from src.research_models import ResearchAssessment


ALLOWED_LEVELS = {"Low", "Medium", "High"}


def validate_research_assessment(
    assessment: ResearchAssessment
) -> bool:
    """
    Validate research assessment structure and evidence grounding.

    Evidence must be an exact substring of the supplied
    old or new disclosure.

    This does not prove that the AI's interpretation is correct.
    """

    if not isinstance(assessment, ResearchAssessment):
        raise TypeError("Expected a ResearchAssessment object.")

    if assessment.significance not in ALLOWED_LEVELS:
        raise ValueError("Invalid significance category.")

    if assessment.research_priority not in ALLOWED_LEVELS:
        raise ValueError("Invalid research priority category.")

    if not isinstance(assessment.rationale, str):
        raise ValueError("Rationale must be a string.")

    if not assessment.rationale.strip():
        raise ValueError("Rationale cannot be empty.")

    if not isinstance(assessment.evidence, list):
        raise ValueError("Evidence must be a list.")

    if not assessment.evidence:
        raise ValueError("At least one evidence quotation is required.")

    source_texts = (
        assessment.old_disclosure or "",
        assessment.new_disclosure or ""
    )

    for quote in assessment.evidence:

        if not isinstance(quote, str) or not quote.strip():
            raise ValueError(
                "Evidence must contain non-empty strings."
            )

        if not any(quote in source for source in source_texts):
           raise ValueError(
    "Evidence quotation was not found in the provided disclosure text. "
    f"Rejected quotation: {quote[:120]!r}"
)

    if not isinstance(assessment.research_questions, list):
        raise ValueError("Research questions must be a list.")

    for question in assessment.research_questions:

        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                "Research questions must be non-empty strings."
            )

    if assessment.requires_human_review is not True:
        raise ValueError("Human review must remain enabled.")

    return True
