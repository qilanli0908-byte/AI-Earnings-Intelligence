
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DisclosureAnalysis:
    """
    Structured AI analysis of one SEC disclosure change.

    The analysis must remain grounded in the supplied
    filing text and must not be treated as investment advice.
    """

    ticker: str

    section: str

    change_type: str

    old_disclosure: Optional[str]

    new_disclosure: Optional[str]

    # AI-generated research analysis
    change_summary: str

    potential_business_implications: str

    research_questions: List[str] = field(
        default_factory=list
    )

    # Source provenance
    old_filing_url: Optional[str] = None

    new_filing_url: Optional[str] = None

    # Transparency
    model_name: Optional[str] = None

    requires_human_review: bool = True
