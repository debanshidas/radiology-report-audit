"""
utils/styles.py
---------------
CSS injection for custom HTML components only.
Does NOT override Streamlit's native buttons, inputs, or layout elements.
Base theme is handled via .streamlit/config.toml
"""
import streamlit as st


def inject_css():
    """Injects only custom component CSS — safe, does not break native Streamlit UI."""
    st.markdown("""<style>

/* ── FONTS ───────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── SIDEBAR DARK THEME ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1a2744 100%) !important;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] strong {
    color: #38bdf8 !important;
}

/* ── PAGE HEADER BANNER ──────────────────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, #0f172a 0%, #0c4a6e 100%);
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 20px rgba(15,23,42,0.15);
}
.page-header-icon { font-size: 2.5rem; line-height: 1; }
.page-header-text h1 {
    font-size: 1.6rem;
    font-weight: 800;
    color: #f8fafc !important;
    margin: 0 0 0.2rem 0;
    padding: 0;
}
.page-header-text p {
    font-size: 0.9rem;
    color: #94a3b8 !important;
    margin: 0;
}

/* ── STAT CARDS ──────────────────────────────────────────────────────── */
.stat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.stat-card-accent {
    position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 14px 0 0 14px;
}
.stat-card-icon { font-size: 1.8rem; margin-bottom: 0.6rem; }
.stat-card-value { font-size: 2rem; font-weight: 800; color: #0f172a; line-height: 1; margin-bottom: 0.2rem; }
.stat-card-label { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #64748b; }
.stat-card-sublabel { font-size: 0.76rem; color: #94a3b8; margin-top: 0.3rem; }

/* ── FEATURE CARDS ───────────────────────────────────────────────────── */
.feature-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
    height: 100%;
}
.feature-card:hover {
    border-color: #0d9488;
    box-shadow: 0 6px 20px rgba(13,148,136,0.1);
    transform: translateY(-2px);
}
.feature-card-icon { font-size: 1.8rem; margin-bottom: 0.75rem; }
.feature-card h3 { font-size: 0.95rem !important; font-weight: 700 !important; color: #0f172a !important; margin-bottom: 0.4rem !important; }
.feature-card p { font-size: 0.85rem; color: #64748b; line-height: 1.6; margin: 0; }

/* ── SCORE GAUGE ─────────────────────────────────────────────────────── */
.score-wrapper {
    background: #ffffff;
    border-radius: 18px;
    padding: 1.75rem;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.score-label {
    font-size: 0.9rem; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
    margin-top: 0.75rem;
}
.score-justification {
    font-size: 0.85rem; color: #475569;
    margin-top: 0.6rem; line-height: 1.6;
    max-width: 280px; margin-left: auto; margin-right: auto;
}

/* ── READINESS BADGES ────────────────────────────────────────────────── */
.readiness-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.55rem 1.2rem; border-radius: 50px;
    font-weight: 700; font-size: 0.9rem;
}
.readiness-ready  { background: #d1fae5; color: #065f46; border: 1.5px solid #6ee7b7; }
.readiness-minor  { background: #fef3c7; color: #92400e; border: 1.5px solid #fcd34d; }
.readiness-major  { background: #fee2e2; color: #991b1b; border: 1.5px solid #fca5a5; }

/* ── QUALITY BREAKDOWN BARS ──────────────────────────────────────────── */
.breakdown-row { margin-bottom: 1rem; }
.breakdown-label {
    display: flex; justify-content: space-between;
    margin-bottom: 0.3rem; font-size: 0.86rem; font-weight: 600; color: #334155;
}
.breakdown-bar-bg { background: #e2e8f0; border-radius: 50px; height: 9px; overflow: hidden; }
.breakdown-bar-fill { height: 100%; border-radius: 50px; }

/* ── SECTION CHECKLIST ───────────────────────────────────────────────── */
.checklist-item {
    display: flex; align-items: flex-start;
    padding: 0.85rem 1rem; background: #ffffff;
    border-radius: 10px; border: 1px solid #e2e8f0;
    margin-bottom: 0.5rem; gap: 0.75rem;
}
.checklist-dot {
    width: 22px; height: 22px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; flex-shrink: 0; margin-top: 1px;
}
.dot-present { background: #d1fae5; color: #065f46; }
.dot-missing  { background: #fee2e2; color: #991b1b; }
.checklist-name { font-weight: 600; font-size: 0.88rem; color: #1e293b; }
.checklist-detail { font-size: 0.78rem; color: #64748b; margin-top: 0.1rem; line-height: 1.4; }

/* ── SUGGESTION CARDS ────────────────────────────────────────────────── */
.suggestion-card {
    border-left: 4px solid; border-radius: 0 10px 10px 0;
    padding: 0.9rem 1.1rem; margin-bottom: 0.65rem;
    transition: transform 0.15s ease;
}
.suggestion-card:hover { transform: translateX(3px); }
.suggestion-card-title {
    font-weight: 700; font-size: 0.75rem;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem;
}
.suggestion-card-text { font-size: 0.88rem; line-height: 1.55; color: #334155; }
.sug-missing     { border-color: #ef4444; background: #fff5f5; }
.sug-missing .suggestion-card-title { color: #b91c1c; }
.sug-template    { border-color: #3b82f6; background: #eff6ff; }
.sug-template .suggestion-card-title { color: #1d4ed8; }
.sug-terminology { border-color: #8b5cf6; background: #f5f3ff; }
.sug-terminology .suggestion-card-title { color: #6d28d9; }
.sug-formatting  { border-color: #0d9488; background: #f0fdfa; }
.sug-formatting .suggestion-card-title { color: #0f766e; }
.sug-impression  { border-color: #f59e0b; background: #fffbeb; }
.sug-impression .suggestion-card-title { color: #b45309; }
.sug-remarks     { border-color: #64748b; background: #f8fafc; }
.sug-remarks .suggestion-card-title { color: #475569; }

/* ── STRENGTHS ───────────────────────────────────────────────────────── */
.strength-card {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 1px solid #bbf7d0; border-radius: 10px;
    padding: 0.8rem 1rem; margin-bottom: 0.5rem;
    display: flex; align-items: flex-start; gap: 0.5rem;
    font-size: 0.88rem; color: #166534; line-height: 1.5;
}
.strength-icon { flex-shrink: 0; }

/* ── INFO BOX ────────────────────────────────────────────────────────── */
.info-box {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border: 1px solid #bfdbfe; border-radius: 12px;
    padding: 1.1rem 1.4rem; margin: 0.75rem 0;
}
.info-box-title { font-weight: 700; color: #1d4ed8; margin-bottom: 0.35rem; font-size: 0.88rem; }
.info-box-text  { font-size: 0.85rem; color: #1e40af; line-height: 1.6; }

/* ── WORKFLOW STEP CARDS ─────────────────────────────────────────────── */
.step-card {
    text-align: center; padding: 1.5rem 1rem;
    background: #fff; border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.step-num {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #0d9488, #0891b2);
    color: white; font-weight: 800; font-size: 1.05rem;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 0.65rem;
}
.step-title { font-weight: 700; color: #0f172a; margin-bottom: 0.35rem; font-size: 0.9rem; }
.step-desc  { font-size: 0.8rem; color: #64748b; line-height: 1.5; }

/* ── TECH BADGE ──────────────────────────────────────────────────────── */
.tech-badge {
    display: inline-block; background: #f1f5f9;
    border: 1px solid #e2e8f0; border-radius: 50px;
    padding: 0.25rem 0.8rem; font-size: 0.8rem;
    font-weight: 600; color: #475569; margin: 0.2rem;
}

</style>""", unsafe_allow_html=True)
