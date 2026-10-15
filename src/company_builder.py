
from src.company_models import CompanyProfile

from src.company_adapter import (
    build_company_identity,
    build_financial_overview,
    build_filing_sources,
)

from src.signal_integration import (
    integrate_company_signals,
)


def build_research_summary(
    ticker,
    financial,
    research_signals,
    assessed_count,
    total_changes,
):
    """
    Create a deterministic research summary.

    No AI calls, causal claims, or investment advice.
    """

    parts = []

    if financial is not None:
        parts.append(
            f"{ticker} latest available fiscal year ends "
            f"{financial.fiscal_year_end}."
        )

        if financial.revenue_growth_pct is not None:
            parts.append(
                "Reported revenue growth: "
                f"{financial.revenue_growth_pct:.2f}%."
            )

        if financial.net_margin_pct is not None:
            parts.append(
                "Reported net margin: "
                f"{financial.net_margin_pct:.2f}%."
            )

    else:
        parts.append(
            "Financial overview is unavailable."
        )

    if (
        research_signals is not None
        and research_signals.financial is not None
    ):
        parts.append(
            "Historical financial research signal: "
            f"{research_signals.financial.research_signal}."
        )

    parts.append(
        f"{assessed_count} of {total_changes} revised "
        "disclosure changes have been assessed."
    )

    if assessed_count > 0:
        parts.append(
            "Highest research priority among assessed "
            "disclosures: "
            f"{research_signals.overall_research_status}."
        )
    else:
        parts.append(
            "Disclosure research priority has not "
            "been assessed."
        )

    parts.append(
        "Financial and disclosure signals are presented "
        "together for further investigation; no causal "
        "relationship is established."
    )

    return " ".join(parts)


def build_company_profile(
    ticker,
    submissions,
    financial_df,
    financial_changes,
    filings_df,
    assessments,
    total_changes,
):
    """
    Build a complete CompanyProfile from existing
    SEC data and validated research assessments.

    All inputs are supplied by the caller.
    No network requests or AI API calls occur here.
    """

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker cannot be empty.")

    if not isinstance(total_changes, int):
        raise TypeError(
            "total_changes must be an integer."
        )

    if total_changes < 0:
        raise ValueError(
            "total_changes cannot be negative."
        )

    # ----------------------------------------
    # 1. SEC Company Identity
    # ----------------------------------------

    identity = build_company_identity(
        ticker=ticker,
        submissions=submissions,
    )

    # ----------------------------------------
    # 2. Latest Financial Overview
    # ----------------------------------------

    financial = build_financial_overview(
        financial_df
    )

    # ----------------------------------------
    # 3. SEC Filing Sources
    # ----------------------------------------

    filing_sources = build_filing_sources(
        filings_df
    )

    # ----------------------------------------
    # 4. Integrated Research Signals
    # ----------------------------------------

    research_signals = integrate_company_signals(
        ticker=ticker,
        financial_changes=financial_changes,
        assessments=assessments,
    )

    assessed_count = (
        research_signals.disclosure_count
    )

    # Prevent incomplete or inconsistent counts.
    if assessed_count > total_changes:
        raise ValueError(
            "Assessed disclosures cannot exceed "
            "total revised disclosure changes."
        )

    # ----------------------------------------
    # 5. Cross-check ticker consistency
    # ----------------------------------------

    if identity.ticker != ticker:
        raise ValueError(
            "Company identity ticker mismatch."
        )

    if (
        research_signals.financial is not None
        and research_signals.financial.ticker != ticker
    ):
        raise ValueError(
            "Financial signal ticker mismatch."
        )

    for disclosure in research_signals.disclosures:
        if disclosure.ticker != ticker:
            raise ValueError(
                "Disclosure signal ticker mismatch."
            )

    # ----------------------------------------
    # 6. Deterministic Research Summary
    # ----------------------------------------

    summary = build_research_summary(
        ticker=ticker,
        financial=financial,
        research_signals=research_signals,
        assessed_count=assessed_count,
        total_changes=total_changes,
    )

    return CompanyProfile(
        identity=identity,
        financial=financial,
        research_signals=research_signals,
        filing_sources=filing_sources,
        research_summary=summary,
        requires_human_review=True,
    )
