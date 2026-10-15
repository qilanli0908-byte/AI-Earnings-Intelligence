
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.thesis_models import (
    InvestmentThesis,
    ThesisEvidence,
    ThesisHypothesis,
)
from src.thesis_storage import load_theses, save_thesis


def run_tests():
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "theses"

        # Keep test data separate from actual investment research.
        with patch("src.thesis_storage.STORAGE_DIR", storage_path):

            bull = InvestmentThesis(
                thesis_id="NVDA-BULL-001",
                ticker="NVDA",
                thesis_type="Bull",
                statement="AI infrastructure spending supports growth.",
                evidence=[
                    ThesisEvidence(
                        description="Historical revenue growth.",
                        source_url="https://www.sec.gov/",
                        status="Unverified",
                    )
                ],
                hypotheses=[
                    ThesisHypothesis(
                        description="Future AI demand remains strong."
                    )
                ],
            )

            save_thesis(bull)

            loaded = load_theses("NVDA")

            assert len(loaded) == 1
            assert loaded[0].thesis_id == "NVDA-BULL-001"
            assert loaded[0].evidence[0].status == "Unverified"
            assert loaded[0].hypotheses[0].status == "Unverified"

            print("PASS: Save and load thesis")

            bear = InvestmentThesis(
                thesis_id="NVDA-BEAR-001",
                ticker="NVDA",
                thesis_type="Bear",
                statement="Growth may moderate as competition increases.",
            )

            save_thesis(bear)

            loaded = load_theses("NVDA")

            assert len(loaded) == 2

            print("PASS: Multiple theses per company")

            bull.statement = "Updated NVIDIA bull thesis."
            save_thesis(bull)

            loaded = load_theses("NVDA")

            assert len(loaded) == 2

            updated = next(
                item
                for item in loaded
                if item.thesis_id == "NVDA-BULL-001"
            )

            assert updated.statement == "Updated NVIDIA bull thesis."

            print("PASS: Updating existing thesis")

            assert load_theses("AMD") == []

            print("PASS: Company data isolation")

            try:
                load_theses("../NVDA")
            except ValueError:
                print("PASS: Invalid ticker rejected")
            else:
                raise AssertionError("Invalid ticker was accepted")

    print("\nALL DAY 11 STORAGE TESTS PASSED")


if __name__ == "__main__":
    run_tests()
