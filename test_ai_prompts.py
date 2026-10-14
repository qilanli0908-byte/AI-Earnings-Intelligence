
from src.ai_prompts import (
    DISCLOSURE_SYSTEM_PROMPT,
    build_disclosure_prompt
)


prompt = build_disclosure_prompt(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure=(
        "Long manufacturing lead times and uncertain "
        "supply and component availability."
    ),
    new_disclosure=(
        "Long manufacturing lead times and uncertain "
        "supply and capacity availability."
    )
)


assert "NVDA" in prompt

assert "component availability" in prompt

assert "capacity availability" in prompt

assert "research_questions" in DISCLOSURE_SYSTEM_PROMPT

assert "Do not invent facts" in DISCLOSURE_SYSTEM_PROMPT


print("PASS: AI disclosure prompt works correctly.")

print("\n========== GENERATED PROMPT ==========")

print(prompt)
