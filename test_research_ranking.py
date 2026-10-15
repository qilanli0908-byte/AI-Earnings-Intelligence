
from src.research_models import ResearchAssessment
from src.research_ranking import (
    rank_assessments,
    build_ranking_rows,
)


def make_sample(label, significance, priority):
    old_text = f"Old disclosure about {label}."
    new_text = f"Updated disclosure about {label}."

    return ResearchAssessment(
        ticker="NVDA",
        section="Item 1A - Risk Factors",
        change_type="Revised",
        old_disclosure=old_text,
        new_disclosure=new_text,
        significance=significance,
        research_priority=priority,
        evidence=[new_text],
        rationale=f"Research assessment for {label}.",
        research_questions=[
            f"What should be investigated about {label}?"
        ],
        model_name="offline-test",
    )


samples = [
    make_sample("Acquisitions", "Low", "Low"),
    make_sample("Supply Chain", "High", "High"),
    make_sample("Competition", "Medium", "Medium"),
    make_sample("Export Restrictions", "High", "Medium"),
    make_sample("Advanced Packaging", "Medium", "High"),
]


ranked = rank_assessments(samples)

assert [
    item.research_priority for item in ranked
] == [
    "High",
    "High",
    "Medium",
    "Medium",
    "Low",
]

assert [
    item.new_disclosure for item in ranked
] == [
    "Updated disclosure about Supply Chain.",
    "Updated disclosure about Advanced Packaging.",
    "Updated disclosure about Export Restrictions.",
    "Updated disclosure about Competition.",
    "Updated disclosure about Acquisitions.",
]

print("PASS: Assessments ranked by priority and significance.")


rows = build_ranking_rows(
    samples,
    total_disclosures=7,
)

assert len(rows) == 7

assert rows[0]["Rank"] == 1
assert rows[0]["Research Priority"] == "High"

assert rows[-1]["Assessment Status"] == "Not Assessed"
assert rows[-1]["Research Priority"] == "Not Assessed"
assert rows[-1]["Rank"] is None

assert sum(
    row["Assessment Status"] == "Not Assessed"
    for row in rows
) == 2

print("PASS: Unassessed disclosures remain Not Assessed.")


try:
    build_ranking_rows(
        samples,
        total_disclosures=3,
    )

except ValueError:
    print("PASS: Invalid disclosure count correctly rejected.")

else:
    raise AssertionError(
        "Expected invalid disclosure count to be rejected."
    )
