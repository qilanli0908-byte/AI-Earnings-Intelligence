
from src.research_models import ResearchAssessment
from src.evidence_repair import repair_evidence


def make_assessment(evidence):
    return ResearchAssessment(
        ticker="NVDA",
        section="Item 1A - Risk Factors",
        change_type="Revised",
        old_disclosure=(
            "Additional risks related to acquisitions include, "
            "but are not limited to:"
        ),
        new_disclosure=(
            "Additional risks relating to acquisitions include, "
            "but are not limited to:"
        ),
        significance="Low",
        research_priority="Low",
        evidence=evidence,
        rationale="Minor editorial wording change.",
        research_questions=[
            "Is there any substantive change elsewhere?"
        ],
        model_name="offline-test",
    )


# Test 1: Remove an AI-added label and outer quotes.
assessment = make_assessment([
    'Old disclosure: "Additional risks related to acquisitions include, but are not limited to:"'
])

repaired = repair_evidence(assessment)

assert repaired.evidence == [
    "Additional risks related to acquisitions include, but are not limited to:"
]

print("PASS: AI-added evidence label repaired.")


# Test 2: Already valid evidence stays unchanged.
assessment = make_assessment([
    "Additional risks relating to acquisitions include, but are not limited to:"
])

repaired = repair_evidence(assessment)

assert repaired.evidence == assessment.evidence

print("PASS: Valid evidence preserved.")


# Test 3: Fabricated evidence must still be rejected.
assessment = make_assessment([
    "NVIDIA has permanently eliminated all acquisition risks."
])

try:
    repair_evidence(assessment)

except ValueError:
    print("PASS: Fabricated evidence rejected.")

else:
    raise AssertionError(
        "Fabricated evidence should never pass validation."
    )


# Test 4: Original assessment must not be modified.
assessment = make_assessment([
    'Old disclosure: "Additional risks related to acquisitions include, but are not limited to:"'
])

original_evidence = list(assessment.evidence)

repair_evidence(assessment)

assert assessment.evidence == original_evidence

print("PASS: Original assessment remains unchanged.")
