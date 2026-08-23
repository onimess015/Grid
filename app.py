"""
app.py
Main entry point for GridSelect: Power Systems Equipment & Procurement Decision Platform.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.ui_helpers import (
    render_sidebar,
    render_page_header,
    init_session_state,
    get_project_status
)

st.set_page_config(
    page_title="GridSelect — Power Systems Procurement Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State & Sidebar
init_session_state()
render_sidebar()

# Main Page Header
render_page_header(
    title="⚡ GridSelect",
    subtitle="Power Systems Equipment & Procurement Decision Platform"
)

st.markdown(
    """
    > **GridSelect** is an educational decision-support prototype that demonstrates how an electrical procurement engineer 
    > can move from project requirements to equipment identification, supplier evaluation, commercial comparison, 
    > negotiation and final procurement recommendation.
    """
)

# 4 Key Dashboard Metrics
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

# Project Status
proj_status = get_project_status()
with col_m1:
    st.metric(
        label="Project Status",
        value=proj_status if proj_status != "Not Started" else "Not Started"
    )

# Equipment Items Count
eq_count = len(st.session_state.get("equipment_requirements", []))
with col_m2:
    st.metric(
        label="Equipment Items",
        value=f"{eq_count} Items" if eq_count > 0 else "—"
    )

# Suppliers Count
suppliers_dict = st.session_state.get("supplier_quotes", {})
total_suppliers = 0
if isinstance(suppliers_dict, dict):
    all_sups = set()
    for eq, quotes in suppliers_dict.items():
        for q in quotes:
            all_sups.add(q.get("supplier_name"))
    total_suppliers = len(all_sups)
with col_m3:
    st.metric(
        label="Evaluated Suppliers",
        value=f"{total_suppliers} Suppliers" if total_suppliers > 0 else "—"
    )

# Potential Savings
neg_res = st.session_state.get("negotiation_results", {})
total_savings = 0.0
if isinstance(neg_res, dict):
    for eq_type, res in neg_res.items():
        total_savings += float(res.get("savings", 0.0))
with col_m4:
    st.metric(
        label="Potential Savings",
        value=f"₹{total_savings:.2f} lakh" if total_savings > 0 else "—"
    )

st.markdown("---")

# Visual Workflow Grid
st.markdown("### 📋 **Techno-Commercial Procurement Workflow**")
st.caption("A structured 8-step decision process linking electrical engineering specifications with commercial bid analysis.")

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

with row1_col1:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 01</div>
            <div class="step-title">Project Requirement</div>
            <div class="step-desc">Define plant load, system voltage, feeders, and stated priorities.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row1_col2:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 02</div>
            <div class="step-title">Equipment Requirement</div>
            <div class="step-desc">Structure transformer, switchgear panels, circuit breakers, and cables.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row1_col3:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 03</div>
            <div class="step-title">RFQ Generator</div>
            <div class="step-desc">Compile formal technical specs and commercial conditions into an RFQ document.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row1_col4:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 04</div>
            <div class="step-title">Supplier Quotations</div>
            <div class="step-desc">Ingest vendor bids (prices, delivery, warranties, offered specs).</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

with row2_col1:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 05</div>
            <div class="step-title">Technical Evaluation</div>
            <div class="step-desc">Verify rating & voltage compliance; flag technical mismatches.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row2_col2:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 06</div>
            <div class="step-title">Commercial Evaluation</div>
            <div class="step-desc">Multi-criteria weighted scoring (Price, Delivery, Quality, Warranty).</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row2_col3:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 07</div>
            <div class="step-title">Negotiation</div>
            <div class="step-desc">Simulate vendor price discounts and track ranking movements.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row2_col4:
    st.markdown(
        """
        <div class="step-box">
            <div class="step-number">STEP 08</div>
            <div class="step-title">Final Recommendation</div>
            <div class="step-desc">Transparent executive decision summary and exportable procurement report.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Call to Action
st.markdown("### 🚀 **Get Started**")
if not st.session_state.get("project_details"):
    st.info("💡 **Start by defining your project requirement.**")
    if st.button("🚀 Start New Project", type="primary", use_container_width=False):
        st.switch_page("pages/01_Project_Requirement.py")
else:
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("➡️ Continue Project", type="primary", use_container_width=True):
            st.switch_page("pages/01_Project_Requirement.py")
    with col_btn2:
        st.success(f"Project **{st.session_state.project_details.get('project_name', '')}** is active.")
