
# AI Earnings Intelligence & Thesis Tracker

An evidence-driven financial research platform designed to help investors track changes in corporate disclosures and evaluate investment hypotheses using SEC filings, financial analytics, and AI.

> Status: Active Development | 21-Day Independent Project

## 1. Project Overview

Traditional financial platforms provide extensive financial data, but analysts must still manually identify changes across filings and determine whether new evidence supports their existing investment theses.

This project aims to streamline that research workflow by combining financial data engineering, SEC filing comparison, and evidence-based AI analysis.

The objective is not to replace investment judgment, but to make financial research more systematic, transparent, and reproducible.

## 2. Current Implementation

The initial financial dashboard includes:

- Dynamic ticker input
- Historical stock price retrieval using yfinance
- Company overview and stock performance visualization
- Financial statement retrieval and ratio calculations
- Rule-based financial commentary
- SEC EDGAR Company Facts integration
- Annual revenue, net income, revenue growth, and net margin analysis

The current implementation has been tested using NVIDIA (NVDA) and AMD.

## 3. Planned Features

The following features are currently under development:

- SEC filing retrieval and section extraction
- Financial change detection
- Filing comparison (10-K / 10-Q)
- Persistent investment thesis tracking
- Evidence-linked AI research analysis
- Bull / Base / Bear scenario modeling
- Investment research memo generation
- PDF report export
- Research accuracy benchmarking

## 4. Technology Stack

- Python
- Streamlit
- pandas
- yfinance
- SEC EDGAR API
- requests
- matplotlib

Planned additions:
- SQLite
- AI API integration
- Automated testing

## 5. Project Structure

```text
AI-Earnings-Intelligence/
├── src/                  # Core research modules (under development)
├── data/                 # Local research data
├── tests/                # Automated tests
├── reports/              # Generated research reports
├── docs/                 # Technical documentation
├── web_app.py            # Current Streamlit application
├── sec_dynamic.py        # SEC financial data retrieval
├── financial_analysis.py # Financial metric calculations
├── requirements.txt
└── README.md
```

## 6. Getting Started

Clone the repository:

```bash
git clone https://github.com/qilanli0908-byte/AI-Earnings-Intelligence.git
cd AI-Earnings-Intelligence
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the current dashboard:

```bash
python -m streamlit run web_app.py
```

The application should open at:

http://localhost:8501

Note: SEC API requests require an appropriate User-Agent identifying the application and providing contact information. Configuration will be standardized during the data pipeline refactor.

## 7. Development Roadmap

| Phase | Focus |
|---|---|
| Week 1 | SEC data pipeline, financial change detection, filing comparison |
| Week 2 | Thesis tracking, AI analysis, scenario modeling, evaluation |
| Week 3 | Dashboard integration, testing, deployment, documentation |

Initial development and validation focus on NVDA and AMD. The longer-term architecture is designed to support additional SEC-reporting companies through dynamic ticker input.

## 8. Research Reliability

The project prioritizes:

- Traceable financial data sources
- Reproducible calculations
- Transparent assumptions
- Evidence-linked AI conclusions
- Explicit handling of missing or insufficient evidence

A research accuracy benchmark will be developed to evaluate the reliability of the system.

## 9. Disclaimer

This project is developed for educational and research purposes only. It does not provide personalized financial advice or investment recommendations.
