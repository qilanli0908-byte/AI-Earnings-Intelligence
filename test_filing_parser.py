
from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text
)


filing_folder = Path("data/filings/NVDA")

files = sorted(
    filing_folder.glob("*_10K.html")
)

assert files, "No downloaded NVDA 10-K files found."

filepath = files[0]

print("\n========== SEC TEXT CLEANING TEST ==========")

print("Testing filing:", filepath)

# Step 1: Extract raw text.
raw_text = extract_filing_text(filepath)

# Step 2: Clean extracted text.
cleaned_text = clean_filing_text(raw_text)

print("\nRaw characters:", len(raw_text))
print("Cleaned characters:", len(cleaned_text))

print("\n========== FIRST 1500 CLEANED CHARACTERS ==========\n")

print(cleaned_text[:1500])

# Basic validation.
assert len(cleaned_text) > 1000, (
    "Cleaned filing text appears unexpectedly short."
)

assert "\n\n" not in cleaned_text, (
    "Repeated empty lines were not removed."
)

print("\nPASS: SEC filing text cleaned successfully.")
