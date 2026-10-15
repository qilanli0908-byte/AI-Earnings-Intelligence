
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from src.research_models import ResearchAssessment
from src.research_storage import (
    make_assessment_id,
    save_assessment,
    load_assessment,
)


assessment = ResearchAssessment(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure="Risks related to acquisitions.",
    new_disclosure="Risks relating to acquisitions.",
    significance="Low",
    research_priority="Low",
    evidence=[
        "Risks related to acquisitions.",
        "Risks relating to acquisitions.",
    ],
    rationale=(
        "This is a minor editorial wording change. "
        "The text does not establish a change in business risk."
    ),
    research_questions=[
        "Is any substantive acquisition risk discussed elsewhere?"
    ],
    model_name="offline-test",
)

assessment_id = make_assessment_id(
    assessment.ticker,
    assessment.section,
    assessment.change_type,
    assessment.old_disclosure,
    assessment.new_disclosure,
)

assert len(assessment_id) == 64

with TemporaryDirectory() as temporary_directory:

    with patch(
        "src.research_storage.STORAGE_DIR",
        Path(temporary_directory),
    ):

        filepath = save_assessment(assessment)

        assert filepath.exists()

        loaded = load_assessment(
            assessment.ticker,
            assessment.section,
            assessment.change_type,
            assessment.old_disclosure,
            assessment.new_disclosure,
        )

        assert loaded is not None
        assert loaded.ticker == "NVDA"
        assert loaded.significance == "Low"
        assert loaded.research_priority == "Low"
        assert loaded.evidence == assessment.evidence

        missing = load_assessment(
            "AMD",
            assessment.section,
            assessment.change_type,
            assessment.old_disclosure,
            assessment.new_disclosure,
        )

        assert missing is None

print("PASS: Research Assessment saved successfully.")
print("PASS: Saved assessment loaded and validated.")
print("PASS: Missing assessment correctly returns None.")
print("PASS: Test used temporary storage.")
