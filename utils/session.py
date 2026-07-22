"""
utils/session.py
----------------
Centralized session state management.
All audit data flows through these helpers to ensure consistency across pages.
"""

import streamlit as st
from datetime import datetime


# ── Keys ──────────────────────────────────────────────────────────────────────
KEYS = {
    "report_text":       "",        # Extracted report text
    "report_filename":   "",        # Original filename
    "report_modality":   "Chest X-Ray",
    "mandatory_sections": [],       # User-selected sections to audit
    "audit_result":      None,      # Full Gemini JSON response
    "audit_timestamp":   None,      # datetime of last audit
    "reports_analyzed":  0,         # Running count
    "reports_exported":  0,         # Running count
    "api_key":           "",        # Gemini API key for this session
}


def init_session():
    """Initialise all session state keys with defaults if not already set."""
    for key, default in KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def set_audit_result(result: dict):
    """Store audit result and update counters/timestamp."""
    st.session_state.audit_result = result
    st.session_state.audit_timestamp = datetime.now()
    st.session_state.reports_analyzed = st.session_state.get("reports_analyzed", 0) + 1


def clear_audit():
    """Reset report + audit data but keep settings."""
    st.session_state.report_text = ""
    st.session_state.report_filename = ""
    st.session_state.audit_result = None
    st.session_state.audit_timestamp = None


def has_report() -> bool:
    return bool(st.session_state.get("report_text", "").strip())


def has_audit() -> bool:
    return st.session_state.get("audit_result") is not None


def get_api_key() -> str:
    """Resolve API key: session UI → st.secrets → environment variable."""
    import os
    key = st.session_state.get("api_key", "").strip()
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")
