
from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialFact:
    """
    A standardized financial fact extracted from SEC EDGAR.

    Each record contains both its financial value and
    the information needed to trace its original source.
    """

    ticker: str
    cik: str
    metric: str

    value: float
    unit: str

    period_start: str
    period_end: str

    filing_date: str
    accession_number: str
    form: str

    source_tag: str

    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None
