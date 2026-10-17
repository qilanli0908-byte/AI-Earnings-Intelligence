import tempfile, unittest
from pathlib import Path
from types import SimpleNamespace as NS
from src.ai_filing_evidence import retrieve_filing_candidates, local_filing_path
from src.thesis_models import InvestmentThesis, ThesisHypothesis
from src.ai_research_engine import prepare_evidence, validate_result
from src.ai_mock_provider import MockResearchProvider

def fixture(ticker='AMD', accession='0000002488-26-000018'):
    p=NS(identity=NS(ticker=ticker,cik='2488'),financial=None,filing_sources=[NS(sec_url='https://www.sec.gov/Archives/edgar/data/2488/test.htm',accession_number=accession,form='10-K',filing_date='2026-02-04')])
    t=InvestmentThesis(thesis_id=ticker+'-TEST',ticker=ticker,thesis_type='Bull',statement='Data center demand drives AMD growth',hypotheses=[ThesisHypothesis('Data center demand remains strong')])
    return p,t
class Phase2(unittest.TestCase):
    def test_local_passages_and_no_promotion(self):
        p,t=fixture()
        with tempfile.TemporaryDirectory() as root:
            f=local_filing_path('AMD',p.filing_sources[0].accession_number,root);f.parent.mkdir(parents=True)
            f.write_text('<html><p>Data center demand increased in the period as customers continued to purchase computing systems for their infrastructure and related applications.</p></html>')
            passages,notes=retrieve_filing_candidates(p,t,root)
            self.assertTrue(passages);self.assertEqual(passages[0].evidence_id,'PASSAGE-1-1')
            inventory=prepare_evidence(p,t)+passages
            result=validate_result(MockResearchProvider().analyze(t,inventory),t,inventory)
            self.assertEqual(result.overall_assessment,'Insufficient Evidence')
            self.assertEqual(result.supporting_evidence_ids,[])
    def test_real_cache_naming(self):
        expected = Path('data/filings/NVDA/NVDA_000104581026000021_10K.html')
        actual = local_filing_path('NVDA', '0001045810-26-000021', '.')
        self.assertEqual(actual, expected)
        self.assertNotIn('-', actual.name)
    def test_missing_cache_no_download(self):
        p,t=fixture()
        with tempfile.TemporaryDirectory() as root:
            passages,notes=retrieve_filing_candidates(p,t,root)
            self.assertFalse(passages);self.assertIn('no local cached HTML',notes[0])
    def test_cross_company_and_path_traversal(self):
        p,t=fixture();p.identity.ticker='NVDA'
        with self.assertRaises(ValueError): retrieve_filing_candidates(p,t)
        with self.assertRaises(ValueError): local_filing_path('../AMD','0000002488-26-000018')
    def test_no_network_import(self):
        import ast
        s=(Path(__file__).parent/'src'/'ai_filing_evidence.py').read_text(); tree=ast.parse(s)
        modules=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any(m.startswith(('requests','openai','httpx','urllib.request')) for m in modules))
if __name__=='__main__':unittest.main()
