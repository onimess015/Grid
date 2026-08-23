"""
02_Equipment_Requirement.py
Step 2: Structure electrical equipment packages into an itemized procurement list
with technical specifications, completeness validation, and educational glossary.
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
    init_session_state
)
from modules.electrical_calculations import EQUIPMENT_GLOSSARY
from modules.equipment_logic import (
    build_equipment_list,
    get_completeness_status,
    generate_equipment_id
)

st.set_page_config(
    page_title="Step 2: Equipment Requirement — GridSelect",
    page_icon="⚡",
    layout="wide"
)

init_session_state()
render_sidebar()

render_page_header(
    title="2. Equipment Requirement",
    subtitle="Convert the project requirement into a structured procurement list."
)

# Page Guard: Requires Step 1
if not check_page_guard("project_details", "pages/01_Project_Requirement.py", "Project Requirement"):
    st.stop()

# Ensure equipment list is populated
if not st.session_state.get("equipment_requirements"):
    st.session_state.equipment_requirements = build_equipment_list(st.session_state.project_details)

eq_list = st.session_state.equipment_requirements

st.markdown("### 📦 **Procurement Equipment Schedule**")
st.caption("Itemized electrical equipment derived from baseline project parameters. Each item receives a traceable ID for RFQ generation.")

# 1. Summary Table
table_rows = []
for item in eq_list:
    eq_type = item.get("equipment_type", "")
    spec = item.get("description", "")
    qty = item.get("quantity", 1)
    
    # Extract voltage representation
    voltage = item.get("voltage", item.get("primary_voltage", item.get("voltage_level", item.get("rated_voltage", "—"))))
    status_raw = item.get("status", get_completeness_status(item))
    
    if status_raw == "complete":
        status_display = "🟢 Complete"
    elif status_raw == "incomplete":
        status_display = "🟡 Incomplete"
    else:
        status_display = "🔴 Missing"

    table_rows.append({
        "Item ID": item.get("equipment_id", "—"),
        "Equipment Category": eq_type,
        "Specification Summary": spec,
        "Quantity": qty,
        "Voltage Class": voltage,
        "Status": status_display
    })

if table_rows:
    df_summary = pd.DataFrame(table_rows)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
else:
    st.warning("No equipment items defined yet. Use the tool below to generate or add items.")

st.markdown("---")

# 2. Detailed Equipment Cards & Glossary
st.markdown("### 🔍 **Item Details & Engineering Glossary**")

for idx, item in enumerate(eq_list):
    eq_id = item.get("equipment_id", f"EQ-{idx+1:03d}")
    eq_type = item.get("equipment_type", "Equipment")
    
    with st.expander(f"📌 **{eq_id} — {eq_type}** ({item.get('description', '')})", expanded=(idx == 0)):
        col_d1, col_d2 = st.columns([3, 2])
        
        with col_d1:
            st.markdown("##### **Technical Parameters**")
            if eq_type == "Transformer":
                st.write(f"- **Rating:** {item.get('rating_kva')} kVA")
                st.write(f"- **Primary Voltage:** {item.get('primary_voltage')}")
                st.write(f"- **Secondary Voltage:** {item.get('secondary_voltage')}")
                st.write(f"- **Quantity:** {item.get('quantity')} Units")
            elif eq_type in ("HT Panel", "LT Panel"):
                st.write(f"- **Operating Voltage:** {item.get('voltage')}")
                st.write(f"- **Outgoing Feeders:** {item.get('feeders')}")
                st.write(f"- **Quantity:** {item.get('quantity')} Panels")
            elif eq_type == "Circuit Breaker":
                st.write(f"- **Breaker Category:** {item.get('type')}")
                st.write(f"- **Rated Voltage:** {item.get('rated_voltage')}")
                st.write(f"- **Quantity:** {item.get('quantity')} Units")
            elif eq_type == "Cable":
                st.write(f"- **Voltage Grade:** {item.get('voltage_level')}")
                st.write(f"- **Total Length:** {item.get('length_m')} metres")
                st.write(f"- **Circuits:** {item.get('quantity')}")
            elif eq_type == "CT/PT":
                st.write(f"- **Application:** {item.get('application')}")
                st.write(f"- **Quantity:** {item.get('quantity')} Sets")
            elif eq_type == "Isolator":
                st.write(f"- **Voltage Level:** {item.get('voltage_level')}")
                st.write(f"- **Quantity:** {item.get('quantity')} Sets")
            else:
                st.write(f"- **Quantity:** {item.get('quantity')}")
                st.write(f"- **Description:** {item.get('description')}")

        with col_d2:
            st.markdown("##### 💡 **Learn More (Engineering Glossary)**")
            glossary_text = EQUIPMENT_GLOSSARY.get(eq_type, "Standard electrical equipment package.")
            st.info(f"**{eq_type}:** {glossary_text}")

        # Remove Item with confirmation
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        col_del_lbl, col_del_btn = st.columns([4, 1])
        with col_del_btn:
            delete_key = f"confirm_del_{eq_id}"
            if st.session_state.get(delete_key, False):
                st.warning("Confirm removal?")
                c_y, c_n = st.columns(2)
                with c_y:
                    if st.button("Yes", key=f"yes_{eq_id}", type="primary"):
                        st.session_state.equipment_requirements = [
                            x for x in st.session_state.equipment_requirements if x.get("equipment_id") != eq_id
                        ]
                        st.session_state[delete_key] = False
                        st.rerun()
                with c_n:
                    if st.button("No", key=f"no_{eq_id}"):
                        st.session_state[delete_key] = False
                        st.rerun()
            else:
                if st.button(f"🗑️ Remove {eq_id}", key=f"btn_del_{eq_id}"):
                    st.session_state[delete_key] = True
                    st.rerun()

st.markdown("---")

# Add Custom Equipment Item Expander
with st.expander("➕ **Add Custom Equipment Item**"):
    with st.form("add_custom_item_form"):
        c_add1, c_add2, c_add3 = st.columns(3)
        with c_add1:
            new_type = st.selectbox(
                "Equipment Type",
                options=["Transformer", "HT Panel", "LT Panel", "Circuit Breaker", "Cable", "CT/PT", "Isolator", "Other"]
            )
        with c_add2:
            new_qty = st.number_input("Quantity", min_value=1, max_value=100, value=1)
        with c_add3:
            new_voltage = st.text_input("Voltage Level", value=st.session_state.project_details.get("system_voltage", "11 kV"))

        new_desc = st.text_input("Specification Description", value="Custom engineered power package")
        
        submitted_add = st.form_submit_button("➕ Add Item to Schedule")
        if submitted_add:
            new_idx = len(st.session_state.equipment_requirements) + 1
            new_item = {
                "equipment_id": generate_equipment_id(new_idx),
                "equipment_type": new_type,
                "quantity": new_qty,
                "voltage": new_voltage,
                "description": new_desc,
                "status": "complete"
            }
            if new_type == "Transformer":
                new_item["rating_kva"] = 1250
                new_item["primary_voltage"] = new_voltage
                new_item["secondary_voltage"] = "0.415 kV"
            st.session_state.equipment_requirements.append(new_item)
            st.success(f"Added {new_item['equipment_id']} to schedule.")
            st.rerun()

st.markdown("---")

# Navigation buttons
col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    if st.button("⬅️ Back to Project Requirement", use_container_width=True):
        st.switch_page("pages/01_Project_Requirement.py")
with col_nav2:
    if st.button("➡️ Proceed to RFQ Generator", type="primary", use_container_width=True):
        st.switch_page("pages/03_RFQ_Generator.py")
