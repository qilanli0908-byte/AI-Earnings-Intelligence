
from dataclasses import dataclass
from typing import Literal

from src.thesis_models import InvestmentThesis


ImpactType = Literal[
    "Potential Support",
    "Potential Challenge",
    "Needs Review",
]


@dataclass
class ThesisMonitoringResult:
    thesis_id: str
    ticker: str
    thesis_type: str
    financial_signal: str
    impact: ImpactType
    explanation: str
    requires_human_review: bool = True


def monitor_thesis(
    thesis: InvestmentThesis,
    financial_signal: str,
) -> ThesisMonitoringResult:
    """
    Assess how a financial signal may affect a thesis.

    This is a rule-based research alert, not an investment
    recommendation or proof that a thesis is correct.
    """
    signal = financial_signal.strip().lower()

    positive_signals = (
        "improving financial momentum",
        "accelerating growth",
        "margin expansion",
    )

    caution_signals = (
        "growth moderation",
        "decelerating growth",
        "margin compression",
        "contraction",
    )

    is_positive = any(item in signal for item in positive_signals)
    is_caution = any(item in signal for item in caution_signals)

    # Mixed signals should not be forced into a bullish/bearish result.
    if is_positive and is_caution:
        impact = "Needs Review"
        explanation = (
            "The financial signal contains both supportive and "
            "cautionary indicators. Review the underlying SEC data."
        )

    elif not is_positive and not is_caution:
        impact = "Needs Review"
        explanation = (
            "The financial signal does not match a predefined rule. "
            "Human review is required."
        )

    elif thesis.thesis_type == "Bull":
        if is_positive:
            impact = "Potential Support"
            explanation = (
                "The financial signal may support the bull thesis, "
                "but does not verify its future assumptions."
            )
        else:
            impact = "Potential Challenge"
            explanation = (
                "The financial signal may challenge the bull thesis. "
                "Review the underlying growth or margin assumptions."
            )

    else:
        if is_caution:
            impact = "Potential Support"
            explanation = (
                "The financial signal may support the bear thesis, "
                "but additional evidence is needed."
            )
        else:
            impact = "Potential Challenge"
            explanation = (
                "The financial signal may challenge the bear thesis. "
                "Review whether its risk assumptions remain valid."
            )

    return ThesisMonitoringResult(
        thesis_id=thesis.thesis_id,
        ticker=thesis.ticker,
        thesis_type=thesis.thesis_type,
        financial_signal=financial_signal,
        impact=impact,
        explanation=explanation,
    )
