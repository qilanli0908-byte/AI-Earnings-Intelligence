
from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text,
    extract_section
)


filing_folder = Path("data/filings/NVDA")

files = sorted(
    filing_folder.glob("*_10K.html")
)

assert files, "No downloaded NVDA 10-K files found."

filepath = files[0]

print("\n========== SECTION EXTRACTION TEST ==========")
print("Testing:", filepath)

raw_text = extract_filing_text(filepath)
text = clean_filing_text(raw_text)

sections = {
    "Risk Factors": ("1A", "1B"),
    "MD&A": ("7", "7A")
}

for name, (start_item, end_item) in sections.items():

    section_text = extract_section(
        text,
        start_item,
        end_item
    )

    print(f"\n========== {name} ==========")

    print("Extracted characters:", len(section_text))

    print("\nFirst 500 characters:\n")
    print(section_text[:500])

    print("\nLast 300 characters:\n")
    print(section_text[-300:])

    assert len(section_text) > 1000

    print(f"\nPASS: {name} extracted successfully.")
