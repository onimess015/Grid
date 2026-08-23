"""
06_Commercial_Evaluation.py
Step 6: Multi-criteria commercial bid evaluation, transparent weighted scoring,
clear separation between Lowest Price and Best Overall, and Plotly visual comparisons.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
from modules.evaluation_logic import compute_commercial_scores, rank_suppliers

st.set_page_config(
    page_title="Step 6: Commercial Evaluation — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="6. Commercial Evaluation",
    subtitle="Compare technically evaluated suppliers using transparent commercial criteria."
)

# Page Guard: Requires Step 5 Technical Evaluation
if not check_page_guard("technical_scores", "pages/05_Technical_Evaluation.py", "Technical Evaluation"):
    st.stop()

quotes_dict = st.session_state.get("supplier_quotes", {})
tech_scores_dict = st.session_state.get("technical_scores", {})

available_eqs = [eq for eq in quotes_dict.keys() if eq in tech_scores_dict]
if not available_eqs:
    st.warning("⚠️ Please perform technical evaluation for at least one equipment category first.")
    st.stop()

# Equipment Selector
st.markdown("### 🔍 **Select Equipment Category for Commercial Bid Evaluation**")
selected_eq_type = st.selectbox(
    "Equipment Category",
    options=available_eqs,
    index=0 if "Transformer" in available_eqs else 0
)

current_quotes = quotes_dict.get(selected_eq_type, [])
tech_eval_map = tech_scores_dict.get(selected_eq_type, {})

# Commercial Weight Controls
st.markdown("### ⚖️ **Evaluation Model: Multi-Criteria Weights**")
st.caption("Adjust weight parameters for commercial bid conditioning. Total weights automatically normalize to 100%.")

w_c1, w_c2, w_c3, w_c4, w_c5 = st.columns(5)
with w_c1:
    w_price = st.slider("Price Weight (%)", 0, 100, 40, key=f"w_price_{selected_eq_type}")
with w_c2:
    w_tech = st.slider("Technical Weight (%)", 0, 100, 30, key=f"w_tech_{selected_eq_type}")
with w_c3:
    w_deliv = st.slider("Delivery Weight (%)", 0, 100, 15, key=f"w_deliv_{selected_eq_type}")
with w_c4:
    w_qual = st.slider("Quality Weight (%)", 0, 100, 10, key=f"w_qual_{selected_eq_type}")
with w_c5:
    w_warr = st.slider("Warranty Weight (%)", 0, 100, 5, key=f"w_warr_{selected_eq_type}")

weights_dict = {
    "price": w_price,
    "technical": w_tech,
    "delivery": w_deliv,
    "quality": w_qual,
    "warranty": w_warr
}

# Formula Explanation Expander
with st.expander("ℹ️ **How is the Commercial Score calculated? (Transparent Formulas)**"):
    st.markdown(
        """
        - **Price Score** = `100 × (Lowest Quoted Price / Supplier Quoted Price)` *(Lower price is better)*
        - **Delivery Score** = `100 × (Fastest Delivery Weeks / Supplier Delivery Weeks)` *(Shorter delivery is better)*
        - **Technical Score** = `Score verified in Step 5 (Base 100, -40 for critical spec mismatch)`
        - **Quality Score** = `Supplier Track Record & Quality Rating (0–100)`
        - **Warranty Score** = `100 × (Supplier Warranty Years / Longest Warranty Offered)`
        - **Overall Score** = `(Price Score × W_price) + (Tech Score × W_tech) + (Deliv Score × W_deliv) + (Qual Score × W_qual) + (Warr Score × W_warr)`
        """
    )

st.markdown("---")

# Compute commercial scores and rankings
evaluated_quotes = compute_commercial_scores(current_quotes, weights_dict, tech_eval_map)
ranked_quotes, lowest_price_sup, best_overall_sup = rank_suppliers(evaluated_quotes)

# Save to session_state
if not st.session_state.get("commercial_scores") or not isinstance(st.session_state.commercial_scores, dict):
    st.session_state.commercial_scores = {}

st.session_state.commercial_scores[selected_eq_type] = {
    "ranked_quotes": ranked_quotes,
    "lowest_price_supplier": lowest_price_sup,
    "best_overall_supplier": best_overall_sup,
    "weights_used": weights_dict
}

# SECTION: Key Procurement Insight Callouts (Lowest Price vs Best Overall)
st.markdown("### 🏆 **Commercial Bid Insights**")

col_callout1, col_callout2 = st.columns(2)

with col_callout1:
    st.markdown(
        f"""
        <div class="gs-card" style="border-left: 5px solid #F9A825;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #B78103; text-transform: uppercase;">💰 Lowest Quoted Price</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #0B2545; margin: 0.25rem 0;">{lowest_price_sup.get('supplier_name', '—')} — ₹{lowest_price_sup.get('unit_price_inr_lakh', 0):.2f} lakh</div>
            <div style="font-size: 0.85rem; color: #64748B;">
                Status: <strong>{lowest_price_sup.get('status', '—')}</strong><br>
                Overall Score: <strong>{lowest_price_sup.get('overall_score', 0):.1f} / 100</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if lowest_price_sup.get("has_critical_mismatch"):
        st.warning(f"⚠️ **Key Insight:** {lowest_price_sup.get('supplier_name')} offers the lowest price but is **technically disqualified** due to non-compliant specifications.")

