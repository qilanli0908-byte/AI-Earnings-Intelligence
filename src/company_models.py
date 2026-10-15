
from dataclasses import dataclass, field
from typing import List, Optional

from src.signal_models import CompanyResearchSignals


@dataclass
class CompanyIdentity:
    ticker: str
    company_name: str
    cik: Optional[str] = None
    exchange: Optional[str] = None
    industry: Optional[str] = None

    source: str = "SEC EDGAR"


@dataclass
class FilingSource:
    form: str
    filing_date: str
    accession_number: str
    sec_url: str

    fiscal_year_end: Optional[str] = None


@dataclass
class CompanyFinancialOverview:
    fiscal_year_end: str

    revenue_billions: Optional[float] = None
    net_income_billions: Optional[float] = None

    revenue_growth_pct: Optional[float] = None
    net_margin_pct: Optional[float] = None

    source: str = "SEC Company Facts"


@dataclass
class CompanyProfile:
    identity: CompanyIdentity

    financial: Optional[CompanyFinancialOverview] = None

    research_signals: Optional[
        CompanyResearchSignals
    ] = None

    filing_sources: List[FilingSource] = field(
        default_factory=list
    )

    research_summary: str = ""

    requires_human_review: bool = True
