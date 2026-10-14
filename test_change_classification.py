
from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text,
    extract_section
)

from src.filing_diff import (
    compare_filing_sections,
    match_revised_disclosures,
    is_formatting_only_change
)


folder = Path("data/filings/NVDA")

old_file = folder / "NVDA_000104581025000023_10K.html"
new_file = folder / "NVDA_000104581026000021_10K.html"


def get_risk_factors(filepath):
    raw_text = extract_filing_text(filepath)
    text = clean_filing_text(raw_text)
    return extract_section(text, "1A", "1B")


old_text = get_risk_factors(old_file)
new_text = get_risk_factors(new_file)

diff = compare_filing_sections(old_text, new_text)

result = match_revised_disclosures(diff, threshold=0.75)

formatting_only = []
wording_changes = []

for item in result["revised"]:
    if is_formatting_only_change(item["old"], item["new"]):
        formatting_only.append(item)
    else:
        wording_changes.append(item)


print("\n========== NVDA CHANGE CLASSIFICATION ==========")

print("Total revised:", result["revised_count"])
print("Formatting-only:", len(formatting_only))
print("Wording changes:", len(wording_changes))
print("Unmatched added:", result["added_count"])
print("Unmatched removed:", result["removed_count"])

print("\n========== FIRST 3 WORDING CHANGES ==========")

for index, item in enumerate(wording_changes[:3], start=1):
    print(f"\n--- Change {index} ---")
    print("Similarity:", item["similarity"])
    print("OLD:", item["old"][:400])
    print("NEW:", item["new"][:400])


assert (
    len(formatting_only) + len(wording_changes)
    == result["revised_count"]
)

print("\nPASS: Change classification completed.")
