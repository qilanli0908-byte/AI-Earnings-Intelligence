"""Offline demonstration of schema and provenance, not LLM-generated research."""
from src.ai_research_models import AIResearchResult, HypothesisAssessment

class MockResearchProvider:
    def analyze(self, thesis, evidence):
        financial = next((e for e in evidence if e.evidence_id == 'FIN-1'), None)
        hypotheses = [h.description for h in thesis.hypotheses] or [thesis.statement]
        results = [HypothesisAssessment(
            hypothesis=h, assessment='Insufficient Evidence',
            explanation=('Available company-wide financial context does not directly verify this hypothesis. '
                         'Keyword-retrieved filing passages are candidates, not independently assessed support or contradiction.'),
            evidence_ids=[financial.evidence_id] if financial else [],
        ) for h in hypotheses]
        return AIResearchResult(
            ticker=thesis.ticker, thesis_id=thesis.thesis_id,
            statement=thesis.statement, provider='MOCK / OFFLINE',
            overall_assessment='Insufficient Evidence', hypotheses=results,
            supporting_evidence_ids=[], contradicting_evidence_ids=[],
            research_gaps=['Find thesis-specific segment and operating metrics in the relevant SEC filing.',
                           'Review MD&A and Risk Factors passages before assessing support or challenge.',
                           'Obtain independently attributable evidence for the forecast horizon.'],
            monitoring_indicators=['Segment revenue and profitability', 'Consolidated growth and margin trend',
                                   'Changes in relevant SEC disclosures'],
            limitations='Offline schema demonstration. No LLM inference, no segment-level verification, no investment recommendation.',
        )
