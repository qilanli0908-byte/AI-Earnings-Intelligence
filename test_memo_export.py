
from src.brief_builder import build_research_brief
from src.brief_evidence import check_brief_evidence
from src.brief_integrity import validate_brief_integrity
from src.memo_export import export_investment_memo

from test_brief_builder import make_profile


def run_tests():
    # Reuse the existing offline Company Profile fixture.
    profile = make_profile()

    brief = build_research_brief(
        profile=profile,
        theses=[],
        monitoring_results=[],
    )

    brief = check_brief_evidence(brief)

    report = validate_brief_integrity(
        brief=brief,
        expected_ticker="NVDA",
    )

    assert report.passed is True, report.errors

    print("PASS: Research Brief integrity")

    # Export to PDF bytes.
    pdf_bytes = export_investment_memo(
        brief=brief,
        integrity_report=report,
    )

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000

    print("PASS: PDF generated successfully")

    # Save a local preview for manual inspection.
    from pathlib import Path

    output = Path("memo_preview.pdf")
    output.write_bytes(pdf_bytes)

    print(f"PASS: Preview saved to {output}")

    # A failed integrity report must block export.
    wrong_report = validate_brief_integrity(
        brief=brief,
        expected_ticker="AMD",
    )

    try:
        export_investment_memo(
            brief=brief,
            integrity_report=wrong_report,
        )
    except ValueError:
        print("PASS: Invalid brief export rejected")
    else:
        raise AssertionError(
            "Invalid brief was incorrectly exported"
        )

    print("\nALL MEMO EXPORT TESTS PASSED")


if __name__ == "__main__":
    run_tests()
