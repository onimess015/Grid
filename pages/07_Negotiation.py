"""
07_Negotiation.py
Step 7: Simulate commercial price negotiations, compute cost savings,
recalculate weighted scores, and observe dynamic ranking shifts.
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
from modules.negotiation_logic import recompute_ranking_after_negotiation, apply_discount

st.set_page_config(
    page_title="Step 7: Negotiation Simulator — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="7. Negotiation Simulator",
    subtitle="Simulate a supplier price negotiation and observe its effect on the commercial ranking."
)

# Page Guard: Requires Step 6 Commercial Evaluation
if not check_page_guard("commercial_scores", "pages/06_Commercial_Evaluation.py", "Commercial Evaluation"):
    st.stop()

comm_scores = st.session_state.get("commercial_scores", {})
tech_scores = st.session_state.get("technical_scores", {})
available_eqs = list(comm_scores.keys())

if not available_eqs:
    st.warning("⚠️ Commercial evaluation data not found. Please complete Step 6.")
    st.stop()

# Equipment Selector
st.markdown("### 🔍 **Select Equipment Package for Commercial Negotiation**")
selected_eq_type = st.selectbox("Equipment Category", options=available_eqs, index=0)

eq_comm_data = comm_scores.get(selected_eq_type, {})
original_ranked = eq_comm_data.get("ranked_quotes", [])
weights_used = eq_comm_data.get("weights_used", {"price": 40, "technical": 30, "delivery": 15, "quality": 10, "warranty": 5})
tech_eval_map = tech_scores.get(selected_eq_type, {})
best_overall_default = eq_comm_data.get("best_overall_supplier", {}).get("supplier_name", "")

# Filter qualified suppliers first for default selection
qualified_sups = [q["supplier_name"] for q in original_ranked if q.get("is_qualified", False)]
all_sups = [q["supplier_name"] for q in original_ranked]

default_sup_index = 0
if best_overall_default in all_sups:
    default_sup_index = all_sups.index(best_overall_default)
elif qualified_sups and qualified_sups[0] in all_sups:
    default_sup_index = all_sups.index(qualified_sups[0])

st.markdown("---")

# Negotiation Inputs Form
col_inp1, col_inp2 = st.columns([1, 1])

with col_inp1:
    target_supplier = st.selectbox(
        "Select Supplier to Negotiate With",
        options=all_sups,
        index=default_sup_index,
        help="Select bidder for targeted commercial counter-offer"
    )
    
    # Retrieve target supplier quote details
    target_quote = next((q for q in original_ranked if q["supplier_name"] == target_supplier), {})
    orig_price = float(target_quote.get("unit_price_inr_lakh", 0.0))

    discount_pct = st.slider(
        "Negotiated Discount (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.5,
        help="Target commercial price concession"
    )

with col_inp2:
    justification_presets = [
        "Bulk project order volume commitment",
        "Competitive quotation benchmarking & volume leverage",
        "Extended payment milestone terms agreed",
        "Framework agreement & long-term business potential",
        "Expedited payment terms (100% LC on dispatch)"
    ]
    justification_choice = st.selectbox("Negotiation Rationale / Justification", options=justification_presets)
    justification_text = st.text_area(
        "Commercial Notes & Strategy",
        value=f"Negotiation applied based on {justification_choice.lower()}.",
        height=75
    )

# Live calculation of discount & savings
discount_calc = apply_discount(orig_price, discount_pct)

# Interactive Negotiation Calculation Breakdown
with st.expander("🧮 **CLICK HERE: How Negotiated Prices, Savings & Re-Ranking are Calculated**", expanded=False):
    st.markdown(
        f"""
        ### 📐 **Step-by-Step Negotiation Formulas:**
        1. **Negotiated Price:**
           $$\\text{{Negotiated Price}} = \\text{{Original Price}} \\times \\left(1 - \\frac{{\\text{{Discount \\%}}}}{{100}}\\right)$$
           $$\\text{{Calculated: }} ₹{orig_price:.2f}\\text{{ lakh}} \\times (1 - {discount_pct/100:.2f}) = \\mathbf{{₹{discount_calc['negotiated_price']:.2f}\\text{{ lakh}}}}$$

        2. **Financial Value Created (Cost Savings):**
           $$\\text{{Project Savings}} = \\text{{Original Price}} - \\text{{Negotiated Price}} = ₹{orig_price:.2f}\\text{{L}} - ₹{discount_calc['negotiated_price']:.2f}\\text{{L}} = \\mathbf{{₹{discount_calc['savings']:.2f}\\text{{ lakh}}}}$$

        3. **Re-Ranking Algorithm:**
           - The affected supplier's price is updated from **₹{orig_price:.2f}L** to **₹{discount_calc['negotiated_price']:.2f}L**.
           - Its Price Score and composite Overall Score are recomputed dynamically.
           - All competing suppliers are re-sorted to determine whether the negotiation triggered a rank shift (e.g. #2 $\\rightarrow$ #1).
           - **Audit Guarantee:** Original baseline quotes are preserved without overwrite.
        """
    )

st.markdown("---")


# 4 Key Negotiation KPI Cards
st.markdown("### 💰 **Negotiation Impact & Value Creation**")

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric(
        label="Original Quoted Price",
        value=f"₹{discount_calc['original_price']:.2f} lakh"
    )

with col_kpi2:
    st.metric(
        label="Applied Discount",
        value=f"{discount_calc['discount_percent']:.1f}%",
        delta=f"-{discount_calc['discount_percent']:.1f}%" if discount_calc['discount_percent'] > 0 else "0.0%"
    )

with col_kpi3:
    st.metric(
        label="Negotiated Price",
        value=f"₹{discount_calc['negotiated_price']:.2f} lakh",
        delta=f"-₹{discount_calc['savings']:.2f} lakh" if discount_calc['savings'] > 0 else None,
        delta_color="inverse"
    )

with col_kpi4:
    st.metric(
        label="Net Project Savings",
        value=f"₹{discount_calc['savings']:.2f} lakh" if discount_calc['savings'] > 0 else "₹0.00 lakh"
    )

st.markdown("---")

# Apply Negotiation Action
simulated_result = recompute_ranking_after_negotiation(
    original_ranked_quotes=original_ranked,
    target_supplier_name=target_supplier,
    discount_percent=discount_pct,
    justification=justification_text,
    weights=weights_used,
    tech_eval_map=tech_eval_map
)

col_app1, col_app2 = st.columns([1, 3])
with col_app1:
    if st.button("🤝 Apply & Commit Negotiation", type="primary", use_container_width=True):
        if not st.session_state.get("negotiation_results") or not isinstance(st.session_state.negotiation_results, dict):
            st.session_state.negotiation_results = {}

        st.session_state.negotiation_results[selected_eq_type] = simulated_result
        st.toast(f"✅ Committed negotiation for {target_supplier} (-₹{discount_calc['savings']:.2f} lakh).")
        st.success(f"Negotiation successfully locked for {target_supplier}.")

st.markdown("---")

# Rank Delta Comparison View
st.markdown("### 🔄 **Comparative Ranking: Before vs After Negotiation**")

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.markdown("##### **Original Standings (Before Negotiation)**")
    old_rows = []
    for r in original_ranked:
        old_rows.append({
            "Rank": f"#{r['rank']}",
            "Supplier": r["supplier_name"],
            "Price": f"₹{r['unit_price_inr_lakh']:.2f} lakh",
            "Price Score": f"{r['price_score']:.1f}",
            "Overall Score": f"{r['overall_score']:.1f}",
            "Status": r["status"]
        })
    st.dataframe(pd.DataFrame(old_rows), use_container_width=True, hide_index=True)

with col_r2:
    st.markdown(f"##### **Post-Negotiation Standings (Target: {target_supplier})**")
    new_rows = []
    for r in simulated_result.get("new_ranked_quotes", []):
        s_name = r["supplier_name"]
        movement = simulated_result.get("rank_changes", {}).get(s_name, {}).get("delta_str", "")
        new_rows.append({
            "New Rank": f"#{r['rank']}",
            "Supplier": s_name,
            "Effective Price": f"₹{r['unit_price_inr_lakh']:.2f} lakh",
            "Price Score": f"{r['price_score']:.1f}",
            "Overall Score": f"{r['overall_score']:.1f}",
            "Rank Shift": movement
        })
    st.dataframe(pd.DataFrame(new_rows), use_container_width=True, hide_index=True)

st.caption(f"<span class='demo-tag'>{DEMO_DATA_LABEL}</span>", unsafe_allow_html=True)

st.markdown("---")

# Navigation
col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    if st.button("⬅️ Back to Commercial Evaluation", use_container_width=True):
        st.switch_page("pages/06_Commercial_Evaluation.py")
with col_nav2:
    if st.button("➡️ Proceed to Final Recommendation", type="primary", use_container_width=True):
        # Auto commit simulation if user hasn't explicitly clicked button
        if selected_eq_type not in st.session_state.get("negotiation_results", {}):
            if not st.session_state.get("negotiation_results") or not isinstance(st.session_state.negotiation_results, dict):
                st.session_state.negotiation_results = {}
            st.session_state.negotiation_results[selected_eq_type] = simulated_result
        st.switch_page("pages/08_Final_Recommendation.py")
