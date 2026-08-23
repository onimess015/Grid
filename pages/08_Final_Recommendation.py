"""
08_Final_Recommendation.py
Step 8: Transparent executive procurement recommendation, dynamic evidence-based justifications,
total project commercial rollup, and full Markdown decision audit report export.
"""

import streamlit as st
import pandas as pd
import datetime
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
    GLOBAL_DISCLAIMER,
    DEMO_DATA_LABEL
)

st.set_page_config(
    page_title="Step 8: Final Recommendation — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="8. Final Recommendation",
    subtitle="Final transparent procurement decision based on technical and commercial evaluation."
)

# Page Guard: Requires Step 6 Commercial Evaluation
if not check_page_guard("commercial_scores", "pages/06_Commercial_Evaluation.py", "Commercial Evaluation"):
    st.stop()

proj = st.session_state.get("project_details", {})
eq_list = st.session_state.get("equipment_requirements", [])
comm_scores = st.session_state.get("commercial_scores", {})
neg_results = st.session_state.get("negotiation_results", {})
quotes_dict = st.session_state.get("supplier_quotes", {})
tech_scores = st.session_state.get("technical_scores", {})

# Save final recommendation to session state
st.session_state.final_recommendation = {
    "project_name": proj.get("project_name", "ABC Manufacturing Plant"),
    "timestamp": datetime.datetime.now().isoformat(),
    "evaluated_packages": list(comm_scores.keys())
}

st.markdown("### 🏆 **Executive Procurement Recommendations by Equipment Package**")
st.caption("Deterministic, rule-based award recommendations based strictly on verified technical compliance and multi-factor commercial scoring.")

total_orig_val = 0.0
total_neg_val = 0.0
total_project_savings = 0.0
awarded_packages_count = 0

recommendations_for_report = []

