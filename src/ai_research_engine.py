"""Construct a bounded evidence inventory from already-loaded profile data."""
from urllib.parse import urlparse
from src.ai_research_models import ResearchEvidence
from src.thesis_models import InvestmentThesis

ALLOWED_HOSTS = {'sec.gov', 'www.sec.gov', 'data.sec.gov'}

def valid_sec_url(url: str) -> bool:
    p = urlparse(url.strip())
    return p.scheme == 'https' and p.hostname in ALLOWED_HOSTS and not p.username and not p.password

def prepare_evidence(profile, thesis: InvestmentThesis) -> list[ResearchEvidence]:
    ticker = profile.identity.ticker.strip().upper()
    if ticker != thesis.ticker.strip().upper():
        raise ValueError('Cross-company thesis blocked')
    result = []
    financial = profile.financial
    cik = str(profile.identity.cik).strip()
    if financial is not None and cik.isdecimal() and int(cik) > 0:
        result.append(ResearchEvidence(
            evidence_id='FIN-1', category='Consolidated financial context',
            description=(f'Fiscal year ended {financial.fiscal_year_end}; '
                f'revenue ${financial.revenue_billions:.2f}B; '
                f'net income ${financial.net_income_billions:.2f}B; '
                f'revenue growth {financial.revenue_growth_pct:.2f}%; '
                f'net margin {financial.net_margin_pct:.2f}%. '
                'Company-wide figures do not establish segment-level performance.'),
            source_url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json',
            citation=f'SEC Company Facts, CIK {int(cik):010d}, FY end {financial.fiscal_year_end}; tag/period mapping requires review.',
        ))
    for i, filing in enumerate(profile.filing_sources[:2], 1):
        if valid_sec_url(filing.sec_url):
            result.append(ResearchEvidence(
                evidence_id=f'FILING-{i}', category='Filing metadata only',
                description=f'{filing.form} filed {filing.filing_date}; content not supplied to the analyzer.',
                source_url=filing.sec_url, citation=filing.accession_number,
            ))
    for i, item in enumerate(thesis.evidence, 1):
        if valid_sec_url(item.source_url) and item.citation.strip():
            result.append(ResearchEvidence(
                evidence_id=f'THESIS-{i}', category='User-supplied claim, not independently verified',
                description=item.description, source_url=item.source_url, citation=item.citation,
            ))
    return result

def validate_result(result, thesis, inventory):
    if result.ticker != thesis.ticker or result.thesis_id != thesis.thesis_id:
        raise ValueError('AI result identity mismatch')
    if result.provider != 'MOCK / OFFLINE' or not result.requires_human_review:
        raise ValueError('Unsafe provider or review state')
    ids = {e.evidence_id for e in inventory}
    referenced = result.supporting_evidence_ids + result.contradicting_evidence_ids
    referenced += [eid for h in result.hypotheses for eid in h.evidence_ids]
    if any(eid not in ids for eid in referenced):
        raise ValueError('Invented evidence reference')
    if any(not valid_sec_url(e.source_url) or not e.citation.strip() for e in inventory):
        raise ValueError('Invalid evidence provenance')
    return result
