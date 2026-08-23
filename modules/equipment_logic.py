"""
equipment_logic.py
Handles conversion of project requirements into structured equipment line items,
validation of equipment completeness, and unique ID generation.
"""

from typing import List, Dict, Any


def generate_equipment_id(index: int) -> str:
    """Generates a standardized equipment identifier (e.g. EQ-001)."""
    return f"EQ-{index:03d}"


def get_completeness_status(item: Dict[str, Any]) -> str:
    """
    Evaluates equipment item completeness.
    Returns:
        'complete'   (🟢 all mandatory specs present and valid)
        'incomplete' (🟡 non-critical specs missing)
        'missing'    (🔴 critical mandatory specs missing or invalid)
    """
    if not isinstance(item, dict):
        return "missing"

    eq_type = item.get("equipment_type", "")
    qty = item.get("quantity", 0)

    if not eq_type or qty <= 0:
        return "missing"

    if eq_type == "Transformer":
        rating = item.get("rating_kva", 0)
        primary = item.get("primary_voltage", "")
        secondary = item.get("secondary_voltage", "")
        if rating <= 0 or not primary or not secondary:
            return "missing"
        return "complete"

    elif eq_type in ("HT Panel", "LT Panel"):
        voltage = item.get("voltage", "")
        feeders = item.get("feeders", 0)
        if not voltage or feeders <= 0:
            return "incomplete"
        return "complete"

    elif eq_type == "Circuit Breaker":
        cb_type = item.get("type", "")
        voltage = item.get("rated_voltage", "")
        if not cb_type or cb_type == "Not decided":
            return "incomplete"
        if not voltage:
            return "missing"
        return "complete"

    elif eq_type == "Cable":
        length = item.get("length_m", 0)
        voltage = item.get("voltage_level", "")
        if length <= 0 or not voltage:
            return "incomplete"
        return "complete"

    elif eq_type == "CT/PT":
        app = item.get("application", "")
        if not app:
            return "incomplete"
        return "complete"

    elif eq_type == "Isolator":
        voltage = item.get("voltage_level", "")
        if not voltage:
            return "incomplete"
        return "complete"

    return "complete"


def build_equipment_list(project_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transforms project details from Section B into a structured list of equipment items.
    Each item is tagged with a unique equipment_id (EQ-001, EQ-002, etc.).
    """
    equipment_list = []
    idx = 1
    system_voltage = project_details.get("system_voltage", "11 kV")

    # 1. Transformer
    if project_details.get("transformer_required", False):
        equipment_list.append({
            "equipment_id": generate_equipment_id(idx),
            "equipment_type": "Transformer",
            "quantity": int(project_details.get("transformer_qty", 2)),
            "rating_kva": float(project_details.get("transformer_rating_kva", 1250)),
            "primary_voltage": str(project_details.get("transformer_primary_kv", "11 kV")),
            "secondary_voltage": str(project_details.get("transformer_secondary_kv", "0.415 kV")),
            "description": f"{project_details.get('transformer_qty', 2)} × {project_details.get('transformer_rating_kva', 1250)} kVA Step-Down Transformer ({project_details.get('transformer_primary_kv', '11 kV')} / {project_details.get('transformer_secondary_kv', '0.415 kV')})"
        })
        idx += 1

    # 2. HT Panel
    if project_details.get("panels_required", False) and project_details.get("ht_panel_qty", 0) > 0:
        equipment_list.append({
            "equipment_id": generate_equipment_id(idx),
            "equipment_type": "HT Panel",
            "quantity": int(project_details.get("ht_panel_qty", 4)),
            "voltage": system_voltage,
            "feeders": int(project_details.get("feeders_count", 8)),
            "description": f"{project_details.get('ht_panel_qty', 4)} Units HT Switchgear Panel ({system_voltage})"
        })
        idx += 1

    # 3. LT Panel
    if project_details.get("panels_required", False) and project_details.get("lt_panel_qty", 0) > 0:
        equipment_list.append({
            "equipment_id": generate_equipment_id(idx),
            "equipment_type": "LT Panel",
            "quantity": int(project_details.get("lt_panel_qty", 6)),
            "voltage": "415 V",
            "feeders": int(project_details.get("feeders_count", 8)),
            "description": f"{project_details.get('lt_panel_qty', 6)} Units LT Power Distribution Panel (415 V)"
        })
        idx += 1

    # 4. Circuit Breakers
    if project_details.get("circuit_breakers_required", False):
        cb_type = project_details.get("cb_type", "ACB")
        cb_qty = int(project_details.get("cb_qty", 4))
        equipment_list.append({
            "equipment_id": generate_equipment_id(idx),
            "equipment_type": "Circuit Breaker",
            "quantity": cb_qty,
            "type": cb_type,
            "rated_voltage": "415 V" if cb_type in ("MCB", "MCCB", "ACB") else system_voltage,
            "description": f"{cb_qty} Units {cb_type} Circuit Breaker"
        })
        idx += 1

    # 5. CT/PT
    if project_details.get("ct_pt_required", False):
        equipment_list.append({
            "equipment_id": generate_equipment_id(idx),
            "equipment_type": "CT/PT",
            "quantity": 2,
            "application": "Metering & Protection",
            "description": f"2 Sets CT/PT Instrument Transformers ({system_voltage})"
        })
        idx += 1

    # 6. Isolators
    if project_details.get("isolators_required", False):
        equipment_list.append({
            "equipment_id": generate_equipment_id(idx),
            "equipment_type": "Isolator",
            "quantity": 2,
            "voltage_level": system_voltage,
            "description": f"2 Sets Air-Break Disconnect Isolators ({system_voltage})"
        })
        idx += 1

    # 7. Cable
    if project_details.get("cable_required", False):
        cable_len = float(project_details.get("cable_length_m", 500))
        cable_v = str(project_details.get("cable_voltage", system_voltage))
        cable_qty = int(project_details.get("cable_qty", 1))
        equipment_list.append({
            "equipment_id": generate_equipment_id(idx),
            "equipment_type": "Cable",
            "quantity": cable_qty,
            "length_m": cable_len,
            "voltage_level": cable_v,
            "description": f"{cable_len} m XLPE Armoured Power Cable ({cable_v})"
        })
        idx += 1

    # Tag each with completeness status
    for item in equipment_list:
        item["status"] = get_completeness_status(item)

    return equipment_list
