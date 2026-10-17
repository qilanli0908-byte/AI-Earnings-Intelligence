import ast, pathlib, sys, unittest
from types import SimpleNamespace as NS
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from src.thesis_models import InvestmentThesis, ThesisHypothesis
from src.ai_research_engine import prepare_evidence, validate_result
from src.ai_mock_provider import MockResearchProvider
from src.ai_openai_provider import OpenAIResearchProvider, LiveAPIDisabled
from src.ai_config import get_mode, LIVE_API_ENABLED

def profile(ticker):
 return NS(identity=NS(ticker=ticker,cik='2488'),financial=NS(fiscal_year_end='2025-12-27',revenue_billions=34.64,net_income_billions=4.34,revenue_growth_pct=34.34,net_margin_pct=12.51),filing_sources=[])
def thesis(ticker):
 return InvestmentThesis(thesis_id=ticker+'-TEST',ticker=ticker,thesis_type='Bull',statement='Data center growth over three years',hypotheses=[ThesisHypothesis('Data center demand stays strong')])
class Tests(unittest.TestCase):
 def test_mock_no_key(self):
  self.assertEqual(get_mode(),'mock'); self.assertFalse(LIVE_API_ENABLED)
  t=thesis('AMD'); e=prepare_evidence(profile('AMD'),t); r=validate_result(MockResearchProvider().analyze(t,e),t,e)
  self.assertEqual(r.overall_assessment,'Insufficient Evidence'); self.assertEqual(r.supporting_evidence_ids,[])
  self.assertTrue(e[0].source_url.endswith('CIK0000002488.json'))
 def test_cross_company(self):
  with self.assertRaises(ValueError): prepare_evidence(profile('NVDA'),thesis('AMD'))
 def test_live_disabled(self):
  with self.assertRaises(LiveAPIDisabled): OpenAIResearchProvider()
 def test_no_api_imports(self):
  for name in ['ai_config','ai_provider','ai_mock_provider','ai_openai_provider','ai_research_models','ai_research_engine','ai_research_ui']:
   s=(ROOT/'src'/f'{name}.py').read_text(); tree=ast.parse(s)
   imports=[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
   imports += [n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
   self.assertFalse(any(x.startswith(('openai','requests','httpx','urllib.request')) for x in imports),name)
 def test_fake_reference_rejected(self):
  from dataclasses import replace
  t=thesis('AMD'); e=prepare_evidence(profile('AMD'),t); r=MockResearchProvider().analyze(t,e)
  with self.assertRaises(ValueError): validate_result(replace(r,supporting_evidence_ids=['FAKE']),t,e)
if __name__=='__main__': unittest.main()
