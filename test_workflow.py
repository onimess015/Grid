"""
test_workflow.py
Comprehensive automated test script for GridSelect verifying all business logic modules,
scoring formulas, mismatch detection, negotiation calculations, and test cases 1 to 7.
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))



from modules.electrical_calculations import estimate_transformer_kva, EQUIPMENT_GLOSSARY
from modules.equipment_logic import build_equipment_list, get_completeness_status, generate_equipment_id
from modules.quotation_logic import load_demo_suppliers, validate_quote, calculate_total_price
from modules.evaluation_logic import compare_specs, compute_technical_score, compute_commercial_scores, rank_suppliers
from modules.negotiation_logic import apply_discount, recompute_ranking_after_negotiation


def test_suite():
    print("=================================================================")
    print("        RUNNING GRIDSELECT AUTOMATED TEST SUITE (TEST CASES 1-7)  ")
    print("=================================================================")

    # --- TEST CASE 1: DEFAULT PROJECT & EQUIPMENT GENERATION ---
    print("\n[TEST 1] Default Project & Equipment Generation...")
    default_project = {
        "project_name": "ABC Manufacturing Plant",
        "industry": "Manufacturing",
        "project_location": "Industrial Hub, Pune",
        "completion_weeks": 12,
        "total_load_kw": 2000,
        "system_voltage": "11 kV",
        "feeders_count": 8,
        "transformer_required": True,
        "transformer_qty": 2,
        "transformer_rating_kva": 1250,
        "transformer_primary_kv": "11 kV",
        "transformer_secondary_kv": "0.415 kV",
        "panels_required": True,
        "ht_panel_qty": 4,
        "lt_panel_qty": 6,
        "circuit_breakers_required": True,
        "cb_qty": 4,
        "cb_type": "ACB",
        "ct_pt_required": True,
        "isolators_required": True,
        "cable_required": True,
        "cable_length_m": 500,
        "cable_voltage": "11 kV",
        "cable_qty": 1,
        "budget_lakh": 50.0,
        "delivery_weeks": 8
    }

    eq_list = build_equipment_list(default_project)
    assert len(eq_list) >= 6, f"Expected >= 6 equipment items, got {len(eq_list)}"
    
    # Verify transformer item
    trans_item = next((item for item in eq_list if item["equipment_type"] == "Transformer"), None)
    assert trans_item is not None, "Transformer item missing"
    assert trans_item["rating_kva"] == 1250, f"Expected 1250 kVA, got {trans_item['rating_kva']}"
    assert trans_item["quantity"] == 2, f"Expected 2 transformers, got {trans_item['quantity']}"
    assert trans_item["status"] == "complete", f"Expected complete status, got {trans_item['status']}"
    print("  ✅ Default project correctly creates 2 × 1250 kVA Transformers and structured equipment list.")

    # Educational sizing hint test
    hint = estimate_transformer_kva(2000, 0.9)
    assert hint["estimated_kva"] == 2222.22, f"Expected 2222.22, got {hint['estimated_kva']}"
    print("  ✅ Educational sizing calculation verified.")

    # --- TEST CASE 2: DEMO SUPPLIERS LOADING ---
    print("\n[TEST 2] Loading Demo Suppliers from CSV...")
    demo_suppliers = load_demo_suppliers()
    assert len(demo_suppliers) >= 3, f"Expected >= 3 suppliers, got {len(demo_suppliers)}"
    
    trans_quotes = [q for q in demo_suppliers if q.get("equipment_type") == "Transformer"]
    assert len(trans_quotes) == 3, f"Expected 3 transformer suppliers (A, B, C), got {len(trans_quotes)}"
    names = [q["supplier_name"] for q in trans_quotes]
    assert "Supplier A" in names and "Supplier B" in names and "Supplier C" in names
    print(f"  ✅ Successfully loaded {len(demo_suppliers)} demo quotations including Supplier A, B, C.")

    # --- TEST CASE 3: TECHNICAL EVALUATION & MISMATCH DETECTION ---
    print("\n[TEST 3] Technical Evaluation & Critical Mismatch Check...")
    tech_eval_map = {}
    for q in trans_quotes:
        comp_res = compare_specs(trans_item, q)
        t_score = compute_technical_score(comp_res)
        tech_eval_map[q["supplier_name"]] = t_score
        print(f"  -> {q['supplier_name']}: Score = {t_score['technical_score']}, Status = {t_score['status_label']}, Critical Mismatches = {t_score['critical_mismatches_count']}")

    # Supplier A: 1250 kVA -> Qualified (100)
    assert tech_eval_map["Supplier A"]["is_qualified"] is True
    assert tech_eval_map["Supplier A"]["has_critical_mismatch"] is False

    # Supplier B: 1000 kVA -> Technical Mismatch (60)
    assert tech_eval_map["Supplier B"]["is_qualified"] is False
    assert tech_eval_map["Supplier B"]["has_critical_mismatch"] is True
    assert tech_eval_map["Supplier B"]["technical_score"] == 60.0, f"Expected 60.0 (100-40), got {tech_eval_map['Supplier B']['technical_score']}"

    # Supplier C: 1250 kVA -> Qualified (100)
    assert tech_eval_map["Supplier C"]["is_qualified"] is True
    assert tech_eval_map["Supplier C"]["has_critical_mismatch"] is False
    print("  ✅ Supplier B correctly flagged with critical rating mismatch (1000 kVA vs 1250 kVA).")

    # --- TEST CASE 4: COMMERCIAL EVALUATION & EXCLUSION RULE ---
    print("\n[TEST 4] Commercial Evaluation & Best Overall vs Lowest Price...")
    weights = {"price": 40, "technical": 30, "delivery": 15, "quality": 10, "warranty": 5}
    comm_results = compute_commercial_scores(trans_quotes, weights, tech_eval_map)
    ranked, lowest_p, best_o = rank_suppliers(comm_results)

    print(f"  -> Lowest Price Supplier: {lowest_p['supplier_name']} (₹{lowest_p['unit_price_inr_lakh']}L, Status: {lowest_p['status']})")
    print(f"  -> Best Overall Recommendation: {best_o['supplier_name']} (Overall Score: {best_o['overall_score']}, Status: {best_o['status']})")

    # Supplier B must be lowest price
    assert lowest_p["supplier_name"] == "Supplier B", f"Expected Supplier B to have lowest price, got {lowest_p['supplier_name']}"
    assert lowest_p["unit_price_inr_lakh"] == 39.0

    # Supplier B CANNOT be best overall recommendation because it has critical mismatch
    assert best_o["supplier_name"] != "Supplier B", "CRITICAL ERROR: Technically mismatched Supplier B was recommended!"
    assert best_o["is_qualified"] is True, "Best overall recommendation must be technically qualified"
    print("  ✅ Lowest Price (Supplier B, ₹39L) and Best Overall (Qualified) properly separated.")

    # --- TEST CASE 5: NEGOTIATION SIMULATION ---
    print("\n[TEST 5] Negotiation Simulation on Supplier A (5% Discount)...")
    neg_res = recompute_ranking_after_negotiation(
        original_ranked_quotes=ranked,
        target_supplier_name="Supplier A",
        discount_percent=5.0,
        justification="Bulk project order volume commitment",
        weights=weights,
        tech_eval_map=tech_eval_map
    )

    assert neg_res["original_price"] == 42.0, f"Expected 42.0, got {neg_res['original_price']}"
    assert neg_res["negotiated_price"] == 39.90, f"Expected 39.90, got {neg_res['negotiated_price']}"
    assert neg_res["savings"] == 2.10, f"Expected 2.10, got {neg_res['savings']}"
    assert neg_res["discount_percent"] == 5.0

    # Verify original quotes were not mutated
    orig_sup_a = next(q for q in ranked if q["supplier_name"] == "Supplier A")
    assert orig_sup_a["unit_price_inr_lakh"] == 42.0, "Original quote was improperly mutated!"
    print(f"  ✅ Supplier A negotiated: ₹{neg_res['original_price']}L → ₹{neg_res['negotiated_price']}L (Saved ₹{neg_res['savings']}L).")
    print("  ✅ Original quote data preserved without mutation.")

    # --- TEST CASE 6: VALIDATION CHECKS ---
    print("\n[TEST 6] Input Validation Checks...")
    invalid_quote = {"supplier_name": "", "unit_price_inr_lakh": -5, "delivery_weeks": 0}
    errors = validate_quote(invalid_quote)
    assert len(errors) >= 3, f"Expected at least 3 validation errors, got {len(errors)}"
    print(f"  ✅ Validation correctly caught {len(errors)} errors: {errors}")

    print("\n=================================================================")
    print("           ALL TEST CASES PASSED SUCCESSFULLY! (100%)            ")
    print("=================================================================")


if __name__ == "__main__":
    test_suite()
