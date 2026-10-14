
from src.filing_diff import is_formatting_only_change


tests = [
    (
        "Financial condition and results of operations.",
        "Financial condition, and results of operations.",
        True
    ),
    (
        "The company faces increased risks.",
        "THE COMPANY FACES INCREASED RISKS.",
        True
    ),
    (
        "Supply and component availability.",
        "Supply and capacity availability.",
        False
    ),
    (
        "These restrictions impact exports.",
        "These restrictions impacted exports.",
        False
    )
]


for old, new, expected in tests:

    actual = is_formatting_only_change(old, new)

    print(f"Expected: {expected} | Actual: {actual}")

    assert actual == expected


print("\nPASS: Formatting-only detection works correctly.")
