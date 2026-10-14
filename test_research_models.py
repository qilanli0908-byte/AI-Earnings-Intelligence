
from src.research_models import ResearchAssessment


assessment = ResearchAssessment(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure="We depend on external manufacturing capacity.",
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
        "The revised disclosure explicitly mentions an additional "
        "capacity dependency. This does not establish that actual "
        "business risk has increased."
    ),
    research_questions=[
        "What prompted the additional disclosure?"
    ],
    model_name="offline-test"
)

assert assessment.ticker == "NVDA"
assert assessment.significance == "Medium"
assert assessment.research_priority == "Medium"
assert len(assessment.evidence) == 1
assert assessment.requires_human_review is True

print("PASS: ResearchAssessment model works.")
