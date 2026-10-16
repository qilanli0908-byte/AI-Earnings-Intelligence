import re
from pathlib import Path

from bs4 import BeautifulSoup


def load_filing_html(filepath):
    """
    Load a downloaded SEC filing as HTML.

    Parameters:
        filepath: Path to a locally downloaded 10-K.

    Returns:
        BeautifulSoup object for further parsing.
    """

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(
            f"SEC filing not found: {filepath}"
        )

    if filepath.stat().st_size == 0:
        raise ValueError(
            f"SEC filing is empty: {filepath}"
        )

    html = filepath.read_bytes()

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    return soup

def extract_filing_text(filepath):
    """
    Extract readable text from a downloaded SEC filing.

    Returns:
        A string containing the filing's extracted text.
    """

    soup = load_filing_html(filepath)

    # Remove elements that are not part of the visible report.
    for element in soup([
        "script",
        "style",
        "noscript"
    ]):
        element.decompose()

    # Extract text while preserving basic line separation.
    text = soup.get_text(separator="\n", strip=True)

    return text

def clean_filing_text(text):
    """
    Clean extracted SEC filing text while preserving
    basic paragraph and section boundaries.
    """

    if not text:
        return ""

    # Normalize common whitespace characters.
    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")

    # Normalize Windows and older Mac line endings.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace repeated spaces and tabs with one space.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove leading/trailing whitespace on each line.
    lines = [
        line.strip()
        for line in text.split("\n")
    ]

    # Remove empty lines.
    lines = [
        line
        for line in lines
        if line
    ]

    return "\n".join(lines)


def find_section_candidates(text, item_number):
    """
    Find possible SEC 10-K section headings.

    Match the exact item number to prevent
    Item 7 from incorrectly matching Item 7A.
    """

    if not text:
        return []

    escaped_item = re.escape(item_number)

    pattern = (
        rf"(?im)^[ \t]*"
        rf"item[ \t]+{escaped_item}"
        rf"(?![A-Za-z0-9])"
        rf"[ \t]*[.\-:\u2013\u2014]?"
        rf"[ \t]*([^\n]{{0,120}})"
    )

    matches = []

    for match in re.finditer(pattern, text):

        matches.append({
            "item": item_number,
            "start": match.start(),
            "end": match.end(),
            "heading": match.group(0).strip()
        })

    return matches

def extract_section(text, start_item, end_item):
    """Conservative extraction; anchor canonical headings where identifiable.

    Avoid treating a body cross-reference such as 'Item 1A\n. Such attacks'
    as a new section. Ambiguous matches still raise for manual review.
    """
    if not text:
        raise ValueError("Filing text is empty.")
    starts = find_section_candidates(text, start_item)
    ends = find_section_candidates(text, end_item)
    if not starts or not ends:
        raise ValueError(f"Missing section heading: Item {start_item} ({len(starts)}), Item {end_item} ({len(ends)}).")

    # Accept title case and uppercase, but require the actual canonical title.
    # Exclude table-of-contents entries: their title is followed by a page number.
    titles = {
        "1A": r"RISK[ \t]+FACTORS\b",
        "1B": r"UNRESOLVED[ \t]+STAFF[ \t]+COMMENTS\b",
        "7": r"MANAGEMENT[’']S[ \t]+DISCUSSION[ \t]+AND[ \t]+ANALYSIS\b",
        "7A": r"QUANTITATIVE[ \t]+AND[ \t]+QUALITATIVE[ \t]+DISCLOSURES?\b",
    }

    def canonical(candidate, item):
        heading = candidate["heading"]
        prefix = re.match(r"^ITEM[ \t]+" + re.escape(item) +
                          r"(?![A-Za-z0-9])[ \t]*[.\-:–—]?[ \t]*", heading, re.I)
        if not prefix:
            return False
        remainder = heading[prefix.end():].strip()
        following_lines = text[candidate["end"]:].split("\n", 3)
        if not remainder:
            remainder = following_lines[1].strip() if len(following_lines) > 1 else ""
            after_title = following_lines[2].strip() if len(following_lines) > 2 else ""
        else:
            after_title = following_lines[1].strip() if len(following_lines) > 1 else ""
        title_pattern = titles.get(item.upper())
        if not title_pattern or not re.match(title_pattern, remainder, re.I):
            return False
        # TOC entries have a standalone page number immediately after the title.
        if re.fullmatch(r"\d{1,3}", after_title):
            return False
        # Narrative references often end with a quote/comma on the next line.
        if after_title.startswith((".", ",", "\"", "”", "’", "\'")):
            return False
        return True

    canonical_starts = [c for c in starts if canonical(c, start_item)]
    canonical_ends = [c for c in ends if canonical(c, end_item)]
    if len(canonical_starts) != 1 or len(canonical_ends) != 1:
        raise ValueError(
            f"Canonical heading ambiguity for Item {start_item} / Item {end_item}: "
            f"{len(canonical_starts)} starts, {len(canonical_ends)} ends. Manual review required."
        )
    starts, ends = canonical_starts, canonical_ends

    possible = []
    for candidate in starts:
        following = [e for e in ends if e["start"] > candidate["start"]]
        if not following:
            continue
        end = following[0]
        body = text[candidate["end"]:end["start"]].strip()
        if len(body) < 1000:
            continue
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if len(body) < 3000 and sum(len(line) >= 80 for line in lines) < 3:
            continue
        possible.append((candidate, end, body))
    if len(possible) != 1:
        diagnostics = [(a["start"], b["start"], len(body)) for a,b,body in possible]
        raise ValueError(f"Ambiguous Item {start_item} to Item {end_item} extraction: "
                         f"{len(possible)} plausible ranges; {diagnostics}. Manual review required.")
    start, end, _ = possible[0]
    return text[start["start"]:end["start"]].strip()


# Legacy EDGAR filings sometimes split ITEM and its number across lines.
# This fallback is deliberately narrow: it runs only when the normal parser
# cannot find either heading, and still requires canonical title text.
_original_extract_section = extract_section


def extract_section(text, start_item, end_item):
    if (start_item, end_item) != ("7", "7A") or find_section_candidates(text, "7"):
        return _original_extract_section(text, start_item, end_item)
    legacy_start = re.compile(
        r"(?im)^ITEM\n7\.\s+MANAGEMENT[’']S\s+DISCUSSION\s+AND\s+ANALYSIS\s+OF\s+FINANCIAL\s+CONDITION\s+AND\s+RESULTS\s+OF\s+OPERATIONS\b"
    )
    legacy_end = re.compile(
        r"(?im)^ITEM\n7A\.\s+QUANTITATIVE\s+AND\s+QUALITATIVE\s+DISCLOSURES?\s+ABOUT\s+MARKET\s+RISK\b"
    )
    starts = list(legacy_start.finditer(text))
    ends = list(legacy_end.finditer(text))
    # A TOC entry is followed by a standalone page number, unlike the body.
    starts = [m for m in starts if not re.match(r"\s*\n\d{1,3}\s*(?:\n|$)", text[m.end():])]
    ends = [m for m in ends if not re.match(r"\s*\n\d{1,3}\s*(?:\n|$)", text[m.end():])]
    if len(starts) != 1 or len(ends) != 1 or ends[0].start() <= starts[0].start():
        raise ValueError("Legacy Item 7 / 7A heading ambiguity; manual review required")
    result = text[starts[0].start():ends[0].start()].strip()
    if len(result) < 1000:
        raise ValueError("Legacy Item 7 extraction is unexpectedly short; manual review required")
    return result
