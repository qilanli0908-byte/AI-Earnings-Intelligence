import streamlit as st


def apply_dashboard_style():
    """Compact, restrained portfolio dashboard styling; presentation only."""
    st.markdown("""
    <style>
    :root { --ei-navy:#14263d; --ei-blue:#2563eb; --ei-border:#e2e8f0; }
    .stApp { background:#f6f8fc; color:#14263d; }
    .block-container { max-width:1460px; padding:1.65rem 2.3rem 3rem; }
    h1,h2,h3 { color:#14263d; letter-spacing:-.025em; }
    h1 { font-size:1.75rem !important; font-weight:720 !important; margin:.3rem 0 .65rem !important; }
    h2 { font-size:1.28rem !important; font-weight:690 !important; margin:1.35rem 0 .65rem !important; }
    h3 { font-size:1.05rem !important; font-weight:680 !important; margin:1rem 0 .55rem !important; }
    p,li { line-height:1.55; }
    [data-testid="stCaptionContainer"] { color:#667790; }
    hr { border-color:#e2e8f0 !important; margin:1.15rem 0 !important; }
    [data-testid="stSidebar"] { background:linear-gradient(160deg,#152a45 0%,#101f34 100%); }
    [data-testid="stSidebar"] > div { padding-top:1.1rem; }
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#e7edf8 !important; }
    .ei-brand { display:flex; align-items:center; gap:13px; margin:.4rem 0 1.75rem; }
    .ei-brand-mark { font-size:1.7rem; font-weight:800; color:#60a5fa; line-height:1; }
    .ei-brand-title { color:#fff; font-size:1.12rem; font-weight:750; letter-spacing:-.02em; }
    .ei-brand-subtitle { color:#a5b5cd; font-size:.75rem; margin-top:3px; }
    .ei-sidebar-label { color:#91a7c6; font-size:.67rem; font-weight:750; letter-spacing:.11em; margin:.9rem 0 .65rem; }
    .ei-sidebar-rule { border-top:1px solid #344862; margin:1.3rem 0; }
    .ei-ticker-status { color:#aebdd2; font-size:.79rem; margin:1rem 0; }
    .ei-ticker-status strong { color:#fff; }
    .ei-status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#10b981; margin-right:7px; }
    [data-testid="stSidebar"] [role="radiogroup"] { gap:.12rem; }
    /* Streamlit radio remains keyboard-accessible; hide its default circular artwork. */
    [data-testid="stSidebar"] [role="radiogroup"] label [data-testid="stRadio"] { display:none !important; }
    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child:has(input) { width:0 !important; min-width:0 !important; overflow:hidden !important; }
    [data-testid="stSidebar"] [role="radiogroup"] label { width:100%; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
      padding:.58rem .7rem !important; border-radius:9px; transition:background .15s;
      color:#bac9df !important; font-size:.88rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:#253d5d; }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
      background:#2b456c !important; box-shadow:inset 3px 0 #3b82f6; color:#fff !important; font-weight:650; }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color:#fff !important; }
    [data-testid="stSidebar"] [role="radiogroup"] [data-testid="stMarkdownContainer"] p { font-size:.88rem; }
    [data-testid="stSidebar"] [role="radiogroup"] [data-testid="stRadio"] { accent-color:#3b82f6; }
    [data-testid="stSidebar"] input[type="text"] { background:#fff !important; color:#17263b !important; -webkit-text-fill-color:#17263b !important; border-radius:9px; }
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button { background:#2563eb !important; border:1px solid #2563eb !important; color:#fff !important; font-weight:650; border-radius:9px; }
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button * { color:#fff !important; }
    [data-testid="stSidebar"] [data-testid="stButton"] button { background:#263e5d !important; border:1px solid #355070 !important; color:#fff !important; border-radius:9px; font-weight:650; }
    [data-testid="stSidebar"] [data-testid="stButton"] button * { color:#fff !important; }
    [data-testid="stSidebar"] [data-testid="stButton"] button:hover { background:#34547b !important; }
    [data-testid="stMetric"] { background:#fff; border:1px solid var(--ei-border); border-radius:12px; padding:15px 18px; box-shadow:0 3px 12px rgba(18,39,66,.035); min-width:0; }
    [data-testid="stMetricLabel"] p { font-size:.77rem !important; color:#64748b !important; }
    [data-testid="stMetricValue"] { font-size:1.35rem !important; font-weight:720 !important; color:#14263d !important; overflow-wrap:anywhere; }
    [data-testid="stMetricValue"] > div { font-size:inherit !important; }
    [data-testid="stMetricValue"],[data-testid="stMetricValue"] * {
      white-space:normal !important; text-overflow:clip !important;
      overflow:visible !important; line-height:1.28 !important;
    }
    [data-testid="stMetric"] { min-height:92px; }
    [data-testid="stMetricLabel"] p { font-size:.81rem !important; }
    /* Prevent the native metric from making company names/industries enormous. */
    [data-testid="stMetricValue"] { font-size:1.2rem !important; }
    [data-testid="stMetricValue"] [data-testid="stMetricValue"] { font-size:inherit !important; }
    .ei-section-title { font-size:1.05rem; font-weight:700; color:#14263d; margin:1.15rem 0 .55rem; }
    .ei-overview-panel { background:#fff; border:1px solid #e2e8f0; border-radius:13px;
      padding:1.15rem 1.3rem; box-shadow:0 3px 12px rgba(18,39,66,.035); }
    .ei-overview-panel h3 { margin-top:0 !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { font-size:.72rem !important; }
    [data-testid="stSidebar"] .stElementContainer { margin-bottom:.12rem; }
    [data-testid="stVerticalBlockBorderWrapper"] > div { border-color:#e2e8f0; }
    [data-testid="stExpander"],[data-testid="stDataFrame"] { border:1px solid var(--ei-border); border-radius:11px; overflow:hidden; }
    .stButton > button,.stDownloadButton > button { border-radius:9px; }
    .stButton > button[kind="primary"] { background:#2563eb; color:white; border-color:#2563eb; }
    .ei-page-eyebrow { font-size:.68rem; letter-spacing:.13em; font-weight:750; color:#6680a5; margin:.15rem 0 .4rem; }
    .ei-page-subtitle { font-size:.87rem; color:#64748b; margin:-.2rem 0 1.35rem; }
    .ei-company-card { display:grid; grid-template-columns:minmax(180px,1.5fr) repeat(2,minmax(130px,1fr)); gap:0; background:#fff; border:1px solid #e2e8f0; border-radius:13px; padding:1.2rem 1.3rem; box-shadow:0 4px 18px rgba(18,39,66,.045); margin:1rem 0 1.3rem; }
    .ei-company-cell { padding:.25rem 1.1rem; min-width:0; border-right:1px solid #e2e8f0; }
    .ei-company-cell:first-child { padding-left:.3rem; }
    .ei-company-cell:last-child { border-right:0; }
    .ei-company-label { color:#64748b; font-size:.73rem; margin-bottom:.45rem; }
    .ei-company-value { color:#14263d; font-size:1rem; font-weight:680; overflow-wrap:anywhere; line-height:1.35; }
    .ei-company-ticker { color:#2563eb; font-size:.76rem; margin-top:.35rem; }
    @media(max-width:950px) { .ei-company-card { grid-template-columns:1fr; gap:.7rem; } .ei-company-cell { border-right:0; border-bottom:1px solid #e2e8f0; padding:.6rem .2rem; } .ei-company-cell:last-child { border-bottom:0; } }
    @media(max-width:768px) { .block-container { padding:1rem; } h1 { font-size:1.5rem !important; } }
    .ei-profile-identity { display:grid; grid-template-columns:minmax(230px,1.65fr) repeat(3,minmax(115px,1fr)); align-items:center; background:#fff; border:1px solid #e2e8f0; border-radius:13px; padding:1.15rem 1.25rem; gap:0; box-shadow:0 3px 14px rgba(18,39,66,.04); margin:.7rem 0 1.3rem; }
    .ei-identity-primary { padding:0 1rem 0 .2rem; min-width:0; }
    .ei-identity-kicker { font-size:.63rem; font-weight:750; letter-spacing:.11em; color:#7187a5; margin-bottom:.4rem; }
    .ei-identity-name { font-size:1.13rem; font-weight:740; line-height:1.35; color:#14263d; overflow-wrap:anywhere; }
    .ei-identity-meta { font-size:.73rem; color:#64748b; margin-top:.3rem; }
    .ei-identity-detail { padding:.2rem 1rem; border-left:1px solid #e2e8f0; min-width:0; }
    .ei-identity-detail span { display:block; font-size:.73rem; color:#64748b; margin-bottom:.42rem; }
    .ei-identity-detail strong { display:block; font-size:.9rem; font-weight:680; color:#14263d; overflow-wrap:anywhere; line-height:1.35; }
    .ei-kpi-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.75rem; margin:.5rem 0 .75rem; }
    .ei-kpi { padding:1rem 1rem .9rem; border:1px solid #e1e9f5; border-radius:11px; background:#f5f8ff; min-width:0; }
    .ei-kpi-green { background:#f1fbf6; border-color:#ddf2e6; }
    .ei-kpi-purple { background:#f7f5ff; border-color:#ebe6fa; }
    .ei-kpi-amber { background:#fff9f0; border-color:#f7ead7; }
    .ei-kpi-label { font-size:.73rem; color:#586d8c; margin-bottom:.45rem; }
    .ei-kpi-value { font-size:1.19rem; font-weight:760; color:#14263d; line-height:1.3; overflow-wrap:anywhere; }
    .ei-kpi-note { font-size:.67rem; color:#71839a; margin-top:.4rem; }
    .ei-priority-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.4rem; }
    .ei-priority-row .ei-kpi { padding:.6rem; }
    .ei-priority-row .ei-kpi-value { font-size:1.03rem; }
    .ei-priority-row .ei-kpi-note { margin-top:.1rem; }
    @media(max-width:1100px) { .ei-profile-identity { grid-template-columns:repeat(3,minmax(0,1fr)); row-gap:1rem; } .ei-identity-primary { grid-column:1/-1; } .ei-kpi-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
    @media(max-width:700px) { .ei-profile-identity { grid-template-columns:1fr; } .ei-identity-primary { grid-column:auto; } .ei-identity-detail { border-left:0; border-top:1px solid #e2e8f0; padding:.6rem .2rem; } .ei-kpi-grid { grid-template-columns:1fr 1fr; } }
    </style>
    """, unsafe_allow_html=True)


def render_dashboard_header():
    """Page-specific headings are rendered by web_app; avoid a duplicate giant title."""
    return None
