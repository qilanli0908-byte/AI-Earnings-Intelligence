from src.public_demo import require_private_feature

import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from src.ai_models import DisclosureAnalysis
from src.ai_validation import validate_analysis

from src.ai_prompts import (
    DISCLOSURE_SYSTEM_PROMPT,
    build_disclosure_prompt
)


def analyze_disclosure(
    ticker,
    section,
    change_type,
    old_disclosure,
    new_disclosure,
    old_filing_url=None,
    new_filing_url=None,
    model="gpt-4.1-mini"
):
    """
    Analyze one SEC disclosure change using an AI model.

    This function makes a real API request when called.
    """

    require_private_feature("Paid AI: analyze_disclosure")
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "A real OPENAI_API_KEY is required to run AI analysis."
        )

    client = OpenAI(api_key=api_key)

    user_prompt = build_disclosure_prompt(
        ticker=ticker,
        section=section,
        change_type=change_type,
        old_disclosure=old_disclosure,
        new_disclosure=new_disclosure
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": DISCLOSURE_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format={
            "type": "json_object"
        },
        temperature=0.2,
        max_completion_tokens=500
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response.")

    result = json.loads(content)

    required_keys = [
        "change_summary",
        "potential_business_implications",
        "research_questions"
    ]

    for key in required_keys:
        if key not in result:
            raise ValueError(
                f"Missing AI response field: {key}"
            )

    if not isinstance(result["research_questions"], list):
        raise ValueError(
            "research_questions must be a list."
        )

    analysis = DisclosureAnalysis(
        ticker=ticker,
        section=section,
        change_type=change_type,
        old_disclosure=old_disclosure,
        new_disclosure=new_disclosure,
        change_summary=result["change_summary"],
        potential_business_implications=(
            result["potential_business_implications"]
        ),
        research_questions=result["research_questions"],
        old_filing_url=old_filing_url,
        new_filing_url=new_filing_url,
        model_name=model,
        requires_human_review=True
    )
    
    validate_analysis(analysis)

    return analysis