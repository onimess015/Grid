"""
quotation_logic.py
Handles loading of demo supplier data, validation of manual quotations,
and price calculations.
"""

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd


def get_data_dir() -> Path:
    """Returns absolute path to the data directory."""
    return Path(__file__).resolve().parent.parent / "data"


def load_demo_suppliers() -> List[Dict[str, Any]]:
    """
    Loads hypothetical supplier quotations from CSV.
    Uses fallback default list if CSV cannot be located.
    """
    csv_path = get_data_dir() / "demo_suppliers.csv"
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            # Fill NaN values with defaults
            df = df.fillna({
                "unit_price_inr_lakh": 0.0,
                "delivery_weeks": 8,
                "technical_score": 90,
                "quality_score": 90,
                "warranty_years": 3,
                "payment_terms": "Standard Commercial Terms",
                "offered_rating_kva": 0.0,
                "offered_primary_kv": 11.0,
                "offered_secondary_kv": 0.415,
                "notes": ""
            })
            return df.to_dict(orient="records")
        except Exception:
            pass

    # Fallback demo data
    return [
        {
            "supplier_name": "Supplier A",
            "equipment_type": "Transformer",
            "unit_price_inr_lakh": 42.0,
            "delivery_weeks": 8,
            "technical_score": 92,
            "quality_score": 94,
            "warranty_years": 5,
            "payment_terms": "30% advance - 70% on delivery",
            "offered_rating_kva": 1250.0,
            "offered_primary_kv": 11.0,
            "offered_secondary_kv": 0.415,
            "notes": "Tier-1 manufacturer meeting full spec"
        },
        {
            "supplier_name": "Supplier B",
            "equipment_type": "Transformer",
            "unit_price_inr_lakh": 39.0,
            "delivery_weeks": 12,
            "technical_score": 88,
            "quality_score": 85,
            "warranty_years": 3,
            "payment_terms": "50% advance - 50% on delivery",
            "offered_rating_kva": 1000.0,
            "offered_primary_kv": 11.0,
            "offered_secondary_kv": 0.415,
            "notes": "Lowest price but undersized rating (1000 kVA vs 1250 kVA required)"
        },
        {
            "supplier_name": "Supplier C",
            "equipment_type": "Transformer",
            "unit_price_inr_lakh": 45.0,
            "delivery_weeks": 6,
            "technical_score": 95,
            "quality_score": 96,
            "warranty_years": 5,
            "payment_terms": "100% advance",
            "offered_rating_kva": 1250.0,
            "offered_primary_kv": 11.0,
            "offered_secondary_kv": 0.415,
            "notes": "Premium offering with shortest delivery and highest quality"
        }
    ]


def validate_quote(quote_data: Dict[str, Any]) -> List[str]:
    """
    Validates supplier quotation entry.
    Returns list of human-readable error messages (empty list if valid).
    """
    errors = []

    supplier_name = str(quote_data.get("supplier_name", "")).strip()
    if not supplier_name:
        errors.append("Supplier name is required.")

    price = float(quote_data.get("unit_price_inr_lakh", 0.0) or 0.0)
    if price <= 0:
        errors.append("Quoted price must be greater than ₹0.00 lakh.")

    delivery = int(quote_data.get("delivery_weeks", 0) or 0)
    if delivery <= 0:
        errors.append("Delivery time must be greater than 0 weeks.")

    warranty = int(quote_data.get("warranty_years", 0) or 0)
    if warranty < 0:
        errors.append("Warranty cannot be negative.")

    quality = float(quote_data.get("quality_score", 0.0) or 0.0)
    if quality < 0 or quality > 100:
        errors.append("Quality score must be between 0 and 100.")

    eq_type = quote_data.get("equipment_type", "")
    if eq_type == "Transformer":
        rating = float(quote_data.get("offered_rating_kva", 0.0) or 0.0)
        if rating <= 0:
            errors.append("Offered transformer rating (kVA) is required and must be > 0.")

    return errors


def calculate_total_price(unit_price: float, quantity: int) -> float:
    """Calculates total line item price from unit price and quantity."""
    return round(float(unit_price) * max(1, int(quantity)), 2)
