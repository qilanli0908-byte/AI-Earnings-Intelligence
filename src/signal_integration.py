
import math

import pandas as pd

from src.signal_models import (
    FinancialSignal,
    DisclosureSignal,
    CompanyResearchSignals,
)

from src.research_models import ResearchAssessment
from src.research_validation import validate_research_assessment


PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
}


def safe_float(value):
    """
    Convert a numeric value to float.

    Missing or non-finite values become None.
    """

    if value is None or pd.isna(value):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(result):
        return None

    return result


def build_financial_signal(ticker, financial_changes):
    """
    Convert the latest SEC financial-change row
    into a structured FinancialSignal.

    Input:
        DataFrame from calculate_financial_changes().
    """

    if financial_changes is None or financial_changes.empty:
        return None

    required_columns = [
        "end",
        "Revenue Growth (%)",
        "Growth Change (pp)",
        "Growth Trend",
        "Net Margin (%)",
        "Margin Change (pp)",
        "Margin Trend",
        "Research Signal",
    ]

    missing = [
        column
        for column in required_columns
        if column not in financial_changes.columns
    ]

    if missing:
        raise ValueError(
            f"Missing financial columns: {missing}"
        )

    # Select the latest period by its actual date.
    latest = (
        financial_changes
        .sort_values("end")
        .iloc[-1]
    )

    return FinancialSignal(
        ticker=ticker.upper(),
        fiscal_year_end=str(latest["end"]),
        revenue_growth=safe_float(
            latest["Revenue Growth (%)"]
        ),
        growth_change_pp=safe_float(
            latest["Growth Change (pp)"]
        ),
        growth_trend=str(
            latest["Growth Trend"]
        ),
        net_margin=safe_float(
            latest["Net Margin (%)"]
        ),
        margin_change_pp=safe_float(
            latest["Margin Change (pp)"]
        ),
        margin_trend=str(
            latest["Margin Trend"]
        ),
        research_signal=str(
            latest["Research Signal"]
        ),
    )


def build_disclosure_signals(ticker, assessments):
    """
    Convert validated ResearchAssessment objects
    into DisclosureSignal objects.

    Only assessments for the selected ticker
    are included.
    """

    signals = []

    for assessment in assessments:

        if not isinstance(
            assessment,
            ResearchAssessment
        ):
            raise TypeError(
                "Expected ResearchAssessment objects."
            )

        validate_research_assessment(assessment)

        if assessment.ticker.upper() != ticker.upper():
            continue

        signals.append(
            DisclosureSignal(
                ticker=assessment.ticker.upper(),
                section=assessment.section,
                change_type=assessment.change_type,
                significance=assessment.significance,
                research_priority=assessment.research_priority,
                evidence=list(assessment.evidence),
                rationale=assessment.rationale,
                requires_human_review=(
                    assessment.requires_human_review
                ),
            )
        )

    return sorted(
        signals,
        key=lambda signal: (
            PRIORITY_ORDER[signal.research_priority],
            PRIORITY_ORDER[signal.significance],
        ),
    )


def integrate_company_signals(
    ticker,
    financial_changes,
    assessments,
):
    """
    Integrate historical financial signals and
    validated disclosure assessments.

    This function does not infer causation or
    generate investment recommendations.
    """

    ticker = ticker.upper()

    financial_signal = build_financial_signal(
        ticker,
        financial_changes,
    )

    disclosure_signals = build_disclosure_signals(
        ticker,
        assessments,
    )

    high_count = sum(
        signal.research_priority == "High"
        for signal in disclosure_signals
    )

    medium_count = sum(
        signal.research_priority == "Medium"
        for signal in disclosure_signals
    )

    low_count = sum(
        signal.research_priority == "Low"
        for signal in disclosure_signals
    )

    if high_count > 0:
        overall_status = "High Research Priority"

    elif medium_count > 0:
        overall_status = "Medium Research Priority"

    elif low_count > 0:
        overall_status = "Low Research Priority"

    else:
        overall_status = "Not Assessed"

    return CompanyResearchSignals(
        ticker=ticker,
        financial=financial_signal,
        disclosures=disclosure_signals,
        disclosure_count=len(disclosure_signals),
        high_priority_count=high_count,
        medium_priority_count=medium_count,
        low_priority_count=low_count,
        overall_research_status=overall_status,
    )
