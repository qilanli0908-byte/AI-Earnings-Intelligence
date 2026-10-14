
from src.filing_diff import (
    compare_filing_sections,
    match_revised_disclosures
)


old_text = """
Long manufacturing lead times and uncertain supply and component availability could affect our operations.
The company faces increased competition in its markets.
"""

new_text = """
Long manufacturing lead times and uncertain supply and capacity availability could affect our operations.
The company faces increased competition in its markets.
A new regulatory requirement could affect future operations.
"""


diff_result = compare_filing_sections(
    old_text,
    new_text
)

result = match_revised_disclosures(
    diff_result,
    threshold=0.75
)


print("\n========== REVISED DISCLOSURE TEST ==========")

print("Revised:", result["revised_count"])
print("Added:", result["added_count"])
print("Removed:", result["removed_count"])

for item in result["revised"]:

    print("\nREVISED DISCLOSURE")

    print("OLD:", item["old"])
    print("NEW:", item["new"])
    print("SIMILARITY:", item["similarity"])


assert result["revised_count"] == 1
assert result["added_count"] == 1
assert result["removed_count"] == 0

assert "component availability" in result["revised"][0]["old"]
assert "capacity availability" in result["revised"][0]["new"]

print("\nPASS: Revised disclosures matched successfully.")
