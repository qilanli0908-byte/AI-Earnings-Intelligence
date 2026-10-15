
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


ThesisType = Literal["Bull", "Bear"]
EvidenceStatus = Literal["Verified", "Unverified"]


@dataclass
class ThesisEvidence:
    description: str
    source_url: str
    status: EvidenceStatus
    source_type: str = "SEC"
    citation: str = ""


@dataclass
class ThesisHypothesis:
    description: str
    status: Literal["Unverified", "Supported", "Contradicted"] = "Unverified"


@dataclass
class InvestmentThesis:
    thesis_id: str
    ticker: str
    thesis_type: ThesisType
    statement: str
    evidence: list[ThesisEvidence] = field(default_factory=list)
    hypotheses: list[ThesisHypothesis] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    requires_human_review: bool = True
