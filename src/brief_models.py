
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


EvidenceType = Literal[
    "SEC Financial",
    "SEC Filing",
    "Research Assessment",
    "Investment Thesis",
]


VerificationStatus = Literal[
    "Verified",
    "Unverified",
    "Requires Review",
]


@dataclass
class BriefEvidence:
    description: str
    evidence_type: EvidenceType
    verification_status: VerificationStatus
    source_url: str = ""
    citation: str = ""


@dataclass
class BriefSection:
    title: str
    summary: str
    evidence: list[BriefEvidence] = field(default_factory=list)
    requires_human_review: bool = True


@dataclass
class ResearchBrief:
    ticker: str
    company_name: str
    fiscal_year_end: str
    sections: list[BriefSection] = field(default_factory=list)
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    requires_human_review: bool = True
