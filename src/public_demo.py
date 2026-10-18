"""Explicit opt-in public mode; no private data is read in this mode."""
import os
from pathlib import Path


def enabled():
    return os.environ.get("EI_PUBLIC_DEMO", "").strip() == "1"


def filing_root():
    if not enabled():
        return Path("data/filings")
    import tempfile
    import uuid
    import shutil
    import streamlit as st
    key = "_ei_public_filing_root"
    if key not in st.session_state:
        root = Path(tempfile.gettempdir()) / "ei_public_sessions" / uuid.uuid4().hex / "filings"
        root.mkdir(parents=True, exist_ok=True)
        public_nvda = Path(__file__).resolve().parents[1] / "demo_data" / "filings" / "NVDA"
        if public_nvda.is_dir():
            shutil.copytree(public_nvda, root / "NVDA", dirs_exist_ok=True)
        st.session_state[key] = str(root)
    return Path(st.session_state[key])


def require_private_feature(feature):
    if enabled():
        raise RuntimeError(f"{feature} is disabled in the free public demo.")
