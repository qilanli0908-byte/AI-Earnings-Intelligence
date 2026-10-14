
from pathlib import Path

from src.filing_parser import (
    extract_filing_text,
    clean_filing_text,
    extract_section
)


tickers = ["NVDA", "AMD"]

sections = {
    "Risk Factors": ("1A", "1B"),
    "MD&A": ("7", "7A")
}


for ticker in tickers:

    print(f"\n========== {ticker} SECTION VALIDATION ==========")

    folder = Path("data/filings") / ticker

    files = sorted(folder.glob("*_10K.html"))

    assert len(files) >= 2, (
        f"Expected at least two downloaded 10-K files for {ticker}."
    )

    # Validate the two locally downloaded filings.
    for filepath in files[:2]:

        print(f"\nFiling: {filepath.name}")

        raw_text = extract_filing_text(filepath)

        text = clean_filing_text(raw_text)

        for name, (start_item, end_item) in sections.items():

            section_text = extract_section(
                text,
                start_item,
                end_item
            )

            print(
                f"{name}: {len(section_text):,} characters"
            )

            print(
                "Beginning:",
                section_text[:120].replace("\n", " ")
            )

            print(
                "Ending:",
                section_text[-120:].replace("\n", " ")
            )

            assert len(section_text) > 1000

        print("PASS: Both sections extracted.")


print("\nALL SECTION VALIDATION TESTS PASSED.")
