
from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text,
    extract_section
)

from src.filing_diff import (
    compare_filing_sections,
    match_revised_disclosures
)


folder = Path("data/filings/NVDA")

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


old_text = get_risk_factors(old_file)
new_text = get_risk_factors(new_file)

diff_result = compare_filing_sections(
    old_text,
    new_text
)

result = match_revised_disclosures(
    diff_result,
    threshold=0.75
)


print("\n========== NVDA REVISED DISCLOSURES ==========")

print("Old filing:", old_file.name)
print("New filing:", new_file.name)

print("\nOriginal comparison:")
print("Added:", diff_result["added_count"])
print("Removed:", diff_result["removed_count"])

print("\nAfter similarity matching:")
print("Revised:", result["revised_count"])
print("Added:", result["added_count"])
print("Removed:", result["removed_count"])


print("\n========== FIRST 5 REVISED DISCLOSURES ==========")

for index, item in enumerate(result["revised"][:5], start=1):

    print(f"\n--- Revised Disclosure {index} ---")

    print("Similarity:", item["similarity"])

    print("\nOLD:")
    print(item["old"][:500])

    print("\nNEW:")
    print(item["new"][:500])


assert (
    result["revised_count"] + result["added_count"]
    == diff_result["added_count"]
)

assert (
    result["revised_count"] + result["removed_count"]
    == diff_result["removed_count"]
)

print("\nPASS: Real revised disclosure comparison completed.")
