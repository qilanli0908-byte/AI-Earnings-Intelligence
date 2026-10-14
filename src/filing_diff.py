
import difflib
import re



def normalize_comparison_text(text):
    """
    Normalize SEC filing text for comparison.

    Removes standalone page numbers and
    table-of-contents artifacts, then joins
    wrapped lines into continuous text.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        # Remove standalone page numbers.
        if re.fullmatch(r"\d{1,3}", line):
            continue

        # Remove standalone Table of Contents headers.
        if re.fullmatch(
            r"Table\s+of\s+Contents",
            line,
            flags=re.IGNORECASE
        ):
            continue

        if line:
            lines.append(line)

    # Join HTML-extracted line breaks with spaces.
    # Sentence splitting happens in the next function.
    normalized = " ".join(lines)

    # Standardize repeated whitespace.
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()



def split_into_comparison_units(text):
    """
    Split cleaned text into sentence-like comparison units.

    This is a preliminary rule-based segmentation method.
    """

    text = normalize_comparison_text(text)

    # Treat line breaks and sentence-ending punctuation
    # as possible comparison boundaries.
    units = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )

    return [
        unit.strip()
        for unit in units
        if len(unit.strip()) >= 20
    ]


def compare_filing_sections(old_text, new_text):
    """
    Compare two SEC filing sections.

    Returns added, removed and unchanged text units.
    """

    old_units = split_into_comparison_units(old_text)

    new_units = split_into_comparison_units(new_text)

    matcher = difflib.SequenceMatcher(
        None,
        old_units,
        new_units,
        autojunk=False
    )

    added = []
    removed = []
    unchanged = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":

            unchanged.extend(old_units[i1:i2])

        elif tag == "insert":

            added.extend(new_units[j1:j2])

        elif tag == "delete":

            removed.extend(old_units[i1:i2])

        elif tag == "replace":

            removed.extend(old_units[i1:i2])
            added.extend(new_units[j1:j2])

    return {
        "old_units": len(old_units),
        "new_units": len(new_units),
        "added_count": len(added),
        "removed_count": len(removed),
        "unchanged_count": len(unchanged),
        "added": added,
        "removed": removed,
        "unchanged": unchanged
    }


def match_revised_disclosures(diff_result, threshold=0.75):
    """
    Match revised disclosures using two-stage similarity filtering.

    Stage 1: Fast approximate similarity.
    Stage 2: Full similarity for promising candidates.

    Similarity is textual, not a measure of financial significance.
    """

    added = diff_result["added"].copy()
    removed = diff_result["removed"].copy()

    candidates = []

    for old_index, old_text in enumerate(removed):

        for new_index, new_text in enumerate(added):

            # Skip pairs with substantially different lengths.
            old_length = len(old_text)
            new_length = len(new_text)

            if old_length == 0 or new_length == 0:
                continue

            length_ratio = min(
                old_length,
                new_length
            ) / max(
                old_length,
                new_length
            )

            if length_ratio < threshold:
                continue

            # Fast initial similarity check.
            matcher = difflib.SequenceMatcher(
                None,
                old_text,
                new_text
            )

            if matcher.quick_ratio() < threshold:
                continue

            # Full comparison only for promising candidates.
            similarity = matcher.ratio()

            if similarity >= threshold:

                candidates.append(
                    (
                        similarity,
                        old_index,
                        new_index
                    )
                )

    # Match the strongest candidate pairs first.
    candidates.sort(reverse=True)

    matched_old = set()
    matched_new = set()

    revised = []

    for similarity, old_index, new_index in candidates:

        if old_index in matched_old:
            continue

        if new_index in matched_new:
            continue

        matched_old.add(old_index)
        matched_new.add(new_index)

        revised.append({
            "old": removed[old_index],
            "new": added[new_index],
            "similarity": round(similarity, 3)
        })

    remaining_added = [
        text
        for index, text in enumerate(added)
        if index not in matched_new
    ]

    remaining_removed = [
        text
        for index, text in enumerate(removed)
        if index not in matched_old
    ]

    return {
        "revised": revised,
        "added": remaining_added,
        "removed": remaining_removed,
        "revised_count": len(revised),
        "added_count": len(remaining_added),
        "removed_count": len(remaining_removed)
    }

def is_formatting_only_change(old_text, new_text):
    """
    Detect changes caused only by punctuation,
    capitalization, or whitespace.

    Returns True if the normalized wording is identical.
    """

    def normalize(text):

        # Ignore capitalization.
        text = text.lower()

        # Remove punctuation, but preserve words and digits.
        text = re.sub(r"[^\w\s]", " ", text)

        # Standardize whitespace.
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    return normalize(old_text) == normalize(new_text)
