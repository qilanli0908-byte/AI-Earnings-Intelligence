
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
    significance="High",
    research_priority="High",
    evidence=[
        "The company experienced severe packaging shortages."
    ],
    rationale=(
        "The disclosure allegedly confirms severe shortages."
    ),
    research_questions=[
        "How severe are these shortages?"
    ],
    model_name="offline-test"
)

try:
    validate_research_assessment(assessment)

except ValueError as error:

    assert "Evidence quotation was not found" in str(error)

    print("PASS: Fabricated evidence correctly rejected.")

else:

    raise AssertionError(
        "Validator incorrectly accepted fabricated evidence."
    )
