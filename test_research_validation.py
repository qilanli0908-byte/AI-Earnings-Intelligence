
from src.research_models import ResearchAssessment
from src.research_validation import validate_research_assessment


assessment = ResearchAssessment(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure=(
        "We depend on external manufacturing capacity."
    ),
    new_disclosure=(
        "We depend on external manufacturing "
        "and advanced packaging capacity."
    ),
    significance="Medium",
    research_priority="Medium",
    evidence=[
        "and advanced packaging capacity"
    ],
    rationale=(
        "The revised wording explicitly identifies advanced "
        "packaging capacity. This does not prove that actual "
        "supplier dependence increased."
    ),
    research_questions=[
        "What prompted this disclosure clarification?"
    ],
    model_name="offline-test",
    requires_human_review=True
)

assert validate_research_assessment(assessment)

print("PASS: Grounded evidence accepted.")
