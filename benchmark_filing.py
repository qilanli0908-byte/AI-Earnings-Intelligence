"""Day 19 filing structural benchmark. Uses cached 10-K HTML; no API calls."""
import csv
from pathlib import Path
from src.filing_parser import extract_filing_text, clean_filing_text, extract_section, find_section_candidates

TICKERS = ('NVDA', 'AMD', 'AAPL', 'WMT')
SECTIONS = (('1A', '1B', 'Risk Factors'), ('7', '7A', 'MD&A'))
root = Path('data/filings')
out = Path('benchmark_results')
out.mkdir(exist_ok=True)
rows = []
for ticker in TICKERS:
    files = sorted((root / ticker).glob(f'{ticker}_*_10K.html'))
    if not files:
        rows.append(dict(Ticker=ticker, File='', Section='', Status='MISSING', Characters='', StartCandidates='', EndCandidates='', Opening='', Ending='', Note='No cached 10-K HTML; download through app first'))
        continue
    for path in files:
        try:
            text = clean_filing_text(extract_filing_text(path))
        except Exception as exc:
            rows.append(dict(Ticker=ticker, File=str(path), Section='', Status='ERROR', Characters='', StartCandidates='', EndCandidates='', Opening='', Ending='', Note=f'{type(exc).__name__}: {exc}'))
            continue
        for start, end, label in SECTIONS:
            starts = find_section_candidates(text, start)
            ends = find_section_candidates(text, end)
            row = dict(Ticker=ticker, File=str(path), Section=f'Item {start} {label}', Status='', Characters='', StartCandidates=len(starts), EndCandidates=len(ends), Opening='', Ending='', Note='')
            try:
                section = extract_section(text, start, end)
                row['Characters'] = len(section)
                row['Opening'] = section[:220].replace('\n', ' ')
                row['Ending'] = section[-220:].replace('\n', ' ')
                row['Status'] = 'REVIEW'
                row['Note'] = 'Extracted; manually compare beginning/end and representative middle paragraphs with original SEC filing'
                if (path.name == 'WMT_000010416916000079_10K.html'
                        and start == '7' and 'incorporated by reference' in section.lower()
                        and 'Exhibit 13' in section):
                    row['Status'] = 'INCORPORATED_BY_REFERENCE'
                    row['Note'] = 'Item 7 references Annual Report to Shareholders in Exhibit 13; this HTML contains the reference, not full MD&A. Obtain Exhibit 13 for full content.'
                if not __import__('re').match(rf'(?i)^item\s+{start}\b', section.lstrip()):
                    row['Status'] = 'FAIL'
                    row['Note'] = 'Unexpected starting heading'
            except ValueError as exc:
                row['Status'] = 'REVIEW'
                row['Note'] = str(exc)
                if (path.name == 'WMT_000010416916000079_10K.html' and start == '7'):
                    import re
                    matches = list(re.finditer(r'(?im)^ITEM 7\.\nMANAGEMENT.S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS\n', text))
                    boundaries = list(re.finditer(r'(?im)^ITEM 7A\.\nQUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK\n', text))
                    if len(matches) == 1 and len(boundaries) == 1 and boundaries[0].start() > matches[0].start():
                        section = text[matches[0].start():boundaries[0].start()].strip()
                        if 'incorporated by reference' in section.lower() and 'Exhibit 13' in section:
                            row['Characters'] = len(section)
                            row['Opening'] = section[:220].replace('\n', ' ')
                            row['Ending'] = section[-220:].replace('\n', ' ')
                            row['Status'] = 'INCORPORATED_BY_REFERENCE'
                            row['Note'] = 'Item 7 references Annual Report to Shareholders in Exhibit 13; HTML contains the reference, not full MD&A.'
                # Document-specific historical exceptions, verified against
                # the supplied original SEC 10-K HTML. Never generalize by year.
                accession = path.name
                if (accession == 'NVDA_000104581005000008_10K.html'
                        and start == '1A' and not starts and not ends):
                    row['Status'] = 'NOT_APPLICABLE'
                    row['Note'] = 'FY2005 filing has no standalone Item 1A / Item 1B; risk discussion appears within Item 7 (Business Risks).'

            except Exception as exc:
                row['Status'] = 'ERROR'
                row['Note'] = f'{type(exc).__name__}: {exc}'
            rows.append(row)
path = out / 'filing_extraction_review.csv'
with path.open('w', newline='', encoding='utf-8-sig') as file:
    writer = csv.DictWriter(file, fieldnames=['Ticker','File','Section','Status','Characters','StartCandidates','EndCandidates','Opening','Ending','Note'])
    writer.writeheader()
    writer.writerows(rows)
from collections import Counter
print('RESULTS:', dict(Counter(row['Status'] for row in rows)))
print('Saved:', path)
print('REVIEW is intentional: structural extraction is not proof of fidelity to the original filing.')
