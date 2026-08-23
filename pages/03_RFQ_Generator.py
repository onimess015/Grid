"""
03_RFQ_Generator.py
Step 3: Generate a formal Request for Quotation (RFQ) document with technical schedules,
commercial bidding conditions, and downloadable Markdown export.
"""

import streamlit as st
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
    init_session_state
)

st.set_page_config(
    page_title="Step 3: RFQ Generator — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="3. RFQ Generator",
    subtitle="Generate a structured Request for Quotation from the project equipment requirements."
)

# Page Guard: Requires Step 2
if not check_page_guard("equipment_requirements", "pages/02_Equipment_Requirement.py", "Equipment Requirement"):
    st.stop()

proj = st.session_state.get("project_details", {})
eq_list = st.session_state.get("equipment_requirements", [])

# Dynamic RFQ Metadata
seq = st.session_state.get("rfq_sequence", 1)
current_year = datetime.datetime.now().year
rfq_number = f"RFQ-{current_year}-{seq:03d}"
issue_date = datetime.date.today().strftime("%d %B %Y")
delivery_weeks = proj.get("delivery_weeks", 8)
project_name = proj.get("project_name", "ABC Manufacturing Plant")
project_loc = proj.get("project_location", "Industrial Hub")

# Build Markdown Content for RFQ
md_lines = [
    f"# REQUEST FOR QUOTATION (RFQ)",
    f"**Document Reference:** `{rfq_number}`  ",
    f"**Project Name:** {project_name}  ",
    f"**Location:** {project_loc}  ",
    f"**Issue Date:** {issue_date}  ",
    f"**Required Delivery Timeline:** Within **{delivery_weeks} weeks** from PO award  ",
    f"**Submission Validity:** 60 calendar days  ",
    "",
    "---",
    "",
    "## 1. PROJECT SCOPE & TECHNICAL REQUIREMENTS",
    "Bidders are requested to furnish competitive techno-commercial bids for the supply of electrical equipment packages listed below. All equipment must comply with relevant Indian/International Electrotechnical Commission (IS/IEC) standards.",
    ""
]

for idx, item in enumerate(eq_list, start=1):
    eq_type = item.get("equipment_type", "Equipment")
    eq_id = item.get("equipment_id", f"EQ-{idx:03d}")
    qty = item.get("quantity", 1)
    
    md_lines.append(f"### Item {idx}: {eq_id} — {eq_type}")
    md_lines.append(f"- **Quantity Required:** {qty} Units")
    
    if eq_type == "Transformer":
        md_lines.append(f"- **Rated Capacity:** {item.get('rating_kva', 1250)} kVA")
        md_lines.append(f"- **Primary / Incomer Voltage:** {item.get('primary_voltage', '11 kV')}")
        md_lines.append(f"- **Secondary / Utilization Voltage:** {item.get('secondary_voltage', '0.415 kV')}")
        md_lines.append(f"- **Vector Group & Cooling:** Dyn11 / ONAN (Standard)")
    elif eq_type in ("HT Panel", "LT Panel"):
        md_lines.append(f"- **Operating Voltage Class:** {item.get('voltage', '11 kV')}")
        md_lines.append(f"- **Configured Feeders:** {item.get('feeders', 8)} circuits")
        md_lines.append(f"- **Enclosure Class:** IP54 / Form 4b execution")
    elif eq_type == "Circuit Breaker":
        md_lines.append(f"- **Breaker Category:** {item.get('type', 'ACB')}")
        md_lines.append(f"- **Rated Voltage:** {item.get('rated_voltage', '415 V')}")
        md_lines.append(f"- **Trip Mechanism:** Microprocessor based LSIG protection")
    elif eq_type == "Cable":
        md_lines.append(f"- **Voltage Grade:** {item.get('voltage_level', '11 kV')}")
        md_lines.append(f"- **Length:** {item.get('length_m', 500)} metres")
        md_lines.append(f"- **Conductor / Insulation:** Aluminium / Copper conductor, XLPE insulated, armoured")
    elif eq_type == "CT/PT":
        md_lines.append(f"- **Application:** {item.get('application', 'Metering & Protection')}")
    elif eq_type == "Isolator":
        md_lines.append(f"- **Operating Voltage:** {item.get('voltage_level', '11 kV')}")
    else:
        md_lines.append(f"- **Specification:** {item.get('description', '')}")

    md_lines.append("")

