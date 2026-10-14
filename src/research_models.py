
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResearchAssessment:
    ticker: str
    section: str
    change_type: str

    old_disclosure: Optional[str]
    new_disclosure: Optional[str]

    significance: str
    research_priority: str

    evidence: List[str] = field(default_factory=list)
    rationale: str = ""
    research_questions: List[str] = field(default_factory=list)

    model_name: Optional[str] = None
    requires_human_review: bool = True
