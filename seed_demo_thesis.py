
from src.thesis_models import InvestmentThesis, ThesisHypothesis
from src.thesis_storage import save_thesis


def main():
    thesis = InvestmentThesis(
        thesis_id="NVDA-BULL-001",
        ticker="NVDA",
        thesis_type="Bull",
        statement=(
            "AI infrastructure spending will sustain NVIDIA's "
            "growth over the next three years."
        ),
        hypotheses=[
            ThesisHypothesis(
                description=(
                    "AI infrastructure demand will remain strong "
                    "over the next three years."
                ),
            )
        ],
    )

    save_thesis(thesis)

    print("PASS: Demo NVDA bull thesis saved")


if __name__ == "__main__":
    main()
