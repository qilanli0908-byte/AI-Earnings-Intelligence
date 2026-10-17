import tempfile, unittest
from types import SimpleNamespace as NS
from src.ai_deep_thesis import decompose_thesis, map_candidates, near_duplicate
from src.ai_filing_evidence import retrieve_filing_candidates, local_filing_path
from src.ai_research_models import ResearchEvidence
from src.thesis_models import InvestmentThesis, ThesisHypothesis

class Phase4(unittest.TestCase):
    def thesis(self):
        return InvestmentThesis(thesis_id='NVDA-T',ticker='NVDA',thesis_type='Bull',statement='AI infrastructure demand will remain strong',hypotheses=[ThesisHypothesis('AI infrastructure demand will remain strong')])
    def test_user_hypotheses_are_preserved(self):
        self.assertEqual(decompose_thesis(self.thesis()),['AI infrastructure demand will remain strong'])
    def test_near_duplicate_and_distinct(self):
        a='The availability of data centers, energy, and capital to support the buildout of NVIDIA AI infrastructure is crucial, and shortages could impact future revenue.'
        b='The availability of data centers, energy and capital to support the buildout of NVIDIA AI infrastructure is crucial and shortages could impact future revenue.'
        c='Export control restrictions could limit international sales and market access for certain computing products.'
        self.assertTrue(near_duplicate(a,b)); self.assertFalse(near_duplicate(a,c))
    def test_mapping_is_candidate_only(self):
        e=ResearchEvidence('PASSAGE-1-1','AI infrastructure demand and energy capacity','https://www.sec.gov/Archives/example','citation','Potential risk-context candidate')
        mapped=map_candidates(decompose_thesis(self.thesis()),[e]);self.assertEqual(mapped[0][1],['PASSAGE-1-1'])
    def test_retrieval_deduplicates(self):
        t=self.thesis();p=NS(identity=NS(ticker='NVDA'),filing_sources=[NS(sec_url='https://www.sec.gov/Archives/example',accession_number='0001045810-26-000021')])
        a='The availability of data centers, energy, and capital to support the buildout of NVIDIA AI infrastructure is crucial, and shortages could impact future revenue.'
        b='The availability of data centers, energy and capital to support the buildout of NVIDIA AI infrastructure is crucial and shortages could impact future revenue.'
        with tempfile.TemporaryDirectory() as d:
            path=local_filing_path('NVDA','0001045810-26-000021',d);path.parent.mkdir(parents=True)
            path.write_text('<html><body><p>'+a+'</p><p>'+b+'</p></body></html>')
            result,_=retrieve_filing_candidates(p,t,d)
            self.assertEqual(len(result),1)
if __name__=='__main__':unittest.main()
