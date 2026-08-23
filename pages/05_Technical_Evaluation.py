"""
05_Technical_Evaluation.py
Step 5: Rigorous rule-based technical verification of supplier specifications
against RFQ engineering requirements, transparent scoring, and mismatch flagging.
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
from modules.evaluation_logic import compare_specs, compute_technical_score

st.set_page_config(
    page_title="Step 5: Technical Evaluation — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="5. Technical Evaluation",
    subtitle="Compare supplier offerings against the project's required specifications."
)

# Page Guard: Requires Step 4 Supplier Quotations
if not check_page_guard("supplier_quotes", "pages/04_Supplier_Quotations.py", "Supplier Quotations"):
    st.stop()

eq_list = st.session_state.get("equipment_requirements", [])
quotes_dict = st.session_state.get("supplier_quotes", {})

# Filter available equipment categories that have quotations
available_eqs = [eq for eq, q_list in quotes_dict.items() if len(q_list) > 0]
if not available_eqs:
    st.warning("⚠️ No supplier quotations found. Ingest supplier quotations in Step 4 first.")
    if st.button("➡️ Go to Supplier Quotations", type="primary"):
        st.switch_page("pages/04_Supplier_Quotations.py")
    st.stop()

# Equipment Category Selector
st.markdown("### 🔍 **Select Equipment Category for Technical Bid Conditioning**")
selected_eq_type = st.selectbox(
    "Equipment Category",
    options=available_eqs,
    index=0 if "Transformer" in available_eqs else 0
)

# Find matching required spec item from equipment_requirements
req_item = next((item for item in eq_list if item.get("equipment_type") == selected_eq_type), {})
current_quotes = quotes_dict.get(selected_eq_type, [])

# Explander: Technical Scoring Methodology & Live Calculation Breakdown
with st.expander("🧮 **CLICK HERE: Step-by-Step Technical Scoring Calculation & Mismatch Deductions**", expanded=False):
    st.markdown("### 📐 **How Technical Score & Qualification are Calculated:**")
    st.markdown(
        """
        - **1. Base Starting Score:** Every evaluated supplier starts with **100.0 points**.
        - **2. Critical Parameter Mismatch Penalty (`-40 points` per critical failure):**
          - **Transformer Capacity:** If Offered kVA < Required kVA $\\rightarrow$ **-40 points** (e.g. Supplier B offers 1000 kVA when 1250 kVA is required $\\rightarrow$ $100 - 40 = 60.0$).
          - **Voltage Levels:** If Primary kV or Secondary kV fails exact nominal match $\\rightarrow$ **-40 points**.
        - **3. Non-Critical Parameter Mismatch Penalty (`-10 points`):**
          - Minor accessory or auxiliary variance.
        - **4. Mathematical Floor & Ceiling:** $\\text{Technical Score} = \\max(0.0, \\min(100.0, \\text{Calculated Score}))$.
        - **5. Qualification Gate:**
          - **Qualified (🟢):** 0 critical mismatches AND Technical Score $\\ge 60.0$.
          - **Disqualified (⚠️ Technical Mismatch):** 1 or more critical mismatches (strictly excluded from final winning recommendations).
        """
    )


st.markdown("---")

# Run Technical Evaluation for each supplier
if not st.session_state.get("technical_scores") or not isinstance(st.session_state.technical_scores, dict):
    st.session_state.technical_scores = {}

eval_results_map = {}
summary_table_rows = []

st.markdown(f"### 📋 **Specification Compliance Check: {selected_eq_type}**")

cols = st.columns(len(current_quotes)) if len(current_quotes) <= 3 else [st.container() for _ in current_quotes]

for idx, q in enumerate(current_quotes):
    s_name = q.get("supplier_name", f"Supplier {idx+1}")
    comp_results = compare_specs(req_item, q)
    tech_eval = compute_technical_score(comp_results)
    eval_results_map[s_name] = tech_eval

    # Display Supplier Technical Card
    with (cols[idx] if len(current_quotes) <= 3 else st.container()):
        card_class = "badge-danger" if tech_eval["has_critical_mismatch"] else "badge-success"
        badge_text = "⚠️ Technical Mismatch" if tech_eval["has_critical_mismatch"] else "🟢 Qualified"
        
        st.markdown(f"#### **{s_name}**")
        st.markdown(f"<span class='{card_class}'>{badge_text}</span>", unsafe_allow_html=True)
        st.metric(label="Technical Score", value=f"{tech_eval['technical_score']:.1f} / 100")

        st.markdown("##### **Parameter Verification:**")
        for comp in comp_results:
            icon = "✅" if comp["match"] else "❌"
            crit_badge = " *(Critical)*" if comp["is_critical"] else ""
            st.write(f"{icon} **{comp['field']}{crit_badge}:** {comp['offered']} *(Req: {comp['required']})*")

        if tech_eval["has_critical_mismatch"]:
            st.error(f"⚠️ **Disqualification Note:** {tech_eval['mismatch_details'][0]}")

        st.markdown("---")

    # Add row to summary table
    summary_table_rows.append({
        "Supplier": s_name,
        "Offered Rating": f"{q.get('offered_rating_kva', 0):.0f} kVA" if selected_eq_type == "Transformer" else "Standard",
        "Primary kV": f"{q.get('offered_primary_kv', 11):.3g} kV",
        "Secondary kV": f"{q.get('offered_secondary_kv', 0.415):.3g} kV",
        "Critical Mismatches": tech_eval["critical_mismatches_count"],
        "Technical Score": f"{tech_eval['technical_score']:.1f}",
        "Compliance Status": "⚠️ Technical Mismatch" if tech_eval["has_critical_mismatch"] else "🟢 Qualified"
    })

# Save evaluation results to session_state
st.session_state.technical_scores[selected_eq_type] = eval_results_map

# Summary Matrix
st.markdown("### 📊 **Technical Evaluation Matrix**")
df_tech = pd.DataFrame(summary_table_rows)
st.dataframe(df_tech, use_container_width=True, hide_index=True)

st.caption(f"<span class='demo-tag'>{DEMO_DATA_LABEL}</span>", unsafe_allow_html=True)

st.markdown("---")

# Navigation
col_n1, col_n2 = st.columns([1, 1])
with col_n1:
    if st.button("⬅️ Back to Supplier Quotations", use_container_width=True):
        st.switch_page("pages/04_Supplier_Quotations.py")
with col_n2:
    if st.button("➡️ Proceed to Commercial Evaluation", type="primary", use_container_width=True):
        st.switch_page("pages/06_Commercial_Evaluation.py")
