
from src.filing_diff import compare_filing_sections


old_text = """
Revenue increased significantly during the fiscal year.
The company faces supply chain disruptions.
Operating expenses remained relatively stable.
"""

new_text = """
Revenue increased significantly during the fiscal year.
The company faces increased export restrictions.
Operating expenses remained relatively stable.
The company expects additional infrastructure investment.
"""


result = compare_filing_sections(
    old_text,
    new_text
)

print("\n========== FILING DIFF TEST ==========")

print("Old units:", result["old_units"])
print("New units:", result["new_units"])
print("Added:", result["added_count"])
print("Removed:", result["removed_count"])
print("Unchanged:", result["unchanged_count"])

print("\nADDED:")
for item in result["added"]:
    print("+", item)

print("\nREMOVED:")
for item in result["removed"]:
    print("-", item)


assert result["added_count"] == 2
assert result["removed_count"] == 1
assert result["unchanged_count"] == 2

print("\nPASS: Filing Diff Engine works correctly.")
