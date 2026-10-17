import time
"""Offline thesis-aware candidate retrieval. Ranking is NOT evidence interpretation."""
from pathlib import Path
import re
from bs4 import BeautifulSoup
from src.ai_research_models import ResearchEvidence
from src.ai_research_engine import valid_sec_url

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 18_000_000
MAX_PASSAGES = 5
MAX_CHARS = 450
STOP = {'about','could','would','their','there','these','those','three','years','year','strong','remain','over','next','with','from','that','this','business','growth','company','support','sustain','revenue','maintains','maintain','position','competitive','will','might','future','nvidia','advanced','micro','devices','inc','corp','corporation'}
TOPIC_PHRASES = ('data center','ai infrastructure','artificial intelligence','customer demand','supply chain','export control','energy capacity','operating income','net sales','capital expenditure')
RISK_WORDS = ('risk','shortage','constraint','restrict','restriction','export control','competition','capacity','uncertainty','depend','delay')

def candidate_terms(thesis):
    content = ' '.join([thesis.statement] + [h.description for h in thesis.hypotheses]).lower()
    words = re.findall(r'[a-zA-Z][a-zA-Z0-9-]{3,}', content)
    return list(dict.fromkeys(w for w in words if w not in STOP))[:12]

def local_filing_path(ticker, accession, root=ROOT):
    ticker = ticker.upper().strip()
    if not re.fullmatch(r'[A-Z0-9.-]{1,12}', ticker) or not re.fullmatch(r'\d{10}-\d{2}-\d{6}', accession):
        raise ValueError('Unsafe filing identifier')
    return Path(root) / 'data' / 'filings' / ticker / f'{ticker}_{accession.replace("-", "")}_10K.html'

def rank_passage(passage, terms, thesis_text):
    """Deterministic relevance ranking only; never assigns support/challenge status."""
    lower = passage.lower()
    matches = [t for t in terms if re.search(r'\b'+re.escape(t)+r'\b', lower)]
    if not matches:
        return None
    phrases = [p for p in TOPIC_PHRASES if p in thesis_text and p in lower]
    risk_context = any(word in lower for word in RISK_WORDS)
    # A phrase shared with the actual thesis is more meaningful than generic token overlap.
    score = 3*len(phrases) + 2*len(matches) + min(len(passage), 800)/800
    if risk_context and phrases: score += 1
    if len(passage) < 110: score -= 1
    return score, matches, phrases, risk_context

def retrieve_filing_candidates(profile, thesis, root=ROOT):
    ticker = profile.identity.ticker.strip().upper()
    if ticker != thesis.ticker.strip().upper():
        raise ValueError('Cross-company filing retrieval blocked')
    terms = candidate_terms(thesis)
    thesis_text = ' '.join([thesis.statement] + [h.description for h in thesis.hypotheses]).lower()
    if not terms: return [], ['No specific thesis terms for passage retrieval.']
    evidence, notices = [], []
    for filing_index, filing in enumerate(profile.filing_sources[:2], 1):
        if not valid_sec_url(filing.sec_url):
            notices.append(f'Filing {filing_index}: invalid SEC source URL; skipped.'); continue
        path = local_filing_path(ticker, filing.accession_number, root)
        if not path.is_file():
            notices.append(f'{filing.accession_number}: no local cached HTML; skipped (no download).'); continue
        if not 0 < path.stat().st_size <= MAX_FILE_BYTES:
            notices.append(f'{filing.accession_number}: empty or over file size limit; skipped.'); continue
        start_time = time.perf_counter()
        print(f"[SEC DEBUG] Starting {filing.accession_number}", flush=True)
        soup = BeautifulSoup(path.read_bytes(), 'html.parser')
        print(f"[SEC DEBUG] HTML parsed: {time.perf_counter() - start_time:.2f}s", flush=True)
        for tag in soup(['script','style','noscript']): tag.decompose()
        blocks = []
        for tag in soup.find_all(['p','div','td','li']):
            if tag.find(['p','div','td','li']): continue
            s = re.sub(r'\s+', ' ', ' '.join(tag.stripped_strings)).strip()
            if 90 <= len(s) <= 2200: blocks.append(s)
        if not blocks:
            blocks = re.split(r'(?<=[.!?])\s+(?=[A-Z])', ' '.join(soup.stripped_strings))
        print(f"[SEC DEBUG] Blocks extracted: {len(blocks)} | {time.perf_counter() - start_time:.2f}s", flush=True)
        from src.ai_deep_thesis import near_duplicate
        # Rank first. Comparing every HTML block with every earlier block is quadratic
        # and can make the Streamlit button appear to hang on large 10-K filings.
        ranked, seen = [], set()
        for passage in blocks:
            normalized = re.sub(r'\s+', ' ', passage).strip()
            ranked_item = rank_passage(normalized, terms, thesis_text)
            if ranked_item is None: continue
            fingerprint = re.sub(r'[^a-z0-9]', '', normalized.lower())[:160]
            if fingerprint in seen: continue
            seen.add(fingerprint)
            ranked.append((ranked_item[0], normalized, *ranked_item[1:]))
        ranked.sort(key=lambda item: -item[0])
        print(f"[SEC DEBUG] Ranking completed: {len(ranked)} candidates | {time.perf_counter() - start_time:.2f}s", flush=True)
        # Only compare high-ranking candidates with a small retained set.
        deduplicated, retained = [], []
        for item in ranked:
            if any(near_duplicate(item[1], old) for old in retained): continue
            deduplicated.append(item)
            retained.append(item[1])
            if len(deduplicated) >= MAX_PASSAGES + 15: break
        ranked = deduplicated
        # Reserve a slot for a relevant risk-context candidate when available; this is NOT a contradiction finding.
        selected = ranked[:MAX_PASSAGES]
        if selected and not any(item[4] for item in selected):
            alternative = next((item for item in ranked[MAX_PASSAGES:] if item[4] and item[3]), None)
            if alternative: selected[-1] = alternative
        for rank, (score, passage, matches, phrases, risk_context) in enumerate(selected, 1):
            label = 'Potential risk-context candidate' if risk_context else 'Thesis-relevant candidate'
            evidence.append(ResearchEvidence(
                evidence_id=f'PASSAGE-{filing_index}-{rank}',
                category=f'{label} (NOT verified thesis evidence)',
                description=passage[:MAX_CHARS] + ('...' if len(passage)>MAX_CHARS else ''),
                source_url=filing.sec_url,
                citation=(f'{filing.accession_number}; local cached HTML; relevance score {score:.1f}; '
                          f'keyword matches: {", ".join(matches)}; shared phrases: {", ".join(phrases) or "none"}; '
                          'candidate only; full source and context require human review.'),
            ))
        if not ranked: notices.append(f'{filing.accession_number}: no keyword-matching passages found.')
    return evidence, notices
