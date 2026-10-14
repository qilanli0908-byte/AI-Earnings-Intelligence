
import json
import os
from unittest.mock import MagicMock, patch

from src.research_engine import assess_research_priority


old_text = "We depend on external manufacturing capacity."

new_text = (
    "We depend on external manufacturing "
    "and advanced packaging capacity."
)

# Deliberately fabricated evidence.
fake_result = {
    "significance": "High",
    "research_priority": "High",
    "evidence": [
        "The company experienced severe packaging shortages."
    ],
    "rationale": (
        "The disclosure allegedly confirms severe shortages."
    ),
    "research_questions": [
        "How severe are these shortages?"
    ],
}

mock_response = MagicMock()
mock_response.choices[0].message.content = json.dumps(fake_result)

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
        try:
            assess_research_priority(
                ticker="NVDA",
                section="Item 1A - Risk Factors",
                change_type="Revised",
                old_disclosure=old_text,
                new_disclosure=new_text,
            )

        except ValueError as error:
            assert "Evidence quotation was not found" in str(error)

            print("PASS: Fabricated evidence rejected by Research Engine.")

        else:
            raise AssertionError(
                "Research Engine accepted fabricated evidence."
            )

mock_client.chat.completions.create.assert_called_once()

print("PASS: Test used a mock; no real API request was made.")
