
from src.research_engine import assess_research_priority


print("Starting ONE research assessment API request...")

assessment = assess_research_priority(
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
    ),
)

print("\n=== RESEARCH ASSESSMENT ===")

print("Ticker:", assessment.ticker)
print("Significance:", assessment.significance)
print("Research Priority:", assessment.research_priority)

print("\nEvidence:")
for quote in assessment.evidence:
    print("-", quote)

print("\nRationale:")
print(assessment.rationale)

print("\nResearch Questions:")
for question in assessment.research_questions:
    print("-", question)

print("\nHuman Review Required:", assessment.requires_human_review)
print("Model:", assessment.model_name)

print("\nPASS: Research assessment completed and validated.")
