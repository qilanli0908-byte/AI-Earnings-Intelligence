import unittest, tempfile
from pathlib import Path
from types import SimpleNamespace as NS
from src.ai_filing_evidence import candidate_terms, rank_passage, retrieve_filing_candidates, local_filing_path
from src.thesis_models import InvestmentThesis, ThesisHypothesis

class Phase3(unittest.TestCase):
    def test_phrase_relevance_beats_generic_overlap(self):
        terms=['infrastructure','demand']
        a=rank_passage('AI infrastructure demand depends on access to energy capacity and supply chain resources.',terms,'ai infrastructure demand')
        b=rank_passage('The graphics infrastructure has broad demand across our products and distribution.',terms,'ai infrastructure demand')
        self.assertGreater(a[0],b[0])
    def test_risk_label_is_not_contradiction(self):
        t=InvestmentThesis(thesis_id='NVDA-T',ticker='NVDA',thesis_type='Bull',statement='AI infrastructure demand remains strong',hypotheses=[ThesisHypothesis('AI infrastructure demand remains strong')])
        p=NS(identity=NS(ticker='NVDA'),filing_sources=[NS(sec_url='https://www.sec.gov/Archives/example',accession_number='0001045810-26-000021')])
        with tempfile.TemporaryDirectory() as d:
            path=local_filing_path('NVDA','0001045810-26-000021',d);path.parent.mkdir(parents=True)
            path.write_text('<p>AI infrastructure demand could face shortages of energy capacity and access to capital, which may constrain future deployments and expansion for our customers.</p>')
            result,_=retrieve_filing_candidates(p,t,d)
            self.assertTrue(result)
            self.assertIn('candidate',result[0].category.lower())
            self.assertNotIn('verified contradiction',result[0].category.lower())
    def test_no_company_name_as_term(self):
        t=InvestmentThesis(thesis_id='NVDA-T',ticker='NVDA',thesis_type='Bull',statement='NVIDIA AI infrastructure demand',hypotheses=[])
        self.assertNotIn('nvidia',candidate_terms(t))
if __name__=='__main__': unittest.main()
