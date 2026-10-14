
from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text,
    find_section_candidates
)


filing_folder = Path("data/filings/NVDA")

files = sorted(
    filing_folder.glob("*_10K.html")
)

assert files, "No downloaded NVDA 10-K files found."

filepath = files[0]

print("\n========== SEC SECTION DETECTION TEST ==========")
print("Testing:", filepath)

raw_text = extract_filing_text(filepath)
text = clean_filing_text(raw_text)

for item in ["1A", "1B", "1C", "2", "7", "7A", "8"]:

    candidates = find_section_candidates(text, item)

    print(f"\nITEM {item}: {len(candidates)} candidate(s)")

    for candidate in candidates[:5]:

        print(
            f"  Position {candidate['start']:,}: "
            f"{candidate['heading'][:100]}"
        )

print("\nPASS: Section candidate detection completed.")
