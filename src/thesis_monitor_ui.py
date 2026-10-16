"""Create and monitor evidence-linked investment theses without paid API calls."""
from uuid import uuid4
from urllib.parse import urlparse
import streamlit as st
from src.thesis_models import InvestmentThesis, ThesisEvidence, ThesisHypothesis
from src.thesis_storage import load_theses, save_thesis
from src.thesis_integration import monitor_company_theses


def render_thesis_monitoring(ticker, financial_changes):
    ticker = ticker.strip().upper()
    st.markdown('#### Investment Thesis Workspace')
    st.caption('Research hypotheses are user-authored, not verified investment conclusions. Monitoring uses existing rule-based SEC financial signals.')
    try:
        theses = load_theses(ticker)
    except (ValueError, OSError, TypeError) as exc:
        st.error(f'Unable to load saved theses: {exc}')
        return
    a, b, c = st.columns(3)
    a.metric('Saved theses', len(theses))
    b.metric('Bull hypotheses', sum(t.thesis_type == 'Bull' for t in theses))
    c.metric('Bear hypotheses', sum(t.thesis_type == 'Bear' for t in theses))

    with st.expander('＋ Create a new investment thesis', expanded=not bool(theses)):
        with st.form(f'create_thesis_{ticker}', clear_on_submit=True):
            kind = st.selectbox('Thesis direction', ['Bull', 'Bear'])
            statement = st.text_area('Investment thesis statement *', placeholder='Write a specific, falsifiable research hypothesis.', max_chars=3000)
            hypothesis = st.text_area('Key assumption *', placeholder='What would need to remain true for this thesis to hold?', max_chars=3000)
            st.caption('Optional source evidence. Do not mark an unreviewed source as Verified.')
            evidence_description = st.text_area('Evidence description', max_chars=3000)
            evidence_url = st.text_input('Evidence source URL (optional)', placeholder='https://www.sec.gov/...')
            citation = st.text_input('Evidence citation (optional)', placeholder='10-K Item 7, FY2025')
            submitted = st.form_submit_button('Save thesis', type='primary', use_container_width=True)
        if submitted:
            if not statement.strip() or not hypothesis.strip():
                st.error('A thesis statement and key assumption are required.')
            elif evidence_url.strip() and urlparse(evidence_url.strip()).scheme not in ('https', 'http'):
                st.error('Use a full http(s) source URL.')
            elif evidence_url.strip() and not evidence_description.strip():
                st.error('Describe the evidence when including a source URL.')
            else:
                evidence = []
                if evidence_description.strip():
                    evidence.append(ThesisEvidence(
                        description=evidence_description.strip(),
                        source_url=evidence_url.strip(),
                        status='Unverified', source_type='SEC' if (urlparse(evidence_url.strip()).hostname or '').lower() in {'sec.gov', 'www.sec.gov'} else 'Other',
                        citation=citation.strip(),
                    ))
                thesis = InvestmentThesis(
                    thesis_id=f'{ticker}-{uuid4().hex[:12]}', ticker=ticker,
                    thesis_type=kind, statement=statement.strip(),
                    evidence=evidence,
                    hypotheses=[ThesisHypothesis(description=hypothesis.strip(), status='Unverified')],
                    requires_human_review=True,
                )
                try:
                    save_thesis(thesis)  # Existing project validation remains authoritative.
                except (ValueError, TypeError, OSError) as exc:
                    st.error(f'Thesis not saved: {exc}')
                else:
                    st.success('Thesis saved. Research Brief and Investment Memo will use the saved thesis on their next render.')
                    st.rerun()

    if not theses:
        st.info(f'No saved investment theses for {ticker}. Use the form above to create the first one.')
        return
    try:
        results = monitor_company_theses(ticker=ticker, theses=theses, financial_changes=financial_changes)
        result_map = {result.thesis_id: result for result in results}
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        st.warning(f'Monitoring is temporarily unavailable: {exc}. Saved thesis records are shown below.')
        result_map = {}
    st.markdown('#### Saved investment theses')
    for thesis in theses:
        with st.container(border=True):
            st.markdown(f'**{thesis.thesis_type} thesis** · {thesis.statement}')
            result = result_map.get(thesis.thesis_id)
            if result:
                left, right = st.columns(2)
                left.metric('Latest financial signal', str(result.financial_signal))
                right.metric('Monitoring impact', str(result.impact))
                st.write(result.explanation)
            else:
                st.caption('No rule-based monitoring result available yet.')
            with st.expander('Assumptions and supporting evidence'):
                for item in thesis.hypotheses:
                    st.write(f'**Assumption · {item.status}:** {item.description}')
                if not thesis.evidence:
                    st.caption('No supporting evidence attached yet; human review required.')
                for item in thesis.evidence:
                    st.write(f'**Evidence · {item.status}:** {item.description}')
                    if item.citation:
                        st.caption(f'Citation: {item.citation}')
                    if item.source_url:
                        st.caption(f'Source: {item.source_url}')
            st.caption('Human review required · Not investment advice.')
