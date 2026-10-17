"""Five-stage offline deep-thesis research UI; explicit user-triggered execution only."""
import streamlit as st
from src.ai_mock_provider import MockResearchProvider
from src.ai_research_engine import prepare_evidence, validate_result
from src.ai_filing_evidence import retrieve_filing_candidates
from src.ai_deep_thesis import decompose_thesis, map_candidates


def render_ai_research(profile, theses):
    ticker = profile.identity.ticker.strip().upper()
    st.subheader('AI Deep Thesis Analysis')
    st.caption('Deterministic offline research scaffolding only. No LLM inference, API key access, network download, or paid AI call.')
    by_id = {t.thesis_id: t for t in theses if t.ticker.strip().upper() == ticker}
    if not by_id:
        st.info('Create a thesis in Thesis Tracker to try the offline research workflow.'); return
    selected = st.selectbox('Select saved thesis', list(by_id),
                            format_func=lambda x: f'{x} · {by_id[x].statement[:75]}', key=f'ai_select_{ticker}')
    thesis = by_id[selected]
    with st.container(border=True):
        st.caption('USER THESIS')
        st.markdown('**' + thesis.statement + '**')
    st.caption(f'{thesis.thesis_type} · Thesis ID: {thesis.thesis_id}')
    key = f'ai_mock_result_{ticker}'
    if st.button('Run Free Mock Analysis', key=f'ai_run_{ticker}', type='primary'):
        try:
            with st.status("Running offline mock analysis...", expanded=True) as status:
                st.write("Step 1/3: Preparing financial evidence...")
                inventory = prepare_evidence(profile, thesis)

                st.write("Step 2/3: Retrieving local SEC filing candidates...")
                passages, notices = retrieve_filing_candidates(profile, thesis)
                inventory.extend(passages)

                st.write("Step 3/3: Validating mock research result...")
                result = validate_result(
                    MockResearchProvider().analyze(thesis, inventory),
                    thesis,
                    inventory
                )

                st.session_state[key] = (selected, result, inventory, notices)
                status.update(label="Offline analysis completed", state="complete")

        except Exception as exc:
            st.error(f"Offline analysis failed: {type(exc).__name__}: {exc}")
            st.exception(exc)
            st.stop()
    saved = st.session_state.get(key)
    if not saved or saved[0] != selected:
        st.info('Click Run Free Mock Analysis. No analysis runs on page refresh.'); return
    _, result, inventory, notices = saved
    hypotheses = decompose_thesis(thesis)
    st.warning(f'{result.provider} · {result.overall_assessment} · Human review required')
    c1, c2, c3 = st.columns(3)
    c1.metric('Hypotheses', len(decompose_thesis(thesis)))
    c2.metric('SEC passage candidates', sum(e.evidence_id.startswith('PASSAGE-') for e in inventory))
    c3.metric('Verified thesis evidence', '0 · Offline')
    st.markdown('#### 1. Thesis Decomposition')
    st.caption('User-saved hypotheses, or the original statement as fallback; no AI-generated claims.')
    for i, hypothesis in enumerate(hypotheses, 1): st.write(f'H{i}. {hypothesis}')
    st.markdown('#### 2. SEC Evidence Retrieval')
    st.caption('FIN = consolidated context; FILING = metadata; PASSAGE = ranked candidate text, NOT established thesis evidence.')
    for notice in notices: st.info(notice)
    for hypothesis, ids in map_candidates(hypotheses, inventory):
        st.markdown(f'**Candidate mapping for: {hypothesis}**')
        st.caption(', '.join(ids) if ids else 'No directly matching passage candidate found.')
    st.caption('Source inventory is collapsed by default. Open a candidate to inspect its excerpt and SEC link.')
    for e in inventory:
        with st.expander(f'{e.evidence_id} · {e.category}'):
            st.write(e.description)
            st.caption(e.citation)
            st.link_button('Open SEC source', e.source_url)
    st.markdown('#### 3. Supporting vs. Contradicting Evidence')
    a,b = st.columns(2)
    with a: st.markdown('**Verified Supporting Evidence**'); st.write('None established by offline mock.')
    with b: st.markdown('**Verified Contradicting Evidence**'); st.write('None established by offline mock.')
    st.caption('Potential risk-context is a retrieval hint, never a verified contradiction.')
    st.markdown('#### 4. Research Gap Identification')
    for gap in result.research_gaps: st.write('- ' + gap)
    st.markdown('**Monitoring indicators**')
    for item in result.monitoring_indicators: st.write('- ' + item)
    st.markdown('#### 5. Evidence-linked Assessment')
    for h in result.hypotheses:
        st.markdown(f'**{h.hypothesis} — {h.assessment}**')
        st.write(h.explanation)
        if h.evidence_ids: st.caption('Context only, not proof: ' + ', '.join(h.evidence_ids))
    st.caption(result.limitations + ' Session-only result; included in Brief/PDF for this thesis while session remains active.')
