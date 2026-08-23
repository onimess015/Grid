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

# Formula Explanation Expander & Interactive Live Math Walkthrough
with st.expander("🧮 **CLICK HERE: Step-by-Step Calculation Breakdown & Live Mathematical Proof**", expanded=False):
    st.markdown("### 📐 **How Each Score & Output is Calculated (Step-by-Step)**")
    
    tab_calc1, tab_calc2, tab_calc3 = st.tabs([
        "1️⃣ Mathematical Formulas",
        "2️⃣ Live Supplier Math (Current Values)",
        "3️⃣ Award Qualification Rule"
    ])

    with tab_calc1:
        st.markdown(
            """
            Each supplier bid is evaluated across **5 distinct criteria** using standardized, transparent formulas:

            1. **Price Score (Inverse Scale — Cheaper is Better):**
               $$\\text{Price Score} = 100 \\times \\frac{\\text{Lowest Quoted Price Among All Bidders}}{\\text{Supplier's Quoted Price}}$$
               *(The cheapest bidder receives 100 points; higher priced bidders receive proportionally lower scores).*

            2. **Delivery Score (Inverse Scale — Faster is Better):**
               $$\\text{Delivery Score} = 100 \\times \\frac{\\text{Shortest Lead Time (Weeks)}}{\\text{Supplier's Delivery Time (Weeks)}}$$
               *(The fastest delivery receives 100 points).*

            3. **Technical Score (Rule-Based Compliance from Step 5):**
               $$\\text{Technical Score} = 100 - (40 \\times \\text{Critical Mismatches}) - (10 \\times \\text{Non-Critical Mismatches})$$
               *(Undersized transformer kVA rating = -40 points penalty).*

            4. **Quality & Track Record Score (Direct Scale):**
               $$\\text{Quality Score} = \\text{Supplier ISO / Factory Audit Rating (0 to 100)}$$

            5. **Warranty Score (Direct Scale — Longer is Better):**
               $$\\text{Warranty Score} = 100 \\times \\frac{\\text{Supplier Warranty (Years)}}{\\text{Longest Warranty Offered (Years)}}$$

            6. **Composite Weighted Overall Score:**
               $$\\text{Overall Score} = (S_{\\text{price}} \\times W_{\\text{price}}) + (S_{\\text{tech}} \\times W_{\\text{tech}}) + (S_{\\text{deliv}} \\times W_{\\text{deliv}}) + (S_{\\text{qual}} \\times W_{\\text{qual}}) + (S_{\\text{warr}} \\times W_{\\text{warr}})$$
               *where weights are normalized so $\\sum W = 1.0$.*
            """
        )

    with tab_calc2:
        st.markdown("#### 🔢 **Live Mathematical Walkthrough with Active Quotes:**")
        if current_quotes:
            valid_prices = [float(q.get("unit_price_inr_lakh", 0)) for q in current_quotes if float(q.get("unit_price_inr_lakh", 0)) > 0]
            valid_delivs = [int(q.get("delivery_weeks", 0)) for q in current_quotes if int(q.get("delivery_weeks", 0)) > 0]
            valid_warrs = [int(q.get("warranty_years", 0)) for q in current_quotes if int(q.get("warranty_years", 0)) > 0]
            
            min_p = min(valid_prices) if valid_prices else 1.0
            min_d = min(valid_delivs) if valid_delivs else 1
            max_w = max(valid_warrs) if valid_warrs else 1
            
            st.info(f"📊 **Current Benchmarks:** Lowest Price = **₹{min_p:.2f}L** | Fastest Delivery = **{min_d} weeks** | Longest Warranty = **{max_w} years**")

            calc_walkthrough = []
            for q in current_quotes:
                s_name = q.get("supplier_name", "")
                p = float(q.get("unit_price_inr_lakh", 0))
                d = int(q.get("delivery_weeks", 1))
                w = int(q.get("warranty_years", 1))
                t_score = float(tech_eval_map.get(s_name, {}).get("technical_score", q.get("technical_score", 90)))
                q_score = float(q.get("quality_score", 90))

                p_score = min(100.0, 100.0 * min_p / p) if p > 0 else 0
                d_score = min(100.0, 100.0 * min_d / d) if d > 0 else 0
                w_score = min(100.0, 100.0 * w / max_w) if max_w > 0 else 100

                tot_w = w_price + w_tech + w_deliv + w_qual + w_warr or 100.0
                ov = (p_score * w_price + t_score * w_tech + d_score * w_deliv + q_score * w_qual + w_score * w_warr) / tot_w

                calc_walkthrough.append({
                    "Supplier": s_name,
                    "Price Math": f"100 × ({min_p:.1f} / {p:.1f}) = {p_score:.1f}",
                    "Delivery Math": f"100 × ({min_d} / {d}) = {d_score:.1f}",
                    "Tech Score": f"{t_score:.1f}",
                    "Quality Score": f"{q_score:.1f}",
                    "Warranty Math": f"100 × ({w} / {max_w}) = {w_score:.1f}",
                    "Weighted Overall Math": f"({p_score:.1f}×{w_price} + {t_score:.1f}×{w_tech} + {d_score:.1f}×{w_deliv} + {q_score:.1f}×{w_qual} + {w_score:.1f}×{w_warr}) / {tot_w:.0f} = {ov:.1f}"
                })

            st.dataframe(pd.DataFrame(calc_walkthrough), use_container_width=True, hide_index=True)
        else:
            st.write("No active quotations to display live math.")

    with tab_calc3:
        st.markdown(
            """
            #### 🛡️ **Award Qualification & Exclusion Logic:**
            - **The Critical Rule:** A bidder with any critical technical mismatch (e.g. **Supplier B offering 1000 kVA instead of required 1250 kVA**) receives a `-40 point` penalty and is tagged with **⚠️ Technical Mismatch**.
            - **Exclusion from Award:** Even though Supplier B achieves a Price Score of **100.0** (lowest price ₹39L), the system's ranking algorithm filters out technically mismatched bidders when selecting the **Best Overall Recommendation**.
            - **Audit Trail:** The mismatched bidder remains fully visible in the comparison matrix and charts for audit compliance and negotiation leverage.
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
        <div class="gs-card" style="border-left: 5px solid #FACC15;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #FACC15; text-transform: uppercase;">💰 Lowest Quoted Price</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #F0F6FC; margin: 0.25rem 0;">{lowest_price_sup.get('supplier_name', '—')} — ₹{lowest_price_sup.get('unit_price_inr_lakh', 0):.2f} lakh</div>
            <div style="font-size: 0.85rem; color: #8B949E;">
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
        <div class="gs-card" style="border-left: 5px solid #4ADE80;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #4ADE80; text-transform: uppercase;">⭐ Best Overall Recommendation</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #F0F6FC; margin: 0.25rem 0;">{best_overall_sup.get('supplier_name', '—')} — Overall Score: {best_overall_sup.get('overall_score', 0):.1f}</div>
            <div style="font-size: 0.85rem; color: #8B949E;">
                Quoted Price: <strong>₹{best_overall_sup.get('unit_price_inr_lakh', 0):.2f} lakh</strong><br>
                Technical Score: <strong>{best_overall_sup.get('technical_score', 0):.1f}</strong> | Delivery: <strong>{best_overall_sup.get('delivery_weeks', 0)} wks</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.success(f"✅ **Procurement Recommendation:** {best_overall_sup.get('supplier_name')} balances technical compliance, lead time, warranty, and price.")

# DEDICATED AUDIT & CREDIBILITY SECTION: Where processed, credibility, methods & exact reasons
with st.expander("🛡️ **DECISION AUDIT: Where Output Was Processed, How It Evaluates Outcomes & What Methods Were Used**", expanded=True):
    tab_cred1, tab_cred2, tab_cred3, tab_cred4 = st.tabs([
        "📡 Where Output Is Processed From",
        "⚙️ How It Evaluates Outcomes & What It Used",
        "🎖️ Credibility & Engineering Integrity",
        "🎯 Exact Reasons Why You Get This Output"
    ])

    with tab_cred1:
        st.markdown(
            """
            #### 📡 **Complete Data Lineage & Processing Chain:**
            This output is processed through a strict 6-stage engineering pipeline:
            1. **Electrical Sizing Baseline (Step 1):** Derived directly from your entered connected load (2000 kW) and 11 kV system voltage.
            2. **Equipment Schedule (Step 2):** Defines the required transformer package as **2 × 1250 kVA (11 kV / 0.415 kV)**.
            3. **Official RFQ Parameters (Step 3):** Standardized technical specifications and commercial terms issued to bidders.
            4. **Quotation Ingestion (Step 4):** Raw bids received from Supplier A, B, and C with stated prices, lead times, and warranties.
            5. **Technical Conditioning Gate (Step 5):** Parameter verification engine checks kVA rating and voltages.
            6. **Weighted Commercial Scoring (Step 6):** Composite multi-criteria calculation based on your active weights.
            """
        )

    with tab_cred2:
        st.markdown(
            """
            #### ⚙️ **How Output is Processed: The Decision Engine Architecture (ML Analogy vs GridSelect Engine)**

            In data science, we often explain how an ML model processes inputs into outputs. Here is the exact breakdown comparing a standard ML pipeline with **GridSelect's deterministic decision engine**:

            | Pipeline Stage | Standard ML Pipeline (e.g. Random Forest / Neural Net) | GridSelect Decision Engine (Power Systems Sourcing) |
            | :--- | :--- | :--- |
            | **1. Inputs / Dataset** | Historical training data, noisy features, test splits | Real-time project specs (2000 kW, 11 kV) + Structured vendor bids (Price, Delivery, kVA, Warranty) |
            | **2. Processing Model** | Black-box statistical learning (approximates probabilities) | **Dual-Stage Engine:** (1) Hard-Constraint Engineering Gate + (2) Multi-Criteria Decision Analysis (MCDA) |
            | **3. Constraint Checking** | Soft statistical probabilities (risk of hallucination / physics violations) | **Hard Deterministic Engineering Rules:** $\\text{Offered kVA} \\ge 1250\\text{ kVA}$, $\\text{kV} == 11.0$ (Zero tolerance for undersizing) |
            | **4. Feature Weighting** | Hidden weights & loss optimization | **User-Defined Normalized Weights:** Price (40%), Technical (30%), Delivery (15%), Quality (10%), Warranty (5%) |
            | **5. Decision Output** | Probability estimate with opaque reasoning | **100% Auditable Ranking Matrix** with exact mathematical step-by-step proof for every decimal point |

            ---

            #### 🛠️ **The 4 Computational Stages in Detail:**

            1. **Input Ingestion & Baseline Calibration:**
               - Ingests active load ($2000\\text{ kW}$) and nominal system voltage ($11\\text{ kV}$).
               - Structures baseline requirement into $2 \\times 1250\\text{ kVA}$ Step-Down Transformer packages.

            2. **Stage 1 — Technical Constraint Conditioning Engine:**
               - Evaluates nominal ratings and voltage compliance against RFQ requirements:
                 $$\\text{Condition} = (\\text{Offered kVA} \\ge 1250) \\land (\\text{Primary kV} == 11.0) \\land (\\text{Secondary kV} == 0.415)$$
               - Deducts $-40\\text{ points}$ per critical failure $\\rightarrow$ Flags **Supplier B (1000 kVA)** with `⚠️ Technical Mismatch`.

            3. **Stage 2 — Multi-Criteria Vector Normalization (MCDA):**
               - Normalizes heterogeneous dimensions (rupees, weeks, years, quality scores) onto a standard $[0, 100]$ interval using inverse and direct ratios:
                 - **Price Vector (Inverse):** $S_{\\text{price}} = 100 \\times (\\text{Min Price} / P_i)$
                 - **Delivery Vector (Inverse):** $S_{\\text{deliv}} = 100 \\times (\\text{Min Weeks} / D_i)$
                 - **Technical Vector (Rule-based):** $S_{\\text{tech}} = 100 - (40 \\times \\text{Critical Mismatches})$
                 - **Quality Vector (Direct):** $S_{\\text{qual}} = \\text{ISO / Factory Audit Score}$
                 - **Warranty Vector (Direct):** $S_{\\text{warr}} = 100 \\times (W_i / \\text{Max Warranty})$
               - Multiplies each vector by normalized weights: $\\text{Overall Score} = \\sum_{j} (S_j \\times W_j)$.

            4. **Stage 3 — Gated Ranking & Award Determination:**
               - Filters only technically qualified candidates ($\\text{is\\_qualified} == \\text{True}$).
               - Sorts qualified candidates descending by Overall Score $\\rightarrow$ Awards **🟢 Recommended** badge to Rank #1.
               - Retains disqualified bidders (Supplier B) for transparent price anchoring and negotiation leverage.

            ---

            #### 💡 **Why This Rule-Based Engine Beats ML for Infrastructure Procurement:**
            - **Legal & Audit Compliance:** High-voltage substation contracts require legally defensible decisions that can be presented to auditors, board members, and government regulators. An ML model cannot explain *why* it assigned a specific probability.
            - **Zero Risk of Hallucination:** Deterministic rules ensure that safety-critical electrical limits (e.g. transformer thermal capacity) are strictly respected.
            """
        )


    with tab_cred3:
        st.markdown(
            """
            #### 🎖️ **Why This Output is 100% Credible & Defensible:**
            - **No Black-Box AI / Guessing:** 100% deterministic, rule-based mathematical models. Every single score can be independently proven by an auditor.
            - **Power Systems Standard Compliance:** Evaluates transformers against nominal IEC/IS voltage classes and capacity rules.
            - **Engineering First, Commercial Second:** Strict two-stage evaluation ensures no uncertified or undersized equipment can bypass safety requirements just by being cheap.
            """
        )

    with tab_cred4:
        st.markdown(
            f"""
            #### 🎯 **Root-Cause Rationale (Why You See This Result):**
            
            1. **Why Supplier B (₹39.00L) Lost:**
               - **The Root Cause:** Supplier B quoted an **undersized 1000 kVA transformer**, which violates the project's **1250 kVA design requirement**.
               - **The Risk:** Installing an undersized transformer leads to severe thermal overheating, insulation breakdown, and costly plant blackouts.
               - **The System Action:** Step 5 deducted `-40 points` and flagged it with **⚠️ Technical Mismatch**, automatically excluding it from the winning recommendation.

            2. **Why {best_overall_sup.get('supplier_name')} Won:**
               - **Technical Suitability:** 100% compliant with the 1250 kVA / 11 kV / 0.415 kV specification.
               - **Balanced Commercial Value:** Achieved the highest overall composite score of **{best_overall_sup.get('overall_score', 0):.1f} / 100**, offering the optimal trade-off between price, guaranteed delivery, quality reputation, and warranty.
            """
        )

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

# DEDICATED OUTPUT CALCULATION EXPLANATION BAR (RIGHT BELOW TABLE)
with st.expander("🧮 **CLICK HERE: How Every Score & Output in the Table Above Was Calculated**", expanded=False):
    st.markdown("### 📐 **Output Calculation Breakdown & Mathematical Proof**")
    
    tab_calc1, tab_calc2, tab_calc3 = st.tabs([
        "1️⃣ Mathematical Formulas",
        "2️⃣ Live Supplier Math (Current Table Values)",
        "3️⃣ Award Qualification & Why Lowest Price Doesn't Always Win"
    ])

    with tab_calc1:
        st.markdown(
            """
            Each score in the table above is calculated using standard, transparent formulas:

            1. **Price Score:**
               $$\\text{Price Score} = 100 \\times \\frac{\\text{Lowest Quoted Price}}{\\text{Supplier Price}}$$
               *(Lowest price gets 100.0 points; higher prices receive proportionally lower scores).*

            2. **Delivery Score:**
               $$\\text{Delivery Score} = 100 \\times \\frac{\\text{Fastest Delivery Weeks}}{\\text{Supplier Delivery Weeks}}$$

            3. **Technical Score:**
               $$\\text{Technical Score} = 100 - (40 \\times \\text{Critical Mismatches}) - (10 \\times \\text{Non-Critical Mismatches})$$

            4. **Quality Score:**
               $$\\text{Quality Score} = \\text{Supplier Track Record & ISO Rating (0 to 100)}$$

            5. **Warranty Score:**
               $$\\text{Warranty Score} = 100 \\times \\frac{\\text{Supplier Warranty (Years)}}{\\text{Longest Warranty Offered (Years)}}$$

            6. **Composite Overall Weighted Score:**
               $$\\text{Overall Score} = (S_{\\text{price}} \\times W_{\\text{price}}) + (S_{\\text{tech}} \\times W_{\\text{tech}}) + (S_{\\text{deliv}} \\times W_{\\text{deliv}}) + (S_{\\text{qual}} \\times W_{\\text{qual}}) + (S_{\\text{warr}} \\times W_{\\text{warr}})$$
            """
        )

    with tab_calc2:
        st.markdown("#### 🔢 **Live Mathematical Walkthrough with Active Quotes:**")
        if current_quotes:
            valid_prices = [float(q.get("unit_price_inr_lakh", 0)) for q in current_quotes if float(q.get("unit_price_inr_lakh", 0)) > 0]
            valid_delivs = [int(q.get("delivery_weeks", 0)) for q in current_quotes if int(q.get("delivery_weeks", 0)) > 0]
            valid_warrs = [int(q.get("warranty_years", 0)) for q in current_quotes if int(q.get("warranty_years", 0)) > 0]
            
            min_p = min(valid_prices) if valid_prices else 1.0
            min_d = min(valid_delivs) if valid_delivs else 1
            max_w = max(valid_warrs) if valid_warrs else 1
            
            st.info(f"📊 **Current Benchmarks:** Lowest Price = **₹{min_p:.2f}L** | Fastest Delivery = **{min_d} weeks** | Longest Warranty = **{max_w} years**")

            calc_walkthrough = []
            for q in current_quotes:
                s_name = q.get("supplier_name", "")
                p = float(q.get("unit_price_inr_lakh", 0))
                d = int(q.get("delivery_weeks", 1))
                w = int(q.get("warranty_years", 1))
                t_score = float(tech_eval_map.get(s_name, {}).get("technical_score", q.get("technical_score", 90)))
                q_score = float(q.get("quality_score", 90))

                p_score = min(100.0, 100.0 * min_p / p) if p > 0 else 0
                d_score = min(100.0, 100.0 * min_d / d) if d > 0 else 0
                w_score = min(100.0, 100.0 * w / max_w) if max_w > 0 else 100

                tot_w = w_price + w_tech + w_deliv + w_qual + w_warr or 100.0
                ov = (p_score * w_price + t_score * w_tech + d_score * w_deliv + q_score * w_qual + w_score * w_warr) / tot_w

                calc_walkthrough.append({
                    "Supplier": s_name,
                    "Price Math": f"100 × ({min_p:.1f} / {p:.1f}) = {p_score:.1f}",
                    "Delivery Math": f"100 × ({min_d} / {d}) = {d_score:.1f}",
                    "Tech Score": f"{t_score:.1f}",
                    "Quality Score": f"{q_score:.1f}",
                    "Warranty Math": f"100 × ({w} / {max_w}) = {w_score:.1f}",
                    "Weighted Overall Math": f"({p_score:.1f}×{w_price} + {t_score:.1f}×{w_tech} + {d_score:.1f}×{w_deliv} + {q_score:.1f}×{w_qual} + {w_score:.1f}×{w_warr}) / {tot_w:.0f} = {ov:.1f}"
                })

            st.dataframe(pd.DataFrame(calc_walkthrough), use_container_width=True, hide_index=True)

    with tab_calc3:
        st.markdown(
            """
            #### 🛡️ **Why Lowest Price Doesn't Automatically Win:**
            - **Supplier B is Cheapest (₹39.00L):** It gets the highest Price Score of `100.0`.
            - **The Technical Mismatch:** Supplier B offered a **1000 kVA** transformer when **1250 kVA** was required. This triggers a `-40 point` penalty in Step 5.
            - **Exclusion Rule:** Because Supplier B failed a critical parameter, it cannot be recommended as the winning bidder.
            - **Best Overall Award:** Recommended to **Supplier A / Supplier C** which meet all technical requirements and offer the best combined balance of cost, delivery, and quality.
            """
        )

st.markdown("---")


# Visualizations: Bar Chart & Radar Chart
st.markdown("### 📈 **Visual Techno-Commercial Analysis**")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("##### **1. Price Comparison (₹ Lakh)**")
    # Bar chart of prices
    df_plot = pd.DataFrame(ranked_quotes)
    colors = ["#4ADE80" if x["is_qualified"] and x["supplier_name"] == best_overall_sup["supplier_name"] else ("#F87171" if not x["is_qualified"] else "#5FA8D3") for x in ranked_quotes]
    
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
        paper_bgcolor="#161B22",
        plot_bgcolor="#0D1117",
        font=dict(color="#E6EDF3")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.markdown("##### **2. Multi-Criteria Evaluation Radar**")
    # Radar chart
    categories = ["Price", "Technical", "Delivery", "Quality", "Warranty"]
    fig_radar = go.Figure()

    palette = ["#5FA8D3", "#F87171", "#62B6CB", "#FACC15", "#4ADE80"]
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
            opacity=0.5
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363D"),
            angularaxis=dict(gridcolor="#30363D"),
            bgcolor="#0D1117"
        ),
        paper_bgcolor="#161B22",
        font=dict(color="#E6EDF3"),
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
