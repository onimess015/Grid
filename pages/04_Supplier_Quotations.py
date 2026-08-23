"""
04_Supplier_Quotations.py
Step 4: Ingest and manage supplier quotations via demo CSV dataset or manual bid entry.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.ui_helpers import (
    render_sidebar,
    render_page_header,
    check_page_guard,
    init_session_state,
    DEMO_DATA_LABEL
)
from modules.quotation_logic import load_demo_suppliers, validate_quote

st.set_page_config(
    page_title="Step 4: Supplier Quotations — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="4. Supplier Quotations",
    subtitle="Capture and compare hypothetical supplier quotations."
)

# Page Guard: Requires Step 2 Equipment Requirements
if not check_page_guard("equipment_requirements", "pages/02_Equipment_Requirement.py", "Equipment Requirement"):
    st.stop()

eq_list = st.session_state.get("equipment_requirements", [])
eq_types = sorted(list(set([item.get("equipment_type", "Transformer") for item in eq_list])))

# Initialize supplier_quotes dict in session state
if not st.session_state.get("supplier_quotes") or not isinstance(st.session_state.supplier_quotes, dict):
    st.session_state.supplier_quotes = {}

# Selected Equipment Category Selector for viewing/managing quotations
st.markdown("### 🔍 **Select Equipment Category to Manage Quotations**")
col_sel1, col_sel2 = st.columns([2, 2])
with col_sel1:
    selected_eq_type = st.selectbox(
        "Equipment Category",
        options=eq_types,
        index=0 if "Transformer" in eq_types else 0,
        help="Select equipment to view or ingest supplier bids"
    )
with col_sel2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("📥 Load Pre-Configured Demo Suppliers", type="primary", use_container_width=True):
        demo_data = load_demo_suppliers()
        # Group demo data by equipment_type
        for d in demo_data:
            e_type = d.get("equipment_type", "Transformer")
            if e_type not in st.session_state.supplier_quotes:
                st.session_state.supplier_quotes[e_type] = []
            
            # Avoid duplicate suppliers in the same category
            existing_names = [x.get("supplier_name") for x in st.session_state.supplier_quotes[e_type]]
            if d.get("supplier_name") not in existing_names:
                st.session_state.supplier_quotes[e_type].append(d)

        st.toast("✅ Demo supplier quotations loaded successfully.")
        st.rerun()

st.caption(f"<span class='demo-tag'>{DEMO_DATA_LABEL}</span>", unsafe_allow_html=True)

# Retrieve current quotes for selected equipment category
current_quotes = st.session_state.supplier_quotes.get(selected_eq_type, [])

st.markdown("---")

# Section: Current Quotations Table
st.markdown(f"### 📊 **Received Quotations for {selected_eq_type}**")

if current_quotes:
    table_data = []
    for q in current_quotes:
        price_val = float(q.get("unit_price_inr_lakh", 0))
        deliv_val = int(q.get("delivery_weeks", 0))
        war_val = int(q.get("warranty_years", 0))
        off_rating = q.get("offered_rating_kva", 0)
        off_pri = q.get("offered_primary_kv", 11.0)
        off_sec = q.get("offered_secondary_kv", 0.415)

        spec_str = f"{off_rating:.0f} kVA ({off_pri:.3g} kV / {off_sec:.3g} kV)" if selected_eq_type == "Transformer" else "Standard Spec"

        table_data.append({
            "Supplier Name": q.get("supplier_name"),
            "Unit Price (₹ lakh)": f"₹{price_val:.2f} lakh",
            "Delivery Time": f"{deliv_val} weeks",
            "Technical Score": f"{float(q.get('technical_score', 90)):.1f}",
            "Quality Score": f"{float(q.get('quality_score', 90)):.1f}",
            "Warranty": f"{war_val} years",
            "Offered Specification": spec_str,
            "Payment Terms": q.get("payment_terms", "Standard")
        })

    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    if len(current_quotes) < 2:
        st.warning(f"⚠️ Only {len(current_quotes)} supplier bid recorded for {selected_eq_type}. At least 2 suppliers are recommended for competitive comparison.")

    # Remove Supplier Section with Safe Confirmation
    with st.expander("🗑️ **Remove Supplier Quotation**"):
        col_rm1, col_rm2 = st.columns([3, 2])
        with col_rm1:
            sup_names = [q.get("supplier_name") for q in current_quotes]
            selected_rm = st.selectbox("Select Supplier to Remove", options=sup_names, key=f"sel_rm_{selected_eq_type}")
        with col_rm2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            confirm_key = f"confirm_rm_{selected_eq_type}_{selected_rm}"
            if st.session_state.get(confirm_key, False):
                st.warning(f"Remove {selected_rm}?")
                c_y, c_n = st.columns(2)
                with c_y:
                    if st.button("Confirm", key=f"yes_rm_{selected_rm}", type="primary"):
                        st.session_state.supplier_quotes[selected_eq_type] = [
                            x for x in st.session_state.supplier_quotes[selected_eq_type] if x.get("supplier_name") != selected_rm
                        ]
                        st.session_state[confirm_key] = False
                        st.toast(f"Removed {selected_rm}.")
                        st.rerun()
                with c_n:
                    if st.button("Cancel", key=f"no_rm_{selected_rm}"):
                        st.session_state[confirm_key] = False
                        st.rerun()
            else:
                if st.button("Delete Quotation", key=f"btn_rm_{selected_rm}"):
                    st.session_state[confirm_key] = True
                    st.rerun()
else:
    st.info(f"💡 No supplier quotations ingested yet for **{selected_eq_type}**. Click **Load Pre-Configured Demo Suppliers** or add a quotation manually below.")

st.markdown("---")

# Section: Manual Entry Form
with st.expander(f"➕ **Add Manual Supplier Quotation for {selected_eq_type}**"):
    with st.form(f"manual_quote_form_{selected_eq_type}"):
        st.markdown(f"##### **Commercial & Technical Offer Details ({selected_eq_type})**")
        
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            m_sup_name = st.text_input("Supplier / Bidder Name *", placeholder="e.g. Supplier D")
            m_price = st.number_input("Unit Price (₹ lakh) *", min_value=0.1, max_value=500.0, value=40.0, step=0.5)
        with c_m2:
            m_delivery = st.number_input("Delivery Lead Time (weeks) *", min_value=1, max_value=52, value=8, step=1)
            m_warranty = st.number_input("Warranty Period (years) *", min_value=1, max_value=10, value=3, step=1)
        with c_m3:
            m_quality = st.slider("Quality & Manufacturing Score (0–100)", min_value=50, max_value=100, value=90)
            m_payment = st.text_input("Payment Terms", value="30% advance, 70% on delivery")

        if selected_eq_type == "Transformer":
            st.markdown("##### **Offered Technical Specifications**")
            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1:
                m_off_rating = st.number_input("Offered Capacity (kVA) *", min_value=100, max_value=10000, value=1250, step=50)
            with c_s2:
                m_off_pri = st.number_input("Primary Voltage (kV)", min_value=0.415, max_value=66.0, value=11.0, step=0.1)
            with c_s3:
                m_off_sec = st.number_input("Secondary Voltage (kV)", min_value=0.220, max_value=33.0, value=0.415, step=0.005)
        else:
            m_off_rating, m_off_pri, m_off_sec = 0.0, 11.0, 0.415

        m_notes = st.text_area("Bid Notes / Qualifications", placeholder="Type tested, includes standard spare parts...")

        submitted_manual = st.form_submit_button("💾 Save Supplier Quotation", type="primary", use_container_width=True)

        if submitted_manual:
            new_quote_obj = {
                "supplier_name": m_sup_name.strip(),
                "equipment_type": selected_eq_type,
                "unit_price_inr_lakh": float(m_price),
                "delivery_weeks": int(m_delivery),
                "technical_score": 90.0,
                "quality_score": float(m_quality),
                "warranty_years": int(m_warranty),
                "payment_terms": m_payment.strip(),
                "offered_rating_kva": float(m_off_rating),
                "offered_primary_kv": float(m_off_pri),
                "offered_secondary_kv": float(m_off_sec),
                "notes": m_notes.strip()
            }

            errors = validate_quote(new_quote_obj)
            if errors:
                for err in errors:
                    st.error(f"⚠️ {err}")
            else:
                if selected_eq_type not in st.session_state.supplier_quotes:
                    st.session_state.supplier_quotes[selected_eq_type] = []
                
                # Replace if already exists with same name, otherwise append
                existing_idx = next(
                    (idx for idx, x in enumerate(st.session_state.supplier_quotes[selected_eq_type]) if x.get("supplier_name") == new_quote_obj["supplier_name"]),
                    None
                )
                if existing_idx is not None:
                    st.session_state.supplier_quotes[selected_eq_type][existing_idx] = new_quote_obj
                    st.success(f"Updated quotation for {new_quote_obj['supplier_name']}.")
                else:
                    st.session_state.supplier_quotes[selected_eq_type].append(new_quote_obj)
                    st.success(f"Added new quotation for {new_quote_obj['supplier_name']}.")
                st.rerun()

st.markdown("---")

# Navigation
col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    if st.button("⬅️ Back to RFQ Generator", use_container_width=True):
        st.switch_page("pages/03_RFQ_Generator.py")
with col_nav2:
    # Check if at least one supplier quotation exists across all items
    has_any_quotes = any(len(v) > 0 for v in st.session_state.supplier_quotes.values()) if isinstance(st.session_state.supplier_quotes, dict) else False
    if st.button("➡️ Proceed to Technical Evaluation", type="primary", use_container_width=True, disabled=not has_any_quotes):
        st.switch_page("pages/05_Technical_Evaluation.py")
