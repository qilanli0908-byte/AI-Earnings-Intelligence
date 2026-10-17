from typing import Protocol
from src.ai_research_models import AIResearchResult, ResearchEvidence
from src.thesis_models import InvestmentThesis

class ResearchProvider(Protocol):
    def analyze(self, thesis: InvestmentThesis, evidence: list[ResearchEvidence]) -> AIResearchResult: ...
