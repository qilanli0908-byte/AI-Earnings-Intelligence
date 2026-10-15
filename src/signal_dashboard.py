
from src.research_storage import load_assessment
from src.signal_integration import integrate_company_signals


SECTION = "Item 1A - Risk Factors"
CHANGE_TYPE = "Revised"


def load_current_disclosure_assessments(
    ticker,
    wording_changes,
):
    """
    Load only validated, saved assessments
    belonging to the current disclosure comparison.

    This function does not call the OpenAI API.
    """

    assessments = []

    for item in wording_changes:

        assessment = load_assessment(
            ticker=ticker,
            section=SECTION,
            change_type=CHANGE_TYPE,
            old_disclosure=item["old"],
            new_disclosure=item["new"],
        )

        if assessment is not None:
            assessments.append(assessment)

    return assessments


def build_company_dashboard_data(
    ticker,
    financial_changes,
    wording_changes,
):
    """
    Build the combined company research view
    using existing financial data and local
    validated disclosure assessments.
    """

    assessments = load_current_disclosure_assessments(
        ticker=ticker,
        wording_changes=wording_changes,
    )

    company = integrate_company_signals(
        ticker=ticker,
        financial_changes=financial_changes,
        assessments=assessments,
    )

    total_changes = len(wording_changes)
    assessed_count = len(assessments)

    if assessed_count > total_changes:
        raise ValueError(
            "Assessed count cannot exceed total changes."
        )

    return {
        "company": company,
        "total_changes": total_changes,
        "assessed_count": assessed_count,
        "not_assessed_count": total_changes - assessed_count,
    }