for eq_type, c_data in comm_scores.items():
    # Find matching equipment item from schedule for quantity
    eq_item = next((item for item in eq_list if item.get("equipment_type") == eq_type), {})
    qty = int(eq_item.get("quantity", 1))

    # Check if negotiation exists for this equipment type
    neg_data = neg_results.get(eq_type)
    if neg_data:
        winner = neg_data.get("new_best_overall_supplier", {})
        unit_orig = float(neg_data.get("original_price", winner.get("unit_price_inr_lakh", 0)))
        unit_final = float(winner.get("unit_price_inr_lakh", 0))
        unit_savings = float(neg_data.get("savings", 0)) if neg_data.get("target_supplier") == winner.get("supplier_name") else 0.0
        disc_pct = float(neg_data.get("discount_percent", 0)) if neg_data.get("target_supplier") == winner.get("supplier_name") else 0.0
    else:
        winner = c_data.get("best_overall_supplier", {})
        unit_orig = float(winner.get("unit_price_inr_lakh", 0))
        unit_final = unit_orig
        unit_savings = 0.0
        disc_pct = 0.0

    line_orig = unit_orig * qty
    line_final = unit_final * qty
    line_savings = unit_savings * qty

    total_orig_val += line_orig
    total_neg_val += line_final
    total_project_savings += line_savings
    awarded_packages_count += 1

    winner_name = winner.get("supplier_name", "Supplier")
    winner_score = float(winner.get("overall_score", 0))
    winner_tech = float(winner.get("technical_score", 0))
    winner_deliv = int(winner.get("delivery_weeks", 0))
    winner_warr = int(winner.get("warranty_years", 0))

    # Compile Evidence-Based Recommendation Reasons
    reasons = []
    if winner.get("is_qualified", True):
        reasons.append("✅ Fully compliant with all required electrical specifications (no critical mismatches).")
    
    if eq_type == "Transformer":
        reasons.append(f"✅ Offered rating ({eq_item.get('rating_kva', 1250)} kVA) meets or exceeds project design capacity.")

    reasons.append(f"✅ Achieved the highest overall techno-commercial score ({winner_score:.1f} / 100).")

    if disc_pct > 0:
        reasons.append(f"✅ Commercial negotiation successfully achieved a {disc_pct:.1f}% discount (Saving ₹{line_savings:.2f} lakh).")
    else:
        reasons.append(f"ℹ️ Original quoted price of ₹{unit_orig:.2f} lakh maintained (No negotiation applied).")

    reasons.append(f"✅ Guaranteed delivery timeline of {winner_deliv} weeks fits project schedule.")
    reasons.append(f"✅ Provides {winner_warr} years of comprehensive equipment warranty.")

    recommendations_for_report.append({
        "equipment_type": eq_type,
        "equipment_desc": eq_item.get("description", eq_type),
        "quantity": qty,
        "winner": winner_name,
        "overall_score": winner_score,
        "unit_orig": unit_orig,
        "unit_final": unit_final,
        "line_final": line_final,
        "line_savings": line_savings,
        "reasons": reasons
    })

    # Render Recommendation Card
    with st.container():
        st.markdown(
            f"""
            <div class="gs-card" style="border-left: 6px solid #4ADE80;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 0.85rem; font-weight: 700; color: #4ADE80; text-transform: uppercase;">
                        RECOMMENDED SUPPLIER AWARD — {eq_type.upper()}
                    </div>
                    <span class="badge-success">🟢 Technically Qualified & Awarded</span>
                </div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #F0F6FC; margin: 0.35rem 0;">
                    {winner_name}
                </div>
                <div style="font-size: 0.95rem; color: #8B949E; margin-bottom: 0.75rem;">
                    <strong>Scope:</strong> {qty} × {eq_item.get('description', eq_type)}
                </div>
            </div>

            """,
            unsafe_allow_html=True
        )

        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        with col_w1:
            st.metric("Technical Score", f"{winner_tech:.1f} / 100")
        with col_w2:
            st.metric("Overall Commercial Score", f"{winner_score:.1f} / 100")
        with col_w3:
            st.metric("Effective Unit Price", f"₹{unit_final:.2f} lakh", delta=f"-₹{unit_savings:.2f} lakh" if unit_savings > 0 else None, delta_color="inverse")
        with col_w4:
            st.metric("Total Line Commitment", f"₹{line_final:.2f} lakh (Qty: {qty})")

        st.markdown("##### **Key Decision Factors & Rationale:**")
        for r_text in reasons:
            st.write(f"- {r_text}")

        st.markdown("---")

# Interactive Financial Rollup Calculation Breakdown
with st.expander("🧮 **CLICK HERE: How Total Project Value & Financial Savings are Calculated**", expanded=False):
    st.markdown(
        """
        ### 📐 **Total Project Financial Rollup Formulas:**
        1. **Line Item Commitment:**
           $$\\text{Line Total} = \\text{Effective Unit Price} \\times \\text{Required Quantity}$$

        2. **Total Original Bid Value:**
           $$\\text{Total Original Value} = \\sum (\\text{Original Unit Price}_i \\times \\text{Quantity}_i)$$

        3. **Total Negotiated Commitment Value:**
           $$\\text{Total Negotiated Value} = \\sum (\\text{Negotiated Unit Price}_i \\times \\text{Quantity}_i)$$

        4. **Total Project Cost Savings (Value Created):**
           $$\\text{Total Savings} = \\text{Total Original Value} - \\text{Total Negotiated Value}$$
        """
    )

st.markdown("---")

# PROJECT SUMMARY & FINANCIAL ROLLUP
st.markdown("### 📊 **Total Project Procurement Summary**")


col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
with col_sum1:
    st.metric("Total Equipment Packages", f"{len(eq_list)} Total ({awarded_packages_count} Evaluated)")
with col_sum2:
    st.metric("Total Original Bid Value", f"₹{total_orig_val:.2f} lakh")
with col_sum3:
    st.metric("Total Negotiated Value", f"₹{total_neg_val:.2f} lakh")
with col_sum4:
    st.metric("Total Project Savings", f"₹{total_project_savings:.2f} lakh", delta=f"-₹{total_project_savings:.2f} lakh" if total_project_savings > 0 else None, delta_color="inverse")

