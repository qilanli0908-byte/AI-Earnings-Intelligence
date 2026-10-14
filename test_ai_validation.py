
from src.ai_models import DisclosureAnalysis


def validate_analysis(analysis):
    """Check the structure of an AI disclosure analysis."""

    assert isinstance(analysis, DisclosureAnalysis)

    assert isinstance(analysis.change_summary, str)
    assert analysis.change_summary.strip()

    assert isinstance(
        analysis.potential_business_implications, str
    )
    assert analysis.potential_business_implications.strip()

    assert isinstance(analysis.research_questions, list)

    assert all(
        isinstance(question, str) and question.strip()
        for question in analysis.research_questions
    )

    assert analysis.requires_human_review is True

    return True


sample = DisclosureAnalysis(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure="The company relies on external manufacturing capacity.",
    new_disclosure=(
        "The company relies on external manufacturing "
        "and advanced packaging capacity."
    ),
    change_summary=(
        "The revised wording explicitly mentions advanced "
        "packaging capacity."
    ),
    potential_business_implications=(
        "This may warrant further research. The wording alone "
        "does not establish that actual supplier dependence increased."
    ),
    research_questions=[
        "What prompted the additional disclosure?"
    ],
    model_name="offline-test",
    requires_human_review=True
)

assert validate_analysis(sample)

print("PASS: AI analysis structure validated.")
