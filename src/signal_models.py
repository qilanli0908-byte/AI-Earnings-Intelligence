
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FinancialSignal:
    ticker: str
    fiscal_year_end: str

    revenue_growth: Optional[float]
    growth_change_pp: Optional[float]
    growth_trend: str

    net_margin: Optional[float]
    margin_change_pp: Optional[float]
    margin_trend: str

    research_signal: str
    source: str = "SEC Company Facts"


@dataclass
class DisclosureSignal:
    ticker: str
    section: str
    change_type: str

    significance: str
    research_priority: str

    evidence: List[str] = field(default_factory=list)
    rationale: str = ""

    source: str = "SEC 10-K Disclosure"
    requires_human_review: bool = True


@dataclass
class CompanyResearchSignals:
    ticker: str

    financial: Optional[FinancialSignal] = None

    disclosures: List[DisclosureSignal] = field(
        default_factory=list
    )

    disclosure_count: int = 0

    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0

    overall_research_status: str = "Not Assessed"
