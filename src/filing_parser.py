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
    """
    Extract a 10-K section between two item headings.

    This initial implementation expects:
    - One table-of-contents occurrence
    - One main-body occurrence
    - A valid start/end section order

    Ambiguous documents raise ValueError.
    """

    start_candidates = find_section_candidates(
        text,
        start_item
    )

    end_candidates = find_section_candidates(
        text,
        end_item
    )

    # For now, require exactly two occurrences:
    # one in the contents and one in the main report.
    if len(start_candidates) != 2:
        raise ValueError(
            f"Expected 2 candidates for Item {start_item}, "
            f"found {len(start_candidates)}."
        )

    if len(end_candidates) != 2:
        raise ValueError(
            f"Expected 2 candidates for Item {end_item}, "
            f"found {len(end_candidates)}."
        )

    # The second occurrence is the body candidate.
    start = start_candidates[1]["start"]
    end = end_candidates[1]["start"]

    if end <= start:
        raise ValueError(
            f"Invalid section order: Item {start_item} "
            f"must appear before Item {end_item}."
        )

    section_text = text[start:end].strip()

    if len(section_text) < 1000:
        raise ValueError(
            f"Extracted Item {start_item} appears too short."
        )

    return section_text