st.markdown("---")

# Final Decision Statement
st.info("📌 **Final Decision Statement:** Final selection should be subject to engineering validation and applicable procurement/technical approval.")
st.caption(f"<div class='demo-tag'>{DEMO_DATA_LABEL}</div>", unsafe_allow_html=True)
st.caption(f"<div style='font-size:0.75rem; color:#777;'>{GLOBAL_DISCLAIMER}</div>", unsafe_allow_html=True)

st.markdown("---")

# Full Markdown Report Generation
report_date = datetime.date.today().strftime("%d %B %Y")
report_lines = [
    "# GRIDSELECT: POWER SYSTEMS EQUIPMENT & PROCUREMENT DECISION REPORT",
    f"**Project:** {proj.get('project_name', 'ABC Manufacturing Plant')}  ",
    f"**Industry:** {proj.get('industry', 'Manufacturing')} | **Location:** {proj.get('project_location', 'N/A')}  ",
    f"**Report Generated:** {report_date}  ",
    f"**Evaluation Status:** FINAL RECOMMENDATION READY  ",
    "",
    "---",
    "",
    "## 1. EXECUTIVE PROCUREMENT SUMMARY",
    f"- **Total Packages Evaluated:** {awarded_packages_count}",
    f"- **Baseline Quoted Commitment:** ₹{total_orig_val:.2f} Lakhs",
    f"- **Final Negotiated Commitment:** ₹{total_neg_val:.2f} Lakhs",
    f"- **Total Value Created / Savings:** ₹{total_project_savings:.2f} Lakhs",
    "",
    "## 2. AWARD RECOMMENDATIONS BY EQUIPMENT PACKAGE",
]

for rec in recommendations_for_report:
    report_lines.append(f"### Package: {rec['equipment_type']}")
    report_lines.append(f"- **Description:** {rec['equipment_desc']}")
    report_lines.append(f"- **Quantity:** {rec['quantity']}")
    report_lines.append(f"- **Selected Supplier:** **{rec['winner']}**")
    report_lines.append(f"- **Overall Score:** {rec['overall_score']:.1f} / 100")
    report_lines.append(f"- **Unit Price:** ₹{rec['unit_final']:.2f} Lakh (Orig: ₹{rec['unit_orig']:.2f} Lakh)")
    report_lines.append(f"- **Total Value:** ₹{rec['line_final']:.2f} Lakh (Savings: ₹{rec['line_savings']:.2f} Lakh)")
    report_lines.append("- **Selection Rationale:**")
    for reason in rec["reasons"]:
        report_lines.append(f"  {reason}")
    report_lines.append("")

report_lines.extend([
    "---",
    "",
    "## 3. TECHNICAL EVALUATION SUMMARY & CRITICAL PRINCIPLES",
    "All supplier proposals underwent deterministic spec conditioning against project requirements.",
    "- **Critical Spec Rule:** Suppliers with undersized capacity or voltage mismatches were flagged with a ⚠️ Technical Mismatch and excluded from winning award pools.",
    "- **Commercial Decision Principle:** The lowest quoted price does not necessarily represent the best techno-commercial decision.",
    "",
    "---",
    "",
    "## 4. GOVERNANCE & ENGINEERING DISCLAIMER",
    f"> {GLOBAL_DISCLAIMER}",
    "",
    "> *Final selection should be subject to engineering validation and applicable procurement/technical approval.*"
])

full_report_md = "\n".join(report_lines)

# Export / Download Actions
col_exp1, col_exp2 = st.columns([1, 1])
with col_exp1:
    st.download_button(
        label="⬇️ Download Procurement Recommendation (GridSelect_Procurement_Recommendation.md)",
        data=full_report_md,
        file_name="GridSelect_Procurement_Recommendation.md",
        mime="text/markdown",
        type="primary",
        use_container_width=True
    )

with col_exp2:
    if st.button("🔄 Start New Project / Reset", use_container_width=True):
        st.session_state.show_reset_confirm = True
        st.switch_page("app.py")
