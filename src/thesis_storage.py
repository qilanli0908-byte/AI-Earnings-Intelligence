
import json
import re
from dataclasses import asdict
from pathlib import Path
from src.thesis_validation import validate_thesis
from src.thesis_models import (
    InvestmentThesis,
    ThesisEvidence,
    ThesisHypothesis,
)


STORAGE_DIR = Path("data/theses")


def _validate_ticker(ticker: str) -> str:
    ticker = ticker.strip().upper()

    if not re.fullmatch(r"[A-Z0-9.-]{1,12}", ticker):
        raise ValueError(f"Invalid ticker: {ticker!r}")

    return ticker


def _get_storage_path(ticker: str) -> Path:
    ticker = _validate_ticker(ticker)
    return STORAGE_DIR / f"{ticker}.json"


def save_thesis(thesis: InvestmentThesis) -> None:
    """
    Save or update one thesis without deleting other theses
    belonging to the same company.
    """
    ticker = _validate_ticker(thesis.ticker)
    thesis.ticker = ticker

    validate_thesis(thesis)

    existing = load_theses(ticker)

    # Replace a thesis if its thesis_id already exists.
    thesis_map = {
        item.thesis_id: item
        for item in existing
    }

    thesis_map[thesis.thesis_id] = thesis

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    path = _get_storage_path(ticker)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            [asdict(item) for item in thesis_map.values()],
            file,
            indent=2,
            ensure_ascii=False,
        )


def load_theses(ticker: str) -> list[InvestmentThesis]:
    """
    Load all saved theses for one ticker.
    Return an empty list if none have been saved.
    """
    path = _get_storage_path(ticker)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    theses = []

    for record in records:
        record["evidence"] = [
            ThesisEvidence(**item)
            for item in record.get("evidence", [])
        ]

        record["hypotheses"] = [
            ThesisHypothesis(**item)
            for item in record.get("hypotheses", [])
        ]

        theses.append(InvestmentThesis(**record))

    return theses
