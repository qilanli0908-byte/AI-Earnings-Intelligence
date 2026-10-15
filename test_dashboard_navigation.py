
from src.dashboard_navigation import should_show_section


def run_tests():

    pages = {
        "Overview": "overview",
        "Financial Analysis": "financial",
        "Filing Comparison": "filing",
        "Thesis Tracker": "thesis",
        "Research Brief": "brief",
        "Investment Memo": "memo",
    }

    for page, expected_section in pages.items():

        assert should_show_section(
            page,
            expected_section,
        )

        for other_section in pages.values():

            if other_section != expected_section:
                assert not should_show_section(
                    page,
                    other_section,
                )

    assert not should_show_section(
        "Unknown Page",
        "financial",
    )

    print("PASS: Dashboard navigation mapping")


if __name__ == "__main__":
    run_tests()
