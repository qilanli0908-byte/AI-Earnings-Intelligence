
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from src.research_models import ResearchAssessment
from src.public_demo import enabled
from src.research_validation import validate_research_assessment


STORAGE_DIR = Path("data/research_assessments")


def make_assessment_id(
    ticker,
    section,
    change_type,
    old_disclosure,
    new_disclosure,
):
    """
    Generate a stable identifier for one disclosure comparison.
    """

    payload = {
        "ticker": ticker,
        "section": section,
        "change_type": change_type,
        "old_disclosure": old_disclosure,
        "new_disclosure": new_disclosure,
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def save_assessment(assessment: ResearchAssessment):
    """
    Save one validated research assessment as JSON.
    """

    validate_research_assessment(assessment)

    assessment_id = make_assessment_id(
        assessment.ticker,
        assessment.section,
        assessment.change_type,
        assessment.old_disclosure,
        assessment.new_disclosure,
    )

    if enabled():
        import streamlit as st
        st.session_state[f"public_assessment_{assessment_id}"] = assessment
        return None

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    filepath = STORAGE_DIR / f"{assessment_id}.json"

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(
            asdict(assessment),
            file,
            ensure_ascii=False,
            indent=2,
        )

    return filepath


def load_assessment(
    ticker,
    section,
    change_type,
    old_disclosure,
    new_disclosure,
):
    """
    Return a saved assessment, or None if none exists.
    """

    assessment_id = make_assessment_id(
        ticker,
        section,
        change_type,
        old_disclosure,
        new_disclosure,
    )

    if enabled():
        import streamlit as st
        return st.session_state.get(f"public_assessment_{assessment_id}")

    filepath = STORAGE_DIR / f"{assessment_id}.json"

    if not filepath.exists():
        return None

    with filepath.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assessment = ResearchAssessment(**data)

    validate_research_assessment(assessment)

    return assessment
