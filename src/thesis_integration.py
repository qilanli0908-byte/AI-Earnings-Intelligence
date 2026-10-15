
import pandas as pd

from src.thesis_models import InvestmentThesis
from src.thesis_monitor import (
    ThesisMonitoringResult,
    monitor_thesis,
)


def get_latest_financial_signal(financial_changes: pd.DataFrame) -> str:
    """
    Extract the latest research signal from the financial
    Change Detector output.
    """
    if financial_changes is None or financial_changes.empty:
        raise ValueError("Financial changes are empty")

    if "Research Signal" not in financial_changes.columns:
        raise ValueError("Missing Research Signal column")

    data = financial_changes.copy()

    # SEC fiscal-year end determines chronological order.
    if "end" not in data.columns:
        raise ValueError("Missing fiscal-year end column")

    data["end"] = pd.to_datetime(data["end"], errors="coerce")

    data = data.dropna(subset=["end"])

    if data.empty:
        raise ValueError("No valid fiscal-year end dates")

    data = data.sort_values("end")

    latest_signal = data.iloc[-1]["Research Signal"]

    if pd.isna(latest_signal) or not str(latest_signal).strip():
        raise ValueError("Latest financial signal is unavailable")

    return str(latest_signal).strip()


def monitor_company_theses(
    ticker: str,
    theses: list[InvestmentThesis],
    financial_changes: pd.DataFrame,
) -> list[ThesisMonitoringResult]:
    """
    Monitor saved theses using the latest SEC financial signal.

    No AI calls or SEC network requests occur in this function.
    """
    ticker = ticker.strip().upper()

    latest_signal = get_latest_financial_signal(financial_changes)

    results = []

    for thesis in theses:
        if thesis.ticker != ticker:
            raise ValueError(
                f"Thesis ticker mismatch: {thesis.ticker} != {ticker}"
            )

        result = monitor_thesis(
            thesis=thesis,
            financial_signal=latest_signal,
        )

        results.append(result)

    return results
