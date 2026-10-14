
from src.ai_models import DisclosureAnalysis


def validate_analysis(analysis: DisclosureAnalysis) -> bool:
    """
    Validate the structure of an AI-generated disclosure analysis.

    This checks data quality, not factual accuracy.
    """

    if not isinstance(analysis, DisclosureAnalysis):
        raise TypeError("Expected a DisclosureAnalysis object.")

    if not isinstance(analysis.change_summary, str):
        raise ValueError("change_summary must be a string.")

    if not analysis.change_summary.strip():
        raise ValueError("change_summary cannot be empty.")

    if not isinstance(analysis.potential_business_implications, str):
        raise ValueError(
            "potential_business_implications must be a string."
        )

    if not analysis.potential_business_implications.strip():
        raise ValueError(
            "potential_business_implications cannot be empty."
        )

    if not isinstance(analysis.research_questions, list):
        raise ValueError("research_questions must be a list.")

    for question in analysis.research_questions:
        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                "Every research question must be a non-empty string."
            )

    if analysis.requires_human_review is not True:
        raise ValueError("Human review must remain enabled.")

    return True
