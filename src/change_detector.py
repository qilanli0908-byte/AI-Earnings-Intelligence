
import pandas as pd


def calculate_financial_changes(df):
    """
    Calculate year-over-year financial changes.

    Input:
        DataFrame returned by get_sec_financials().

    Output:
        DataFrame containing financial metrics
        and additional change indicators.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    # Ensure chronological order.
    result = result.sort_values("end").reset_index(drop=True)

    # Revenue growth acceleration / deceleration.
    # Unit: percentage points (pp).
    result["Growth Change (pp)"] = (
        result["Revenue Growth (%)"].diff()
    )

    # Net margin expansion / compression.
    # Unit: percentage points (pp).
    result["Margin Change (pp)"] = (
        result["Net Margin (%)"].diff()
    )
        # Classify revenue growth trends.
    result["Growth Trend"] = result.apply(
        lambda row: classify_growth_trend(
            row["Revenue Growth (%)"],
            row["Growth Change (pp)"]
        ),
        axis=1
    )
        # Classify net margin changes.
    result["Margin Trend"] = result[
        "Margin Change (pp)"
    ].apply(classify_margin_trend)
        # Combine growth and margin trends into a research signal.
    result["Research Signal"] = result.apply(
        lambda row: generate_research_signal(
            row["Growth Trend"],
            row["Margin Trend"]
        ),
        axis=1
    )

    return result

def classify_growth_trend(revenue_growth, growth_change):
    """
    Classify revenue growth trends.

    Revenue Growth: percentage (%)
    Growth Change: percentage points (pp)
    """

    # Missing data: insufficient information.
    if pd.isna(revenue_growth):
        return "Insufficient Data"

    # Negative revenue growth means revenue contracted.
    if revenue_growth < 0:
        return "Revenue Contraction"

    # No previous growth rate available for comparison.
    if pd.isna(growth_change):
        return "No Prior Comparison"

    # Classification thresholds (percentage points).
    if growth_change > 1:
        return "Accelerating Growth"

    elif growth_change < -1:
        return "Decelerating Growth"

    else:
        return "Stable Growth"

def classify_margin_trend(margin_change):
    """
    Classify changes in net profit margin.

    Unit: percentage points (pp).

    A 1 pp threshold is used to distinguish
    meaningful changes from relatively small movements.
    """

    if pd.isna(margin_change):
        return "No Prior Comparison"

    if margin_change >= 1:
        return "Margin Expansion"

    elif margin_change <= -1:
        return "Margin Compression"

    else:
        return "Stable Margin"

def generate_research_signal(growth_trend, margin_trend):
    """
    Generate a rule-based research signal by combining
    revenue growth and net margin trends.

    Signals describe historical financial changes,
    not investment recommendations.
    """

    # Insufficient historical information.
    if growth_trend in [
        "Insufficient Data",
        "No Prior Comparison"
    ]:
        return "Insufficient Historical Data"

    # Revenue contraction deserves separate attention.
    if growth_trend == "Revenue Contraction":

        if margin_trend == "Margin Compression":
            return "Revenue and Profitability Deterioration"

        return "Revenue Contraction — Further Investigation"

    # Both growth momentum and profitability are improving.
    if (
        growth_trend == "Accelerating Growth"
        and margin_trend == "Margin Expansion"
    ):
        return "Improving Financial Momentum"

    # Growth is slowing while profitability is also weakening.
    if (
        growth_trend == "Decelerating Growth"
        and margin_trend == "Margin Compression"
    ):
        return "Growth and Margin Pressure"

    # Growth is slowing but margins remain relatively stable.
    if (
        growth_trend == "Decelerating Growth"
        and margin_trend == "Stable Margin"
    ):
        return "Growth Moderation — Stable Profitability"

    # Growth is slowing, but profitability is improving.
    if (
        growth_trend == "Decelerating Growth"
        and margin_trend == "Margin Expansion"
    ):
        return "Growth Moderation - Margin Improvement"

    # Other combinations require additional context.
    return "Mixed Financial Signals"
