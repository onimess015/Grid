"""
01_Project_Requirement.py
Step 1: Capture project baseline information, electrical requirements,
equipment selections, and stated procurement priorities.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.ui_helpers import (
    render_sidebar,
    render_page_header,
    init_session_state
)
from modules.electrical_calculations import estimate_transformer_kva
from modules.equipment_logic import build_equipment_list

st.set_page_config(
    page_title="Step 1: Project Requirement — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="1. Project Requirement",
    subtitle="Define the electrical and procurement requirements for the project."
)

# Load existing values from session state if present
proj = st.session_state.get("project_details", {})

with st.form("project_requirement_form"):
    # SECTION A: Project Information
    st.markdown("### 🏢 **Section A: Project Information**")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        project_name = st.text_input(
            "Project Name *",
            value=proj.get("project_name", "ABC Manufacturing Plant"),
            help="Enter descriptive name for the installation or facility"
        )
        industry = st.selectbox(
            "Industry Sector",
            options=["Manufacturing", "Commercial Building", "Data Centre", "Infrastructure", "Process Industry", "Other"],
            index=["Manufacturing", "Commercial Building", "Data Centre", "Infrastructure", "Process Industry", "Other"].index(
                proj.get("industry", "Manufacturing")
            )
        )
    with col_a2:
        project_location = st.text_input(
            "Project Location",
            value=proj.get("project_location", "Industrial Hub, Pune")
        )
        completion_weeks = st.number_input(
            "Target Project Completion (weeks)",
            min_value=1,
            max_value=100,
            value=int(proj.get("completion_weeks", 12)),
            step=1
        )

    st.markdown("---")

    # SECTION B: Electrical Requirements
    st.markdown("### ⚡ **Section B: Electrical Baseline & Equipment Selection**")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        total_load_kw = st.slider(
            "Total Connected Load (kW) *",
            min_value=10,
            max_value=5000,
            value=int(proj.get("total_load_kw", 2000)),
            step=50,
            help="Total active electrical demand of the facility"
        )
    with col_b2:
        system_voltage = st.selectbox(
            "Incomer System Voltage *",
            options=["415 V", "690 V", "3.3 kV", "6.6 kV", "11 kV", "33 kV"],
            index=["415 V", "690 V", "3.3 kV", "6.6 kV", "11 kV", "33 kV"].index(
                proj.get("system_voltage", "11 kV")
            )
        )
    with col_b3:
        feeders_count = st.slider(
            "Number of Distribution Feeders",
            min_value=1,
            max_value=50,
            value=int(proj.get("feeders_count", 8)),
            step=1
        )

    # Equipment Category Checkboxes & Expandable Parameters
    st.markdown("#### **Required Equipment Packages**")

    # 1. Transformer
    col_t1, col_t2 = st.columns([1, 3])
    with col_t1:
        transformer_req = st.checkbox("Transformer", value=proj.get("transformer_required", True))
    with col_t2:
        if transformer_req:
            # Educational sizing hint
            hint = estimate_transformer_kva(total_load_kw, pf=0.9)
            st.caption(f"💡 *Sizing Hint (pf=0.9): Load {total_load_kw} kW / 0.9 = ~{hint['estimated_kva']} kVA. (Educational sizing hint only — not a certified engineering calculation)*")
            
            c_t_q, c_t_r, c_t_p, c_t_s = st.columns(4)
            with c_t_q:
                trans_qty = st.number_input("Transformer Qty", min_value=1, max_value=10, value=int(proj.get("transformer_qty", 2)))
            with c_t_r:
                trans_rating = st.number_input("Rating (kVA) *", min_value=100, max_value=10000, value=int(proj.get("transformer_rating_kva", 1250)), step=50)
            with c_t_p:
                trans_pri = st.selectbox("Primary Voltage", options=["33 kV", "11 kV", "6.6 kV", "3.3 kV"], index=["33 kV", "11 kV", "6.6 kV", "3.3 kV"].index(proj.get("transformer_primary_kv", "11 kV")))
            with c_t_s:
                trans_sec = st.selectbox("Secondary Voltage", options=["0.415 kV", "0.690 kV", "3.3 kV"], index=["0.415 kV", "0.690 kV", "3.3 kV"].index(proj.get("transformer_secondary_kv", "0.415 kV")))
        else:
            trans_qty, trans_rating, trans_pri, trans_sec = 0, 0, "11 kV", "0.415 kV"

    # 2. Switchgear Panels
    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        panels_req = st.checkbox("Switchgear Panels", value=proj.get("panels_required", True))
    with col_p2:
        if panels_req:
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                ht_panels_qty = st.number_input("HT Panel Quantity", min_value=0, max_value=20, value=int(proj.get("ht_panel_qty", 4)))
            with c_p2:
                lt_panels_qty = st.number_input("LT Panel Quantity", min_value=0, max_value=30, value=int(proj.get("lt_panel_qty", 6)))
        else:
            ht_panels_qty, lt_panels_qty = 0, 0

    # 3. Circuit Breakers
    col_cb1, col_cb2 = st.columns([1, 3])
    with col_cb1:
        cb_req = st.checkbox("Circuit Breakers", value=proj.get("circuit_breakers_required", True))
    with col_cb2:
        if cb_req:
            c_cb1, c_cb2 = st.columns(2)
            with c_cb1:
                cb_qty = st.number_input("Breaker Quantity", min_value=1, max_value=50, value=int(proj.get("cb_qty", 4)))
            with c_cb2:
                cb_type = st.selectbox("Breaker Category", options=["MCB", "MCCB", "ACB", "VCB", "Not decided"], index=["MCB", "MCCB", "ACB", "VCB", "Not decided"].index(proj.get("cb_type", "ACB")))
        else:
            cb_qty, cb_type = 0, "ACB"

    # 4. CT / PT
    col_ct1, col_ct2 = st.columns([1, 3])
    with col_ct1:
        ct_pt_req = st.checkbox("CT / PT Instrument Sets", value=proj.get("ct_pt_required", True))
    with col_ct2:
        if ct_pt_req:
            st.caption("Instrument transformers for metering and protection relays.")

    # 5. Isolators
    col_iso1, col_iso2 = st.columns([1, 3])
    with col_iso1:
        isolators_req = st.checkbox("Isolators / Disconnectors", value=proj.get("isolators_required", True))
    with col_iso2:
        if isolators_req:
            st.caption(f"Air-break disconnectors rated for {system_voltage} isolation.")

    # 6. Cables
    col_c1, col_c2 = st.columns([1, 3])
    with col_c1:
        cable_req = st.checkbox("Power Cables", value=proj.get("cable_required", True))
    with col_c2:
        if cable_req:
            c_c1, c_c2, c_c3 = st.columns(3)
            with c_c1:
                cable_len = st.number_input("Cable Length (metres)", min_value=10, max_value=10000, value=int(proj.get("cable_length_m", 500)), step=50)
            with c_c2:
                cable_v = st.selectbox("Cable Voltage Level", options=["1.1 kV", "3.3 kV", "11 kV", "33 kV"], index=["1.1 kV", "3.3 kV", "11 kV", "33 kV"].index(proj.get("cable_voltage", "11 kV") if proj.get("cable_voltage") in ["1.1 kV", "3.3 kV", "11 kV", "33 kV"] else "11 kV"))
            with c_c3:
                cable_qty = st.number_input("Runs / Circuits", min_value=1, max_value=10, value=int(proj.get("cable_qty", 1)))
        else:
            cable_len, cable_v, cable_qty = 0, "11 kV", 0

    st.markdown("---")

    # SECTION C: Procurement Requirements & Stated Priorities
    st.markdown("### 💰 **Section C: Commercial Constraints & Stated Priorities**")
    col_c_b1, col_c_b2 = st.columns(2)
    with col_c_b1:
        max_budget = st.number_input(
            "Estimated Project Budget (₹ lakh) *",
            min_value=1.0,
            max_value=1000.0,
            value=float(proj.get("budget_lakh", 50.0)),
            step=1.0
        )
    with col_c_b2:
        required_delivery = st.number_input(
            "Required Delivery Schedule (weeks) *",
            min_value=1,
            max_value=52,
            value=int(proj.get("delivery_weeks", 8)),
            step=1
        )

    st.markdown("#### **Stated Procurement Priorities**")
    st.caption("Indicate your initial qualitative priorities. *(Note: Page 6 uses its own independent multi-criteria scoring model)*")

    p_c1, p_c2, p_c3, p_c4 = st.columns(4)
    with p_c1:
        raw_cost_prio = st.slider("Cost Importance", 0, 100, int(proj.get("raw_cost_prio", 40)))
    with p_c2:
        raw_tech_prio = st.slider("Technical Quality", 0, 100, int(proj.get("raw_tech_prio", 30)))
    with p_c3:
        raw_deliv_prio = st.slider("Delivery Speed", 0, 100, int(proj.get("raw_deliv_prio", 20)))
    with p_c4:
        raw_warr_prio = st.slider("Warranty / Service", 0, 100, int(proj.get("raw_warr_prio", 10)))

    # Priority Normalization Preview
    tot_prio = raw_cost_prio + raw_tech_prio + raw_deliv_prio + raw_warr_prio
    if tot_prio > 0:
        norm_cost = round((raw_cost_prio / tot_prio) * 100, 1)
        norm_tech = round((raw_tech_prio / tot_prio) * 100, 1)
        norm_deliv = round((raw_deliv_prio / tot_prio) * 100, 1)
        norm_warr = round((raw_warr_prio / tot_prio) * 100, 1)
    else:
        norm_cost, norm_tech, norm_deliv, norm_warr = 25.0, 25.0, 25.0, 25.0

    st.info(
        f"📊 **Stated Priorities:** Cost: **{norm_cost}%** | Technical Quality: **{norm_tech}%** | "
        f"Delivery: **{norm_deliv}%** | Warranty/Service: **{norm_warr}%**"
    )

    st.markdown("---")
    submitted = st.form_submit_button("💾 Save Project Requirement", type="primary", use_container_width=True)

if submitted:
    # Validation Rules (Section 30 & 84)
    validation_errors = []

    if not str(project_name).strip():
        validation_errors.append("Project Name cannot be empty.")
    if total_load_kw <= 0:
        validation_errors.append("Total connected load must be greater than 0 kW.")
    if max_budget <= 0:
        validation_errors.append("Budget must be greater than ₹0 lakh.")
    if required_delivery <= 0:
        validation_errors.append("Required delivery must be greater than 0 weeks.")
    if transformer_req and trans_rating <= 0:
        validation_errors.append("Please enter a valid transformer rating (> 0 kVA).")
    
    # Check at least one equipment category selected
    has_any_eq = any([transformer_req, panels_req, cb_req, ct_pt_req, isolators_req, cable_req])
    if not has_any_eq:
        validation_errors.append("Please select at least one equipment category for the project.")

    if validation_errors:
        for err in validation_errors:
            st.error(f"⚠️ {err}")
    else:
        # Save to session_state
        updated_project = {
            "project_name": str(project_name).strip(),
            "industry": industry,
            "project_location": project_location,
            "completion_weeks": completion_weeks,
            "total_load_kw": total_load_kw,
            "system_voltage": system_voltage,
            "feeders_count": feeders_count,
            "transformer_required": transformer_req,
            "transformer_qty": trans_qty,
            "transformer_rating_kva": trans_rating,
            "transformer_primary_kv": trans_pri,
            "transformer_secondary_kv": trans_sec,
            "panels_required": panels_req,
            "ht_panel_qty": ht_panels_qty,
            "lt_panel_qty": lt_panels_qty,
            "circuit_breakers_required": cb_req,
            "cb_qty": cb_qty,
            "cb_type": cb_type,
            "ct_pt_required": ct_pt_req,
            "isolators_required": isolators_req,
            "cable_required": cable_req,
            "cable_length_m": cable_len,
            "cable_voltage": cable_v,
            "cable_qty": cable_qty,
            "budget_lakh": max_budget,
            "delivery_weeks": required_delivery,
            "raw_cost_prio": raw_cost_prio,
            "raw_tech_prio": raw_tech_prio,
            "raw_deliv_prio": raw_deliv_prio,
            "raw_warr_prio": raw_warr_prio,
            "stated_priorities": {
                "cost": norm_cost,
                "technical": norm_tech,
                "delivery": norm_deliv,
                "warranty": norm_warr
            }
        }
        st.session_state.project_details = updated_project

        # Automatically generate structured equipment list
        eq_list = build_equipment_list(updated_project)
        st.session_state.equipment_requirements = eq_list

        st.success("✅ Project requirement saved successfully.")

# Display summary card if project is saved
if st.session_state.get("project_details"):
    p = st.session_state.project_details
    st.markdown("### 📋 **Active Project Summary**")
    
    col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
    with col_s1:
        st.markdown(f"**Project**<br>{p.get('project_name')}", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"**Load**<br>{p.get('total_load_kw')} kW", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"**Voltage**<br>{p.get('system_voltage')}", unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"**Budget**<br>₹{p.get('budget_lakh'):.2f} lakh", unsafe_allow_html=True)
    with col_s5:
        st.markdown(f"**Delivery**<br>{p.get('delivery_weeks')} weeks", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("➡️ Continue to Equipment Requirement", type="primary", use_container_width=True):
        st.switch_page("pages/02_Equipment_Requirement.py")
