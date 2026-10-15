
import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from src.evidence_repair import repair_evidence

from src.research_models import ResearchAssessment
from src.research_prompts import (
    RESEARCH_SYSTEM_PROMPT,
    build_research_prompt,
)
from src.research_validation import validate_research_assessment


def assess_research_priority(
    ticker,
    section,
    change_type,
    old_disclosure,
    new_disclosure,
    model="gpt-4.1-mini",
):
    """
    Generate a research assessment for one SEC disclosure change.

    Makes one real API request when called.
    Validates the result before returning it.
    """

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "A real OPENAI_API_KEY is required for research assessment."
        )

    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )

    user_prompt = build_research_prompt(
        ticker=ticker,
        section=section,
        change_type=change_type,
        old_disclosure=old_disclosure,
        new_disclosure=new_disclosure,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": RESEARCH_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_completion_tokens=700,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty research assessment.")

    result = json.loads(content)

    required_keys = (
        "significance",
        "research_priority",
        "evidence",
        "rationale",
        "research_questions",
    )

    for key in required_keys:
        if key not in result:
            raise ValueError(
                f"Missing research assessment field: {key}"
            )

    assessment = ResearchAssessment(
        ticker=ticker,
        section=section,
        change_type=change_type,
        old_disclosure=old_disclosure,
        new_disclosure=new_disclosure,
        significance=result["significance"],
        research_priority=result["research_priority"],
        evidence=result["evidence"],
        rationale=result["rationale"],
        research_questions=result["research_questions"],
        model_name=model,
        requires_human_review=True,
    )

    assessment = repair_evidence(assessment)

    return assessment
