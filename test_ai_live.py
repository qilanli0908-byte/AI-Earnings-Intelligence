
from src.ai_analyzer import analyze_disclosure


result = analyze_disclosure(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure=(
        "Our business depends on third-party suppliers "
        "for manufacturing capacity."
    ),
    new_disclosure=(
        "Our business depends on third-party suppliers "
        "for manufacturing capacity and advanced packaging capacity."
    )
)

print("\n=== AI ANALYSIS ===")
print("Ticker:", result.ticker)
print("Section:", result.section)
print("Change Summary:", result.change_summary)
print(
    "Potential Business Implications:",
    result.potential_business_implications
)
print("Research Questions:", result.research_questions)
print("Human Review Required:", result.requires_human_review)
print("Model:", result.model_name)
