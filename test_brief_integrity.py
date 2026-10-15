
from src.brief_models import (
    BriefEvidence,
    BriefSection,
    ResearchBrief,
)
from src.brief_integrity import (
    REQUIRED_SECTIONS,
    validate_brief_integrity,
)


def make_brief():
    sections = [
        BriefSection(
            title=title,
            summary=f"Example summary for {title}.",
        )
        for title in REQUIRED_SECTIONS
    ]

    return ResearchBrief(
        ticker="NVDA",
        company_name="NVIDIA CORP",
        fiscal_year_end="2026-01-25",
        sections=sections,
    )


def run_tests():
    # 1. Valid structure
    brief = make_brief()

    report = validate_brief_integrity(
        brief,
        expected_ticker="NVDA",
    )

    assert report.passed is True
    assert report.errors == []

    print("PASS: Valid brief structure")

    # 2. Cross-company mismatch
    report = validate_brief_integrity(
        brief,
        expected_ticker="AMD",
    )

    assert report.passed is False
    assert any(
        "Company mismatch" in error
        for error in report.errors
    )

    print("PASS: Cross-company mismatch rejected")

    # 3. Missing section
    missing = make_brief()
    missing.sections.pop()

    report = validate_brief_integrity(
        missing,
        expected_ticker="NVDA",
    )

    assert report.passed is False

    print("PASS: Missing section detected")

    # 4. Invalid SEC source
    invalid = make_brief()

    filing_section = next(
        section
        for section in invalid.sections
        if section.title == "SEC Filing Sources"
    )

    filing_section.evidence.append(
        BriefEvidence(
            description="Example filing",
            evidence_type="SEC Filing",
            verification_status="Requires Review",
            source_url="https://example.com/fake-filing",
            citation="TEST-001",
        )
    )

    report = validate_brief_integrity(
        invalid,
        expected_ticker="NVDA",
    )

    assert report.passed is False
    assert any(
        "Invalid SEC source URL" in error
        for error in report.errors
    )

    print("PASS: Invalid SEC URL rejected")

    # 5. Verified must not be automatic
    unreviewed = make_brief()

    unreviewed.sections[0].evidence.append(
        BriefEvidence(
            description="Unreviewed example",
            evidence_type="Investment Thesis",
            verification_status="Verified",
        )
    )

    report = validate_brief_integrity(
        unreviewed,
        expected_ticker="NVDA",
    )

    assert report.passed is False

    print("PASS: Unreviewed Verified claim rejected")

    # 6. Missing financial attribution is a warning
    warning_brief = make_brief()

    financial_section = next(
        section
        for section in warning_brief.sections
        if section.title == "Financial Momentum"
    )

    financial_section.evidence.append(
        BriefEvidence(
            description="Historical financial metrics",
            evidence_type="SEC Financial",
            verification_status="Requires Review",
        )
    )

    report = validate_brief_integrity(
        warning_brief,
        expected_ticker="NVDA",
    )

    assert report.passed is True
    assert len(report.warnings) == 2

    print("PASS: Missing financial attribution flagged")

    print("\nALL BRIEF INTEGRITY TESTS PASSED")


if __name__ == "__main__":
    run_tests()
