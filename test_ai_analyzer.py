
from src.ai_analyzer import analyze_disclosure


try:
    analyze_disclosure(
        ticker="NVDA",
        section="Item 1A - Risk Factors",
        change_type="Revised",
        old_disclosure="Supply and component availability.",
        new_disclosure="Supply and capacity availability."
    )

except ValueError as error:

    assert "OPENAI_API_KEY" in str(error)

    print("PASS: AI Analyzer correctly rejects placeholder API keys.")

else:

    raise AssertionError(
        "Expected the placeholder API key to be rejected."
    )