md_lines.extend([
    "---",
    "",
    "## 2. COMMERCIAL & BIDDING CONDITIONS",
    "Bidders must explicitly confirm and provide the following commercial information:",
    "1. **Itemized Unit Price & Total Price:** Ex-works price quoted in INR Lakhs.",
    "2. **Delivery Schedule:** Firm delivery lead time in weeks from receipt of technically clear Purchase Order.",
    "3. **Warranty Terms:** Comprehensive warranty period (minimum 12–60 months).",
    "4. **Quality Certifications:** ISO 9001 compliance, Type Test certificates from accredited labs (CPRI/ERDA/KEMA).",
    "5. **Payment Terms:** Stated milestone payment terms (e.g. advance vs dispatch/handover).",
    "6. **Quotation Validity:** Minimum 60 days.",
    "7. **Applicable Taxes & Duties:** Explicit mention of GST (18%) and freight terms (FOR site).",
    "",
    "---",
    "",
    "> *Disclaimer: Educational prototype generated document. Hypothetical RFQ for academic and demonstration purposes only.*"
])

rfq_markdown_text = "\n".join(md_lines)

# Display Document Card Preview
st.markdown("### 📄 **Document Preview: Official RFQ**")

with st.container():
    st.markdown(f"#### ⚡ **REQUEST FOR QUOTATION: {rfq_number}**")
    
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.write(f"**Project:** {project_name}")
        st.write(f"**Location:** {project_loc}")
    with col_h2:
        st.write(f"**Issue Date:** {issue_date}")
        st.write(f"**Validity:** 60 Days")
    with col_h3:
        st.write(f"**Required Delivery:** {delivery_weeks} Weeks")
        st.write(f"**Items in Scope:** {len(eq_list)} Packages")

    st.markdown("---")
    
    # Technical requirements summary table
    st.markdown("##### **Technical Requirements Summary**")
    for idx, item in enumerate(eq_list, start=1):
        st.markdown(f"- **Item {idx} ({item.get('equipment_id')}):** {item.get('description', item.get('equipment_type'))} — **Qty: {item.get('quantity')}**")

    st.markdown("---")
    st.markdown("##### **Commercial & Submission Requirements**")
    st.info(
        "Suppliers are required to submit: Unit Price (₹ Lakh), Guaranteed Delivery Time (Weeks), "
        "Comprehensive Warranty (Years), Quality Certifications, and Milestone Payment Terms."
    )

st.markdown("---")

# RFQ Actions
col_act1, col_act2 = st.columns([1, 1])

with col_act1:
    if st.button("📋 Save & Lock RFQ Details", type="primary", use_container_width=True):
        st.session_state.rfq_details = {
            "rfq_number": rfq_number,
            "project_name": project_name,
            "issue_date": issue_date,
            "delivery_weeks": delivery_weeks,
            "items_count": len(eq_list),
            "raw_text": rfq_markdown_text
        }
        st.success(f"✅ RFQ `{rfq_number}` saved to session state.")

with col_act2:
    st.download_button(
        label=f"⬇️ Download RFQ ({rfq_number}.md)",
        data=rfq_markdown_text,
        file_name=f"{rfq_number}.md",
        mime="text/markdown",
        use_container_width=True
    )

st.markdown("---")

# Navigation
col_n1, col_n2 = st.columns([1, 1])
with col_n1:
    if st.button("⬅️ Back to Equipment Requirement", use_container_width=True):
        st.switch_page("pages/02_Equipment_Requirement.py")
with col_n2:
    if st.button("➡️ Proceed to Supplier Quotations", type="primary", use_container_width=True):
        # Auto-save RFQ if not saved yet
        if not st.session_state.get("rfq_details"):
            st.session_state.rfq_details = {
                "rfq_number": rfq_number,
                "project_name": project_name,
                "issue_date": issue_date,
                "delivery_weeks": delivery_weeks,
                "items_count": len(eq_list),
                "raw_text": rfq_markdown_text
            }
        st.switch_page("pages/04_Supplier_Quotations.py")
