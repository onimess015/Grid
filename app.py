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

# INTERACTIVE EXPLANATION BAR & COMPREHENSIVE GUIDE
with st.expander("📘 **CLICK HERE: How GridSelect Works, Why It Gives You an Edge & How to Use It**", expanded=False):
    tab_edge, tab_sections, tab_how_to = st.tabs([
        "💡 Why This Project & The Edge",
        "🧭 How Each Section Helps",
        "🚀 Simple How-to-Use Guide"
    ])

    with tab_edge:
        st.markdown("### 💡 **Why GridSelect Matters & What Problems It Solves**")
        st.markdown(
            """
            In real power infrastructure projects (factories, substations, data centres), **procurement is not just about buying the cheapest item**. 
            GridSelect is built to solve 3 real-world industrial problems:

            1. **The 'Cheapest Trap' Problem:**
               - **Problem:** Often, procurement teams buy the lowest-priced quote (e.g. Supplier B) to save money. But Supplier B might have quoted an **undersized 1000 kVA transformer** instead of the required **1250 kVA**, leading to dangerous overloading, equipment failure, and massive plant downtime.
               - **How GridSelect Solves It:** It automatically checks technical compliance in Step 5 before comparing prices in Step 6. Mismatched suppliers are flagged and cannot win the recommendation.

            2. **The Engineering vs Commercial Communication Gap:**
               - **Problem:** Electrical engineers speak in voltages, kVA, and protection relays, while procurement managers speak in budgets, payment terms, and delivery timelines.
               - **How GridSelect Solves It:** It unites technical specifications and commercial scores into **one transparent, 5-factor scoring model**.

            3. **The 'Black Box' AI Mistrust Problem:**
               - **Problem:** Critical infrastructure decisions cannot be made by opaque AI or hidden algorithms. Auditors and project owners require clear formulas.
               - **How GridSelect Solves It:** 100% deterministic, rule-based formulas where every point is explainable.

            ---
            #### 🌟 **How This Project Gives You an Edge in Interviews & Industry:**
            - **Connects Two Worlds:** Shows you understand both electrical hardware (Transformers, Panels, ACB, VCB, Cables, CT/PT) and commercial procurement strategy (RFQs, TBE, CBE, Negotiation).
            - **Demonstrates Sound Judgment:** Proves you know why **Lowest Quoted Price $\\neq$ Best Procurement Decision**.
            - **Executive-Ready:** Produces instant, professional RFQ documents and decision audit reports in Markdown.
            """
        )

    with tab_sections:
        st.markdown("### 🧭 **Section-by-Section: What Each Step Does & Why It Helps**")
        st.markdown(
            """
            | Step | Section Name | What Happens in Simple Words | Why It Helps the Project |
            | :--- | :--- | :--- | :--- |
            | **01** | **Project Requirement** | Enter facility load (kW), voltage (11 kV), budget, and target delivery weeks. | Establishes the project baseline and prevents missing critical engineering parameters. |
            | **02** | **Equipment Requirement** | Automatically converts project needs into structured line items (`EQ-001`, `EQ-002`, ...) with engineering definitions. | Organizes electrical packages into a traceable schedule with completeness verification. |
            | **03** | **RFQ Generator** | Packages all equipment requirements and commercial conditions into a formal quotation request (`RFQ-2026-001`). | Ensures all competing suppliers bid on the exact same technical scope and payment terms. |
            | **04** | **Supplier Quotations** | Ingests vendor bids with prices, delivery weeks, quality ratings, and offered specs. | Consolidates all supplier offers in one place for side-by-side analysis. |
            | **05** | **Technical Evaluation (TBE)** | Compares offered capacity and voltages against the RFQ. Flags **Supplier B (1000 kVA)** with a ⚠️ Mismatch. | Prevents buying non-compliant hardware while keeping data visible for audit integrity. |
            | **06** | **Commercial Evaluation (CBE)** | Uses 5 weighted sliders (Price, Tech, Delivery, Quality, Warranty) and Plotly radar charts. | Clearly separates the **Cheapest Bid** from the **Best Overall Value**. |
            | **07** | **Negotiation Simulator** | Apply a 5% discount to Supplier A (₹42L $\\rightarrow$ ₹39.9L, Saving ₹2.1L) and watch rankings re-calculate. | Tests commercial counter-offers and quantifies financial savings without corrupting original quotes. |
            | **08** | **Final Recommendation** | Generates an executive award card with dynamic justifications, total project savings, and downloadable report. | Delivers a boardroom-ready procurement recommendation report backed by transparent math. |
            """
        )

    with tab_how_to:
        st.markdown("### 🚀 **Quick Start: How to Run the 2-Minute Demo**")
        st.markdown(
            """
            Follow these 4 simple steps to experience the complete workflow:

            1. **Step 1:** Click **Start New Project** below $\\rightarrow$ Keep default values (ABC Plant, 2000 kW) $\\rightarrow$ Click **Save Project Requirement** $\\rightarrow$ Proceed.
            2. **Steps 2 & 3:** Review the equipment list and RFQ preview $\\rightarrow$ Proceed to **Supplier Quotations**.
            3. **Steps 4 & 5:** Click **Load Pre-Configured Demo Suppliers** $\\rightarrow$ Go to **Technical Evaluation** to see why Supplier B is flagged with ⚠️ Mismatch.
            4. **Steps 6 to 8:** View Commercial Evaluation $\\rightarrow$ Run a **5% negotiation on Supplier A** in Step 7 $\\rightarrow$ View the Final Recommendation card and download the full report in Step 8!
            """
        )

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)


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
