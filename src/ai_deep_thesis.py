"""Offline, deterministic research scaffolding. Mapping is NOT evidence interpretation."""
import re
from difflib import SequenceMatcher
from src.ai_filing_evidence import STOP, TOPIC_PHRASES

def _tokens(s):
    return set(w for w in re.findall(r'[a-z][a-z0-9-]{3,}', s.lower()) if w not in STOP)

def decompose_thesis(thesis):
    """Use user-saved hypotheses verbatim; never invent factual assertions."""
    saved = [h.description.strip() for h in thesis.hypotheses if h.description.strip()]
    return list(dict.fromkeys(saved or [thesis.statement.strip()]))

def map_candidates(hypotheses, inventory):
    """Return candidate IDs by lexical relevance; no support/challenge judgments."""
    passages = [e for e in inventory if e.evidence_id.startswith('PASSAGE-')]
    output = []
    for hypothesis in hypotheses:
        terms = _tokens(hypothesis)
        phrases = [p for p in TOPIC_PHRASES if p in hypothesis.lower()]
        scored = []
        for e in passages:
            content = e.description.lower()
            overlap = len(terms & _tokens(content))
            shared = sum(p in content for p in phrases)
            score = overlap + 3 * shared
            if score: scored.append((score, e.evidence_id))
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        output.append((hypothesis, [eid for _, eid in scored[:5]]))
    return output

def near_duplicate(a, b):
    """Compare substantive normalized text, not only its first 160 characters."""
    def norm(s): return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()
    x, y = norm(a), norm(b)
    if not x or not y: return False
    if x == y: return True
    shorter, longer = sorted((x, y), key=len)
    if len(shorter) >= 150 and shorter in longer: return True
    return SequenceMatcher(None, x[:1200], y[:1200], autojunk=False).ratio() >= .88
