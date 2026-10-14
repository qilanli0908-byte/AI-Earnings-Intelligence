
from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text,
    extract_section
)

from src.filing_diff import compare_filing_sections


folder = Path("data/filings/NVDA")

# Explicitly identify the filings to avoid reversing old/new.
old_file = folder / "NVDA_000104581025000023_10K.html"
new_file = folder / "NVDA_000104581026000021_10K.html"

assert old_file.exists(), f"Missing: {old_file}"
assert new_file.exists(), f"Missing: {new_file}"


def get_risk_factors(filepath):
    raw_text = extract_filing_text(filepath)
    clean_text = clean_filing_text(raw_text)

    return extract_section(
        clean_text,
        "1A",
        "1B"
    )


old_risks = get_risk_factors(old_file)
new_risks = get_risk_factors(new_file)

result = compare_filing_sections(
    old_risks,
    new_risks
)

print("\n========== NVDA RISK FACTORS DIFF ==========")

print("Old filing:", old_file.name)
print("New filing:", new_file.name)

print("\nOld comparison units:", result["old_units"])
print("New comparison units:", result["new_units"])

print("\nAdded:", result["added_count"])
print("Removed:", result["removed_count"])
print("Unchanged:", result["unchanged_count"])

print("\n========== FIRST 5 ADDED UNITS ==========")

for item in result["added"][:5]:
    print("\n+", item[:350])

print("\n========== FIRST 5 REMOVED UNITS ==========")

for item in result["removed"][:5]:
    print("\n-", item[:350])

print("\nPASS: Real filing comparison completed.")
