"""
evaluation_logic.py
Implements rule-based technical specification verification, technical scoring,
multi-criteria commercial scoring, and transparent supplier ranking.
"""

from typing import List, Dict, Any, Tuple
import re


def _parse_voltage_num(val: Any) -> float:
    """Helper to normalize voltage strings or numbers to kV."""
    if val is None:
        return 0.0
    val_str = str(val).strip().lower()
    # Extract numeric part
    match = re.search(r"[-+]?\d*\.?\d+", val_str)
    if not match:
        return 0.0
    num = float(match.group(0))
    if "v" in val_str and "kv" not in val_str:
        return num / 1000.0  # Convert V to kV
    return num


def compare_specs(required: Dict[str, Any], offered: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compares required equipment specifications against offered supplier values.

    Rules:
    - Rating / Capacity: Critical field. Offered >= Required is acceptable (Match=True).
    - Voltage Class: Critical field. Offered == Required (Match=True).
    """
    eq_type = required.get("equipment_type", "")
    results = []

    if eq_type == "Transformer":
        # 1. Rating (kVA) - Critical
        req_rating = float(required.get("rating_kva", 1250))
        off_rating = float(offered.get("offered_rating_kva", 0) or 0)
        rating_match = off_rating >= req_rating
        results.append({
            "field": "Transformer Rating (kVA)",
            "required": f"{req_rating:.0f} kVA",
            "offered": f"{off_rating:.0f} kVA",
            "match": rating_match,
            "is_critical": True,
            "detail": "Offered capacity meets or exceeds requirement" if rating_match else "Undersized rating (critical mismatch)"
        })

        # 2. Primary Voltage (kV) - Critical
        req_pri = _parse_voltage_num(required.get("primary_voltage", 11.0))
        off_pri = _parse_voltage_num(offered.get("offered_primary_kv", 11.0))
        pri_match = abs(req_pri - off_pri) < 0.01
        results.append({
            "field": "Primary Voltage",
            "required": f"{req_pri:.3g} kV",
            "offered": f"{off_pri:.3g} kV",
            "match": pri_match,
            "is_critical": True,
            "detail": "Voltage level matched" if pri_match else "Primary voltage mismatch"
        })

        # 3. Secondary Voltage (kV) - Critical
        req_sec = _parse_voltage_num(required.get("secondary_voltage", 0.415))
        off_sec = _parse_voltage_num(offered.get("offered_secondary_kv", 0.415))
        sec_match = abs(req_sec - off_sec) < 0.01
        results.append({
            "field": "Secondary Voltage",
            "required": f"{req_sec:.3g} kV ({req_sec*1000:.0f} V)",
            "offered": f"{off_sec:.3g} kV ({off_sec*1000:.0f} V)",
            "match": sec_match,
            "is_critical": True,
            "detail": "Voltage level matched" if sec_match else "Secondary voltage mismatch"
        })

    elif eq_type in ("HT Panel", "LT Panel"):
        req_v = _parse_voltage_num(required.get("voltage", 11.0))
        off_v = _parse_voltage_num(offered.get("offered_primary_kv", 11.0))
        v_match = abs(req_v - off_v) < 0.01
        results.append({
            "field": "System Voltage",
            "required": f"{req_v:.3g} kV",
            "offered": f"{off_v:.3g} kV",
            "match": v_match,
            "is_critical": True,
            "detail": "Voltage class matched" if v_match else "Voltage class mismatch"
        })

    else:
        # Generic spec match
        results.append({
            "field": "Standard Specification",
            "required": "Standard Industry Compliance",
            "offered": "Compliant",
            "match": True,
            "is_critical": False,
            "detail": "Meets general equipment specifications"
        })

    return results


def compute_technical_score(comparison_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates technical score from spec comparisons:
        Starting Score = 100
        Critical mismatch = -40
        Non-critical mismatch = -10
        Minimum score = 0, Maximum = 100
    """
    score = 100.0
    critical_mismatches = 0
    non_critical_mismatches = 0
    mismatch_details = []

    for comp in comparison_results:
        if not comp["match"]:
            if comp["is_critical"]:
                score -= 40.0
                critical_mismatches += 1
                mismatch_details.append(f"Critical: {comp['field']} (Offered: {comp['offered']} vs Req: {comp['required']})")
            else:
                score -= 10.0
                non_critical_mismatches += 1
                mismatch_details.append(f"Non-Critical: {comp['field']}")

    score = max(0.0, min(100.0, score))
    has_critical_mismatch = critical_mismatches > 0
    is_qualified = not has_critical_mismatch and score >= 60.0

    return {
        "technical_score": score,
        "has_critical_mismatch": has_critical_mismatch,
        "critical_mismatches_count": critical_mismatches,
        "non_critical_mismatches_count": non_critical_mismatches,
        "mismatch_details": mismatch_details,
        "is_qualified": is_qualified,
        "status_label": "⚠️ Technical Mismatch" if has_critical_mismatch else ("Qualified" if is_qualified else "Low Score")
    }


def compute_commercial_scores(
    quotes: List[Dict[str, Any]],
    weights: Dict[str, float],
    tech_eval_map: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Computes 5-factor normalized commercial evaluation scores for each supplier.

    Formulas:
        Price Score = 100 × (Lowest Price / Supplier Price)
        Delivery Score = 100 × (Fastest Delivery / Supplier Delivery)
        Technical Score = Page 5 Technical Score
        Quality Score = Supplier Quality Score
        Warranty Score = 100 × (Supplier Warranty / Longest Warranty)

        Overall Score = (
            Price Score × Price Weight +
            Technical Score × Technical Weight +
            Delivery Score × Delivery Weight +
            Quality Score × Quality Weight +
            Warranty Score × Warranty Weight
        )
    """
    if not quotes:
        return []

    # Normalize weights to sum = 1.0
    w_price = float(weights.get("price", 40))
    w_tech = float(weights.get("technical", 30))
    w_deliv = float(weights.get("delivery", 15))
    w_qual = float(weights.get("quality", 10))
    w_warr = float(weights.get("warranty", 5))

    total_weight = w_price + w_tech + w_deliv + w_qual + w_warr
    if total_weight <= 0:
        total_weight = 100.0

    nw_price = w_price / total_weight
    nw_tech = w_tech / total_weight
    nw_deliv = w_deliv / total_weight
    nw_qual = w_qual / total_weight
    nw_warr = w_warr / total_weight

    # Extract benchmarks across all valid quotes
    valid_prices = [float(q.get("unit_price_inr_lakh", 0)) for q in quotes if float(q.get("unit_price_inr_lakh", 0)) > 0]
    valid_deliveries = [int(q.get("delivery_weeks", 0)) for q in quotes if int(q.get("delivery_weeks", 0)) > 0]
    valid_warranties = [int(q.get("warranty_years", 0)) for q in quotes if int(q.get("warranty_years", 0)) > 0]

    min_price = min(valid_prices) if valid_prices else 1.0
    min_delivery = min(valid_deliveries) if valid_deliveries else 1
    max_warranty = max(valid_warranties) if valid_warranties else 1

    results = []

    for q in quotes:
        sup_name = q.get("supplier_name", "")
        price = float(q.get("unit_price_inr_lakh", 0) or 0)
        deliv = int(q.get("delivery_weeks", 0) or 1)
        qual = float(q.get("quality_score", 80) or 80)
        warr = int(q.get("warranty_years", 1) or 1)

        # Technical score from Page 5
        tech_eval = tech_eval_map.get(sup_name, {})
        tech_score = float(tech_eval.get("technical_score", q.get("technical_score", 90)))
        has_critical = bool(tech_eval.get("has_critical_mismatch", False))

        # Price Score (inverse: lower price is better)
        price_score = min(100.0, (100.0 * min_price / price)) if price > 0 else 0.0

        # Delivery Score (inverse: faster delivery is better)
        deliv_score = min(100.0, (100.0 * min_delivery / deliv)) if deliv > 0 else 0.0

        # Quality Score (direct)
        qual_score = min(100.0, max(0.0, qual))

        # Warranty Score (direct: longer is better)
        warr_score = min(100.0, (100.0 * warr / max_warranty)) if max_warranty > 0 else 100.0

        # Overall Weighted Score
        overall = (
            price_score * nw_price +
            tech_score * nw_tech +
            deliv_score * nw_deliv +
            qual_score * nw_qual +
            warr_score * nw_warr
        )
        overall = round(overall, 1)

        status = "⚠️ Technical Mismatch" if has_critical else "Qualified"

        results.append({
            "supplier_name": sup_name,
            "equipment_type": q.get("equipment_type", ""),
            "unit_price_inr_lakh": price,
            "delivery_weeks": deliv,
            "warranty_years": warr,
            "quality_score": qual_score,
            "technical_score": tech_score,
            "price_score": round(price_score, 1),
            "delivery_score": round(deliv_score, 1),
            "warranty_score": round(warr_score, 1),
            "overall_score": overall,
            "has_critical_mismatch": has_critical,
            "is_qualified": not has_critical,
            "status": status,
            "payment_terms": q.get("payment_terms", ""),
            "notes": q.get("notes", "")
        })

    return results


def rank_suppliers(evaluated_quotes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """
    Ranks suppliers adhering to critical procurement principles:
    1. Qualified suppliers first (has_critical_mismatch == False)
    2. Overall score descending
    3. Lowest price supplier is identified separately from Best Overall recommendation.

    Returns:
        (ranked_list, lowest_price_supplier, best_overall_supplier)
    """
    if not evaluated_quotes:
        return [], {}, {}

    # Sort: qualified first (is_qualified True -> 0, False -> 1), then overall_score desc
    sorted_quotes = sorted(
        evaluated_quotes,
        key=lambda x: (not x["is_qualified"], -x["overall_score"])
    )

    # Assign ranks
    for idx, item in enumerate(sorted_quotes, start=1):
        item["rank"] = idx

    # Find lowest price overall among all suppliers
    lowest_price_sup = min(evaluated_quotes, key=lambda x: x["unit_price_inr_lakh"])

    # Find best overall among QUALIFIED suppliers only
    qualified_suppliers = [s for s in sorted_quotes if s["is_qualified"]]
    best_overall_sup = qualified_suppliers[0] if qualified_suppliers else sorted_quotes[0]

    # Tag status on best overall
    for item in sorted_quotes:
        if item["supplier_name"] == best_overall_sup["supplier_name"] and item["is_qualified"]:
            item["status"] = "🟢 Recommended"

    return sorted_quotes, lowest_price_sup, best_overall_sup