with col_callout2:
    st.markdown(
        f"""
        <div class="gs-card" style="border-left: 5px solid #2E7D32;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #2E7D32; text-transform: uppercase;">⭐ Best Overall Recommendation</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #0B2545; margin: 0.25rem 0;">{best_overall_sup.get('supplier_name', '—')} — Overall Score: {best_overall_sup.get('overall_score', 0):.1f}</div>
            <div style="font-size: 0.85rem; color: #64748B;">
                Quoted Price: <strong>₹{best_overall_sup.get('unit_price_inr_lakh', 0):.2f} lakh</strong><br>
                Technical Score: <strong>{best_overall_sup.get('technical_score', 0):.1f}</strong> | Delivery: <strong>{best_overall_sup.get('delivery_weeks', 0)} wks</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.success(f"✅ **Procurement Recommendation:** {best_overall_sup.get('supplier_name')} balances technical compliance, lead time, warranty, and price.")

st.markdown("---")

# Commercial Evaluation Matrix Table
st.markdown("### 📊 **Commercial Comparison Matrix**")

table_rows = []
for r in ranked_quotes:
    table_rows.append({
        "Rank": f"#{r['rank']}",
        "Supplier": r["supplier_name"],
        "Quoted Price": f"₹{r['unit_price_inr_lakh']:.2f} lakh",
        "Price Score": f"{r['price_score']:.1f}",
        "Technical Score": f"{r['technical_score']:.1f}",
        "Delivery Score": f"{r['delivery_score']:.1f} ({r['delivery_weeks']}w)",
        "Quality Score": f"{r['quality_score']:.1f}",
        "Warranty Score": f"{r['warranty_score']:.1f} ({r['warranty_years']}y)",
        "Overall Score": f"{r['overall_score']:.1f}",
        "Status": r["status"]
    })

df_comm = pd.DataFrame(table_rows)
st.dataframe(df_comm, use_container_width=True, hide_index=True)

st.caption(f"<span class='demo-tag'>{DEMO_DATA_LABEL}</span>", unsafe_allow_html=True)

st.markdown("---")

# Visualizations: Bar Chart & Radar Chart
st.markdown("### 📈 **Visual Techno-Commercial Analysis**")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("##### **1. Price Comparison (₹ Lakh)**")
    # Bar chart of prices
    df_plot = pd.DataFrame(ranked_quotes)
    colors = ["#2E7D32" if x["is_qualified"] and x["supplier_name"] == best_overall_sup["supplier_name"] else ("#C62828" if not x["is_qualified"] else "#1B4965") for x in ranked_quotes]
    
    fig_bar = go.Figure(data=[
        go.Bar(
            x=df_plot["supplier_name"],
            y=df_plot["unit_price_inr_lakh"],
            text=[f"₹{v:.2f}L" for v in df_plot["unit_price_inr_lakh"]],
            textposition="auto",
            marker_color=colors
        )
    ])
    fig_bar.update_layout(
        title=f"Quoted Unit Prices — {selected_eq_type}",
        xaxis_title="Supplier",
        yaxis_title="Price (₹ Lakh)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=360,
        plot_bgcolor="#FAFAFA"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.markdown("##### **2. Multi-Criteria Evaluation Radar**")
    # Radar chart
    categories = ["Price", "Technical", "Delivery", "Quality", "Warranty"]
    fig_radar = go.Figure()

    palette = ["#1B4965", "#C62828", "#5FA8D3", "#F9A825", "#2E7D32"]
    for idx, r in enumerate(ranked_quotes):
        values = [
            r["price_score"],
            r["technical_score"],
            r["delivery_score"],
            r["quality_score"],
            r["warranty_score"]
        ]
        # Close the loop
        values.append(values[0])
        radar_cats = categories + [categories[0]]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=radar_cats,
            fill='toself',
            name=f"{r['supplier_name']} ({'Mismatched' if r['has_critical_mismatch'] else 'Qualified'})",
            line_color=palette[idx % len(palette)],
            opacity=0.6
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        margin=dict(l=20, r=20, t=40, b=20),
        height=360
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# Navigation
col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    if st.button("⬅️ Back to Technical Evaluation", use_container_width=True):
        st.switch_page("pages/05_Technical_Evaluation.py")
with col_nav2:
    if st.button("➡️ Proceed to Negotiation Simulator", type="primary", use_container_width=True):
        st.switch_page("pages/07_Negotiation.py")
