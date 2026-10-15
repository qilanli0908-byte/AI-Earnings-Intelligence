
from src.research_models import ResearchAssessment


PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
}


def rank_assessments(assessments):
    """
    Rank validated research assessments.

    Primary sort:
        Research Priority: High -> Medium -> Low

    Secondary sort:
        Change Significance: High -> Medium -> Low

    Original input order is preserved when both values are equal.
    """

    from src.research_validation import validate_research_assessment

    for assessment in assessments:
        validate_research_assessment(assessment)

    return sorted(
        assessments,
        key=lambda assessment: (
            PRIORITY_ORDER[assessment.research_priority],
            PRIORITY_ORDER[assessment.significance],
        ),
    )


def build_ranking_rows(
    assessments,
    total_disclosures=None,
):
    """
    Convert ranked assessments into dashboard-ready rows.

    Unassessed disclosures are not assigned an artificial priority.
    """

    ranked = rank_assessments(assessments)

    rows = []

    for index, assessment in enumerate(ranked, start=1):

        rows.append(
            {
                "Rank": index,
                "Ticker": assessment.ticker,
                "Section": assessment.section,
                "Change Type": assessment.change_type,
                "Significance": assessment.significance,
                "Research Priority": assessment.research_priority,
                "Evidence Count": len(assessment.evidence),
                "Rationale": assessment.rationale,
                "Assessment Status": "Assessed",
            }
        )

    if total_disclosures is not None:

        if total_disclosures < len(assessments):
            raise ValueError(
                "Total disclosures cannot be smaller "
                "than the number of assessments."
            )

        unassessed_count = total_disclosures - len(assessments)

        for _ in range(unassessed_count):

            rows.append(
                {
                    "Rank": None,
                    "Ticker": None,
                    "Section": None,
                    "Change Type": None,
                    "Significance": "Not Assessed",
                    "Research Priority": "Not Assessed",
                    "Evidence Count": 0,
                    "Rationale": "",
                    "Assessment Status": "Not Assessed",
                }
            )

    return rows
