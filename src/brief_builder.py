
from src.brief_models import (
    BriefEvidence,
    BriefSection,
    ResearchBrief,
)
from src.company_models import CompanyProfile
from src.thesis_models import InvestmentThesis
from src.thesis_monitor import ThesisMonitoringResult


def build_research_brief(
    profile: CompanyProfile,
    theses: list[InvestmentThesis],
    monitoring_results: list[ThesisMonitoringResult],
) -> ResearchBrief:
    """
    Build a deterministic research brief from existing data.

    No SEC requests or AI API calls are made here.
    """
    ticker = profile.identity.ticker.strip().upper()

    if not ticker:
        raise ValueError("Company ticker is required")

    for thesis in theses:
        if thesis.ticker.strip().upper() != ticker:
            raise ValueError("Cross-company thesis detected")

    for result in monitoring_results:
        if result.ticker.strip().upper() != ticker:
            raise ValueError("Cross-company monitoring result detected")

    thesis_ids = {thesis.thesis_id for thesis in theses}

    if len(thesis_ids) != len(theses):
        raise ValueError("Duplicate thesis IDs detected")

    result_ids = [result.thesis_id for result in monitoring_results]

    if len(set(result_ids)) != len(result_ids):
        raise ValueError("Duplicate monitoring results detected")

    if set(result_ids) != thesis_ids:
        raise ValueError("Thesis and monitoring results do not match")

    sections = []

    # 1. Company Overview
    sections.append(
        BriefSection(
            title="Company Overview",
            summary=(
                f"{profile.identity.company_name} ({ticker}). "
                f"Industry: {profile.identity.industry}. "
                f"Exchange: {profile.identity.exchange}. "
                f"SEC CIK: {profile.identity.cik}."
            ),
        )
    )

    # 2. Financial Momentum
    # Company Facts is the source dataset, not independent verification of
    # each displayed metric or the derivation of growth/margin.
    cik_digits = str(profile.identity.cik).strip()
    if not cik_digits.isdecimal() or int(cik_digits) <= 0:
        raise ValueError("A valid numeric SEC CIK is required for financial attribution")
    financial = profile.financial

    financial_summary = (
        f"Fiscal year ended {financial.fiscal_year_end}. "
        f"Revenue: ${financial.revenue_billions:.2f}B. "
        f"Net income: ${financial.net_income_billions:.2f}B. "
        f"Revenue growth: {financial.revenue_growth_pct:.2f}%. "
        f"Net margin: {financial.net_margin_pct:.2f}%."
    )

    sections.append(
        BriefSection(
            title="Financial Momentum",
            summary=financial_summary,
            evidence=[
                BriefEvidence(
                    description=(
                        "Historical financial metrics from "
                        "the existing SEC financial pipeline."
                    ),
                    evidence_type="SEC Financial",
                    verification_status="Requires Review",
                    source_url=(
                        "https://data.sec.gov/api/xbrl/companyfacts/"
                        f"CIK{int(cik_digits):010d}.json"
                    ),
                    citation=(
                        f"SEC EDGAR Company Facts, CIK {int(cik_digits):010d}; "
                        f"fiscal year ended {financial.fiscal_year_end}. "
                        "Metric/tag and period mapping require human review."
                    ),
                )
            ],
        )
    )

    # 3. SEC Filing Sources
    filing_evidence = []

    for filing in profile.filing_sources:
        filing_evidence.append(
            BriefEvidence(
                description=(
                    f"{filing.form} filed {filing.filing_date}; "
                    f"accession {filing.accession_number}."
                ),
                evidence_type="SEC Filing",
                verification_status="Requires Review",
                source_url=filing.sec_url,
                citation=filing.accession_number,
            )
        )

    sections.append(
        BriefSection(
            title="SEC Filing Sources",
            summary=(
                f"{len(filing_evidence)} filing source(s) "
                "available for review."
            ),
            evidence=filing_evidence,
        )
    )

    # 4. Research Signals
    signals = profile.research_signals
    financial_signal = signals.financial

    signal_summary = (
        f"Financial Signal: {financial_signal.research_signal}\n"
        f"Growth Trend: {financial_signal.growth_trend}\n"
        f"Margin Trend: {financial_signal.margin_trend}\n"
        f"Saved Disclosure Assessments: {len(signals.disclosures)}"
    )

    sections.append(
        BriefSection(
            title="Research Signals",
            summary=signal_summary,
        )
    )


    # 5. Investment Theses
    thesis_evidence = []

    for thesis in theses:
        for evidence in thesis.evidence:
            # Preserve only the status supported by source metadata.
            # Do not promote a claim to Verified automatically.
            thesis_evidence.append(
                BriefEvidence(
                    description=evidence.description,
                    evidence_type="Investment Thesis",
                    verification_status=(
                        "Requires Review"
                        if evidence.status == "Verified"
                        else "Unverified"
                    ),
                    source_url=evidence.source_url,
                    citation=evidence.citation,
                )
            )


    # Build a structured thesis summary.
    # Only use information already saved in the thesis objects.
    thesis_lines = []

    if not theses:
        thesis_summary = "No saved investment theses."

    else:
        for thesis in theses:
            thesis_lines.extend([
                f"{thesis.thesis_type.upper()} THESIS",
                f"Thesis ID: {thesis.thesis_id}",
                f"Core Statement: {thesis.statement}",
                f"Supporting Evidence: {len(thesis.evidence)} saved item(s)",
                f"Key Hypotheses: {len(thesis.hypotheses)} saved item(s)",
            ])

            if thesis.evidence:
                thesis_lines.append("Evidence Details:")

                for index, evidence in enumerate(
                    thesis.evidence,
                    start=1,
                ):
                    thesis_lines.append(
                        f"{index}. {evidence.description} "
                        f"[Original status: {evidence.status}; "
                        f"brief requires independent review]"
                    )
            else:
                thesis_lines.append(
                    "Evidence Details: No saved supporting evidence."
                )

            if thesis.hypotheses:
                thesis_lines.append("Hypothesis Details:")

                for index, hypothesis in enumerate(
                    thesis.hypotheses,
                    start=1,
                ):
                    thesis_lines.append(
                        f"{index}. {hypothesis.description} "
                        f"[{hypothesis.status}]"
                    )
            else:
                thesis_lines.append(
                    "Hypothesis Details: No saved hypotheses."
                )

            thesis_lines.append(
                "Research Limitation: This thesis is not "
                "automatically validated by the financial signal."
            )

            thesis_lines.append("")

        thesis_summary = "\n".join(thesis_lines).strip()


    sections.append(
        BriefSection(
            title="Investment Theses",
            summary=thesis_summary,
            evidence=thesis_evidence,
        )
    )

    # 6. Thesis Monitoring
    monitoring_summary = (
        "\n".join(
            f"{result.thesis_id}: {result.impact}. "
            f"Signal: {result.financial_signal}. "
            f"{result.explanation}"
            for result in monitoring_results
        )
        if monitoring_results
        else "No thesis monitoring results available."
    )

    sections.append(
        BriefSection(
            title="Thesis Monitoring",
            summary=monitoring_summary,
        )
    )

    return ResearchBrief(
        ticker=ticker,
        company_name=profile.identity.company_name,
        fiscal_year_end=financial.fiscal_year_end,
        sections=sections,
        requires_human_review=True,
    )
