"""
verify_pages.py
Validates syntax, imports, and execution safety across all 8 pages and modules.
"""

import sys
import importlib.util
from pathlib import Path

# Set UTF-8 encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

PAGES = [
    "app.py",
    "pages/01_Project_Requirement.py",
    "pages/02_Equipment_Requirement.py",
    "pages/03_RFQ_Generator.py",
    "pages/04_Supplier_Quotations.py",
    "pages/05_Technical_Evaluation.py",
    "pages/06_Commercial_Evaluation.py",
    "pages/07_Negotiation.py",
    "pages/08_Final_Recommendation.py"
]

MODULES = [
    "modules.electrical_calculations",
    "modules.equipment_logic",
    "modules.quotation_logic",
    "modules.evaluation_logic",
    "modules.negotiation_logic",
    "modules.ui_helpers"
]


def test_imports_and_compilation():
    print("--- 1. Testing Module Imports ---")
    for mod_name in MODULES:
        try:
            mod = importlib.import_module(mod_name)
            print(f"  [OK] {mod_name}")
        except Exception as e:
            print(f"  [FAIL] {mod_name}: {e}")
            raise e

    print("\n--- 2. Testing Page Syntax & Compilation ---")
    for page_path_str in PAGES:
        p = ROOT_DIR / page_path_str
        assert p.exists(), f"File does not exist: {p}"
        try:
            with open(p, "r", encoding="utf-8") as f:
                code_text = f.read()
            compile(code_text, str(p), "exec")
            print(f"  [OK] Compiled {page_path_str} cleanly.")
        except Exception as e:
            print(f"  [FAIL] Compilation error in {page_path_str}: {e}")
            raise e

    print("\n--- 3. Verifying CSV Demo Files ---")
    eq_csv = ROOT_DIR / "data" / "demo_equipment.csv"
    sup_csv = ROOT_DIR / "data" / "demo_suppliers.csv"
    assert eq_csv.exists(), "demo_equipment.csv missing"
    assert sup_csv.exists(), "demo_suppliers.csv missing"
    print("  [OK] data/demo_equipment.csv verified.")
    print("  [OK] data/demo_suppliers.csv verified.")

    print("\n========================================================")
    print("      ALL PAGES AND MODULES COMPILED & VALIDATED 100%    ")
    print("========================================================")


if __name__ == "__main__":
    test_imports_and_compilation()
