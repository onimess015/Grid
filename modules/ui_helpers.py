"""
ui_helpers.py
Provides shared UI styling, sidebar workflow navigation, session state initialization,
page guard checks, and confirmation dialogs for GridSelect.
"""

import streamlit as st
from typing import Optional

# Global Educational Disclaimer text
GLOBAL_DISCLAIMER = (
    "Educational prototype only. Equipment selection, technical specifications, "
    "procurement decisions and electrical designs for real installations require "
    "qualified engineering review, applicable standards and project-specific validation. "
    "Supplier and pricing data in this prototype are hypothetical."
)

DEMO_DATA_LABEL = "Demo data — hypothetical values for educational illustration only."

CUSTOM_CSS = """
<style>
/* GridSelect Industrial Dark Theme */
:root {
    --primary-color: #5FA8D3;
    --secondary-color: #1B4965;
    --accent-color: #62B6CB;
    --success-color: #4ADE80;
    --warning-color: #FACC15;
    --danger-color: #F87171;
    --bg-color: #0D1117;
    --card-bg: #161B22;
    --border-color: #30363D;
    --text-color: #E6EDF3;
    --text-muted: #8B949E;
}

/* Page Header */
.gridselect-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    padding: 1.5rem 2rem;
    border-radius: 10px;
    color: #FFFFFF;
    margin-bottom: 1.5rem;
    border: 1px solid #334155;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}
.gridselect-header h1 {
    color: #F0F6FC !important;
    margin: 0;
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.gridselect-header p {
    color: #94A3B8;
    margin: 0.35rem 0 0 0;
    font-size: 0.95rem;
}

/* Cards */
.gs-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    color: #E6EDF3;
}

.gs-card-highlight {
    background: #1C2128;
    border-left: 4px solid #5FA8D3;
    border-radius: 4px 8px 8px 4px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    color: #E6EDF3;
}

/* Workflow Step Box */
.step-box {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    height: 100%;
}
.step-box:hover {
    border-color: #5FA8D3;
    box-shadow: 0 4px 12px rgba(95, 168, 211, 0.15);
}
.step-number {
    font-size: 0.75rem;
    font-weight: 700;
    color: #5FA8D3;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.step-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #F0F6FC;
    margin: 0.25rem 0;
}
.step-desc {
    font-size: 0.8rem;
    color: #8B949E;
}

/* Badges */
.badge-success {
    background-color: rgba(46, 125, 50, 0.25);
    color: #4ADE80;
    border: 1px solid rgba(74, 222, 128, 0.35);
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}
.badge-warning {
    background-color: rgba(249, 168, 37, 0.2);
    color: #FACC15;
    border: 1px solid rgba(250, 204, 21, 0.35);
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}
.badge-danger {
    background-color: rgba(198, 40, 40, 0.25);
    color: #F87171;
    border: 1px solid rgba(248, 113, 113, 0.35);
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}
.badge-neutral {
    background-color: #21262D;
    color: #8B949E;
    border: 1px solid #30363D;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}

/* Small notice tag */
.demo-tag {
    font-size: 0.75rem;
    color: #8B949E;
    background: #21262D;
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
    border-left: 3px solid #5FA8D3;
}
</style>
"""


def init_session_state():
    """Initializes all global session state keys if not already present."""
    default_state = {
        "project_details": {},
        "equipment_requirements": [],
        "rfq_details": {},
        "supplier_quotes": {},
        "technical_scores": {},
        "commercial_scores": {},
        "negotiation_results": {},
        "final_recommendation": {},
        "rfq_sequence": 1,
        "show_reset_confirm": False
    }

    for key, val in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_project_status() -> str:
    """Computes overall project workflow status."""
    if st.session_state.get("final_recommendation"):
        return "Completed"
    elif st.session_state.get("commercial_scores"):
        return "Evaluation"
    elif st.session_state.get("project_details"):
        return "In Progress"
    return "Not Started"


def render_sidebar():
    """Renders standardized sidebar navigation, status, reset workflow, and disclaimer."""
    init_session_state()
    st.sidebar.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⚡ **GridSelect**")
        st.caption("Power Systems Decision Platform")

        st.markdown("---")

        # Project Status Indicator
        status = get_project_status()
        status_badges = {
            "Not Started": '<span class="badge-neutral">⚪ Not Started</span>',
            "In Progress": '<span class="badge-warning">🟡 In Progress</span>',
            "Evaluation": '<span class="badge-warning">🟠 Evaluation</span>',
            "Completed": '<span class="badge-success">🟢 Completed</span>'
        }
        st.markdown(f"**Project Status:** {status_badges.get(status, status)}", unsafe_allow_html=True)

        if st.session_state.project_details.get("project_name"):
            st.caption(f"📌 **{st.session_state.project_details['project_name']}**")

        st.markdown("---")
        st.markdown("##### **Workflow Navigation**")
        st.caption("01. Project Requirement")
        st.caption("02. Equipment Requirement")
        st.caption("03. RFQ Generator")
        st.caption("04. Supplier Quotations")
        st.caption("05. Technical Evaluation")
        st.caption("06. Commercial Evaluation")
        st.caption("07. Negotiation")
        st.caption("08. Final Recommendation")

        st.markdown("---")

        # Reset Workflow with Safe Confirmation
        if not st.session_state.get("show_reset_confirm", False):
            if st.button("🔄 Reset Project", use_container_width=True, help="Clear all project state"):
                st.session_state.show_reset_confirm = True
                st.rerun()
        else:
            st.warning("⚠️ Are you sure? This will clear all project and quotation data.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Confirm Reset", use_container_width=True, type="primary"):
                    st.session_state.project_details = {}
                    st.session_state.equipment_requirements = []
                    st.session_state.rfq_details = {}
                    st.session_state.supplier_quotes = {}
                    st.session_state.technical_scores = {}
                    st.session_state.commercial_scores = {}
                    st.session_state.negotiation_results = {}
                    st.session_state.final_recommendation = {}
                    st.session_state.show_reset_confirm = False
                    st.toast("Project reset successfully.")
                    st.rerun()
            with col_no:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_reset_confirm = False
                    st.rerun()

        st.markdown("---")
        st.markdown(f"<div class='demo-tag'>{DEMO_DATA_LABEL}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:0.7rem; color:#888; line-height:1.3; margin-top:8px;'>{GLOBAL_DISCLAIMER}</div>",
            unsafe_allow_html=True
        )


def check_page_guard(required_key: str, redirect_page: str, step_name: str) -> bool:
    """
    Ensures previous required steps are completed before allowing user to view the current page.
    Returns True if guard passes, False if guarded and rendered redirection alert.
    """
    has_data = False
    val = st.session_state.get(required_key)
    if isinstance(val, (dict, list)):
        has_data = len(val) > 0
    elif val is not None:
        has_data = bool(val)

    if not has_data:
        st.warning(f"⚠️ Complete the **{step_name}** step first.")
        if st.button(f"➡️ Go to {step_name}", type="primary"):
            st.switch_page(redirect_page)
        return False
    return True


def render_page_header(title: str, subtitle: str):
    """Renders a uniform styled top header."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="gridselect-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
