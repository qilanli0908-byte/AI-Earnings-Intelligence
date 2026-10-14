
import json
import os
from unittest.mock import MagicMock, patch

from src.research_engine import assess_research_priority


old_text = "We depend on external manufacturing capacity."

new_text = (
    "We depend on external manufacturing "
    "and advanced packaging capacity."
)

mock_result = {
    "significance": "Medium",
    "research_priority": "Medium",
    "evidence": [
        "and advanced packaging capacity"
    ],
    "rationale": (
        "The new wording explicitly mentions advanced packaging. "
        "It does not establish that actual supplier dependence increased."
    ),
    "research_questions": [
        "What prompted the additional disclosure?"
    ],
}

mock_response = MagicMock()
mock_response.choices[0].message.content = json.dumps(mock_result)

mock_client = MagicMock()
mock_client.chat.completions.create.return_value = mock_response

with patch.dict(
    os.environ,
    {"OPENAI_API_KEY": "offline-test-key"},
):
    with patch(
        "src.research_engine.OpenAI",
        return_value=mock_client,
    ):
        assessment = assess_research_priority(
            ticker="NVDA",
            section="Item 1A - Risk Factors",
            change_type="Revised",
            old_disclosure=old_text,
            new_disclosure=new_text,
        )

assert assessment.significance == "Medium"
assert assessment.research_priority == "Medium"
assert assessment.evidence == [
    "and advanced packaging capacity"
]
assert assessment.requires_human_review is True

mock_client.chat.completions.create.assert_called_once()

print("PASS: Research Engine works with a mocked AI response.")
print("PASS: No real API request was made.")
