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
    """Extract a section conservatively, without assuming exactly two headings.

    A candidate must be followed by the next target heading, contain substantial
    body text, and not contain another standalone heading for the start item.
    If multiple plausible body spans remain, refuse to guess.
    """
    if not text:
        raise ValueError("Filing text is empty.")

    starts = find_section_candidates(text, start_item)
    ends = find_section_candidates(text, end_item)
    if not starts or not ends:
        raise ValueError(
            f"Missing section heading: Item {start_item} ({len(starts)}), "
            f"Item {end_item} ({len(ends)})."
        )

    # Table-of-contents rows are generally short and close together; actual
    # report sections should contain meaningful prose before the next heading.
    possible = []
    for i, candidate in enumerate(starts):
        next_start = starts[i + 1]["start"] if i + 1 < len(starts) else len(text)
        following_ends = [
            end for end in ends
            if candidate["start"] < end["start"] < next_start
        ]
        if not following_ends:
            continue
        end = following_ends[0]
        body = text[candidate["end"]:end["start"]].strip()
        if len(body) < 1000:
            continue
        # Reject a likely contents entry linking to a later body heading.
        # Prefer substantial paragraph-like prose over lists of short TOC lines.
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        long_lines = sum(len(line) >= 80 for line in lines)
        if len(body) < 3000 and long_lines < 3:
            continue
        possible.append((candidate, end, body))

    if len(possible) != 1:
        diagnostics = [
            (entry[0]["start"], entry[1]["start"], len(entry[2]))
            for entry in possible
        ]
        raise ValueError(
            f"Ambiguous Item {start_item} to Item {end_item} extraction: "
            f"{len(possible)} plausible body ranges; "
            f"positions/lengths={diagnostics}. Manual review required."
        )

    start, end, _ = possible[0]
    return text[start["start"]:end["start"]].strip()
