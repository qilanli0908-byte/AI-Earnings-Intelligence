from dataclasses import dataclass, field
from typing import Literal

Assessment = Literal['Supported', 'Challenged', 'Insufficient Evidence']

@dataclass(frozen=True)
class ResearchEvidence:
    evidence_id: str
    description: str
    source_url: str
    citation: str
    category: str

@dataclass(frozen=True)
class HypothesisAssessment:
    hypothesis: str
    assessment: Assessment
    explanation: str
    evidence_ids: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class AIResearchResult:
    ticker: str
    thesis_id: str
    statement: str
    provider: str
    overall_assessment: Assessment
    hypotheses: list[HypothesisAssessment]
    supporting_evidence_ids: list[str]
    contradicting_evidence_ids: list[str]
    research_gaps: list[str]
    monitoring_indicators: list[str]
    limitations: str
    requires_human_review: bool = True
