
from src.ai_models import DisclosureAnalysis


analysis = DisclosureAnalysis(
    ticker="NVDA",
    section="Item 1A - Risk Factors",
    change_type="Revised",
    old_disclosure="Supply and component availability.",
    new_disclosure="Supply and capacity availability.",
    change_summary="The company revised its supply-related wording.",
    potential_business_implications=(
        "Capacity constraints may warrant further investigation."
    ),
    research_questions=[
        "Has manufacturing capacity become a more important constraint?",
        "Does management discuss related supply limitations elsewhere?"
    ]
)


assert analysis.ticker == "NVDA"

assert analysis.change_type == "Revised"

assert len(analysis.research_questions) == 2

assert analysis.requires_human_review is True


print("PASS: AI Disclosure Analysis data model works correctly.")
