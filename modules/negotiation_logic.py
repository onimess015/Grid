"""
negotiation_logic.py
Handles price negotiation simulation, recalculation of commercial scores,
and transparent before-and-after ranking analysis.
"""

from typing import List, Dict, Any, Tuple
import copy
from .evaluation_logic import compute_commercial_scores, rank_suppliers


def apply_discount(original_price: float, discount_percent: float) -> Dict[str, float]:
    """
    Applies discount percentage to original price and computes savings.

    Formula:
        Negotiated Price = Original Price × (1 − Discount / 100)
        Savings = Original Price − Negotiated Price
    """
    orig = float(original_price)
    disc = max(0.0, min(100.0, float(discount_percent)))
    negotiated = round(orig * (1.0 - disc / 100.0), 2)
    savings = round(orig - negotiated, 2)

    return {
        "original_price": orig,
        "discount_percent": disc,
        "negotiated_price": negotiated,
        "savings": savings,
        "savings_percent": disc
    }


def recompute_ranking_after_negotiation(
    original_ranked_quotes: List[Dict[str, Any]],
    target_supplier_name: str,
    discount_percent: float,
    justification: str,
    weights: Dict[str, float],
    tech_eval_map: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Simulates price negotiation for target supplier without destroying original quote data.
    Recalculates price score, overall score, and tracks rank movements.
    """
    if not original_ranked_quotes:
        return {}

    # Store previous rank lookup
    old_rank_map = {item["supplier_name"]: item.get("rank", idx + 1) for idx, item in enumerate(original_ranked_quotes)}

    # Create non-destructive deep copy
    negotiated_quotes_input = []
    target_orig_price = 0.0
    target_negotiated_price = 0.0
    target_savings = 0.0

    for q in original_ranked_quotes:
        q_copy = copy.deepcopy(q)
        if q_copy["supplier_name"] == target_supplier_name:
            target_orig_price = float(q_copy.get("unit_price_inr_lakh", 0))
            calc = apply_discount(target_orig_price, discount_percent)
            q_copy["unit_price_inr_lakh"] = calc["negotiated_price"]
            target_negotiated_price = calc["negotiated_price"]
            target_savings = calc["savings"]
        negotiated_quotes_input.append(q_copy)

    # Recompute commercial scores and re-rank
    recomputed = compute_commercial_scores(negotiated_quotes_input, weights, tech_eval_map)
    new_ranked, new_lowest, new_best = rank_suppliers(recomputed)

    # Compute rank movements
    rank_changes = {}
    for item in new_ranked:
        s_name = item["supplier_name"]
        old_r = old_rank_map.get(s_name, item["rank"])
        new_r = item["rank"]
        if old_r > new_r:
            delta_str = f"#{old_r} → #{new_r} 🟢 (+{old_r - new_r})"
        elif old_r < new_r:
            delta_str = f"#{old_r} → #{new_r} 🔴 (-{new_r - old_r})"
        else:
            delta_str = f"#{new_r} (Unchanged)"

        rank_changes[s_name] = {
            "old_rank": old_r,
            "new_rank": new_r,
            "delta_str": delta_str
        }

    return {
        "target_supplier": target_supplier_name,
        "original_price": target_orig_price,
        "negotiated_price": target_negotiated_price,
        "discount_percent": float(discount_percent),
        "savings": target_savings,
        "justification": justification,
        "old_ranked_quotes": original_ranked_quotes,
        "new_ranked_quotes": new_ranked,
        "new_lowest_price_supplier": new_lowest,
        "new_best_overall_supplier": new_best,
        "rank_changes": rank_changes
    }
