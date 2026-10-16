"""Day 19: SEC source reconciliation. No paid AI calls.
Run from project root: .\.venv\Scripts\python.exe benchmark_financial.py
"""
import csv
import math
import time
from pathlib import Path
import requests
import pandas as pd
from sec_dynamic import get_cik, get_sec_financials, HEADERS
from src.change_detector import calculate_financial_changes
from decimal import Decimal, ROUND_HALF_UP

TICKERS = ("NVDA", "AMD", "AAPL", "WMT")
METRICS = (
    ("Revenue", "Revenue ($B)", "Revenue Source Tag", "Revenue Accession",
     ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet")),
    ("Net Income", "Net Income ($B)", "Net Income Source Tag", "Net Income Accession",
     ("NetIncomeLoss",)),
)
out = Path("benchmark_results")
out.mkdir(exist_ok=True)
rows = []

def record(ticker, period, metric, status, actual="", reference="", note=""):
    rows.append(dict(Ticker=ticker, Period=period, Metric=metric, Status=status,
                     Actual=actual, Reference=reference, Note=note))

def close(a, b, tol=0.0050001):
    return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)

for ticker in TICKERS:
    print(f"Checking {ticker}...")
    try:
        cik = get_cik(ticker)
        if not cik:
            raise ValueError("Ticker not found in SEC ticker mapping")
        result = get_sec_financials(ticker)
        if result is None or result.empty:
            raise ValueError("No financial summary returned")
        response = requests.get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            headers=HEADERS, timeout=30
        )
        response.raise_for_status()
        facts = response.json()["facts"]["us-gaap"]
        result = result.sort_values("end").tail(3).reset_index(drop=True)
        for _, item in result.iterrows():
            period = str(item["end"])
            raw_values = {}
            for metric, column, tag_column, accession_column, allowed_tags in METRICS:
                tag, accn = item[tag_column], item[accession_column]
                start = str(item["start"])
                candidates = [
                    entry for entry in facts.get(tag, {}).get("units", {}).get("USD", [])
                    if entry.get("start") == start and entry.get("end") == period
                    and entry.get("accn") == accn and entry.get("form") == "10-K"
                ]
                if tag not in allowed_tags or not candidates:
                    record(ticker, period, metric, "FAIL", item[column], "",
                           "Source tag/accession/period not found in raw SEC 10-K facts")
                    continue
                values = {entry["val"] for entry in candidates}
                if len(values) != 1:
                    record(ticker, period, metric, "REVIEW", item[column], "",
                           f"Conflicting raw values: {sorted(values)}")
                    continue
                raw = next(iter(values))
                raw_values[metric] = raw
                expected = float(
                    (Decimal(raw) / Decimal(1_000_000_000)).quantize(
                        Decimal("0.01"),
                        rounding=ROUND_HALF_UP
                    )
                )
                status = "PASS" if close(item[column], expected) else "FAIL"
                record(ticker, period, metric, status, item[column], expected,
                       f"Tag={tag}; accession={accn}; raw USD={raw}")
            if len(raw_values) == 2 and raw_values["Revenue"] != 0:
                expected_margin = round(
                    raw_values["Net Income"] / raw_values["Revenue"] * 100, 2
                )
                actual_margin = item["Net Margin (%)"]
                record(ticker, period, "Net Margin (%)",
                       "PASS" if close(actual_margin, expected_margin) else "FAIL",
                       actual_margin, expected_margin, "Recalculated from raw USD values")
        for index in range(1, len(result)):
            previous = result.iloc[index - 1]
            current = result.iloc[index]
            # Only treat consecutive comparable annual periods as YoY.
            gap = (pd.to_datetime(current["end"]) - pd.to_datetime(previous["end"])).days
            if not 330 <= gap <= 400:
                record(ticker, str(current["end"]), "Revenue Growth (%)", "REVIEW",
                       current["Revenue Growth (%)"], "",
                       f"Nonconsecutive fiscal period gap: {gap} days")
                continue
            # Displayed $B values are rounded; exact growth cannot be reconstructed
            # from those values. Re-read the provenance-linked raw USD records.
            def raw_revenue(row):
                entries = facts[row["Revenue Source Tag"]]["units"]["USD"]
                values = {e["val"] for e in entries
                          if e.get("start") == str(row["start"])
                          and e.get("end") == str(row["end"])
                          and e.get("accn") == row["Revenue Accession"]
                          and e.get("form") == "10-K"}
                return next(iter(values)) if len(values) == 1 else None
            old, new = raw_revenue(previous), raw_revenue(current)
            if old in (None, 0) or new is None:
                record(ticker, str(current["end"]), "Revenue Growth (%)", "REVIEW",
                       current["Revenue Growth (%)"], "", "Raw comparable values unavailable")
            else:
                expected = round((new / old - 1) * 100, 2)
                actual = current["Revenue Growth (%)"]
                record(ticker, str(current["end"]), "Revenue Growth (%)",
                       "PASS" if close(actual, expected) else "FAIL",
                       actual, expected, "Recalculated from raw USD values")
        changes = calculate_financial_changes(result)
        for i in range(1, len(changes)):
            prev, cur = changes.iloc[i - 1], changes.iloc[i]
            for metric, source, change in (
                ("Growth Change (pp)", "Revenue Growth (%)", "Growth Change (pp)"),
                ("Margin Change (pp)", "Net Margin (%)", "Margin Change (pp)"),
            ):
                expected = cur[source] - prev[source]
                actual = cur[change]
                if pd.isna(expected) and pd.isna(actual):
                    status = "PASS"
                elif pd.isna(expected) or pd.isna(actual):
                    status = "FAIL"
                else:
                    status = "PASS" if close(actual, expected, 1e-8) else "FAIL"
                record(ticker, str(cur["end"]), metric, status, actual, expected,
                       "Recomputed from displayed input columns")
        time.sleep(0.2)
    except Exception as exc:
        record(ticker, "", "Company run", "ERROR", "", "",
               f"{type(exc).__name__}: {exc}")

with (out / "financial_reconciliation.csv").open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
counts = pd.Series([r["Status"] for r in rows]).value_counts().to_dict()
print("\nRESULTS:", counts)
print("Saved:", out / "financial_reconciliation.csv")
print("NOTE: SEC raw-record reconciliation is not independent annual-report validation.")
if counts.get("FAIL", 0) or counts.get("ERROR", 0) or counts.get("REVIEW", 0):
    print("Review non-PASS rows before claiming any accuracy score.")
