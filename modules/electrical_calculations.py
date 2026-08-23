"""
electrical_calculations.py
Contains electrical equipment glossary definitions and educational sizing hints.
"""

EQUIPMENT_GLOSSARY = {
    "Transformer": (
        "A transformer transfers electrical energy between voltage levels using electromagnetic "
        "induction. In power distribution systems, it is commonly used to step voltage up (generation) "
        "or down (substation to utilization voltage)."
    ),
    "HT Panel": (
        "A High Tension (HT) switchgear panel houses medium-to-high voltage switching, protection, "
        "and metering devices (typically 3.3 kV to 33 kV) controlling primary distribution feeders."
    ),
    "LT Panel": (
        "A Low Tension (LT) panel receives stepped-down voltage (e.g. 415 V) from a transformer and "
        "distributes power safely to plant loads, sub-distribution boards, and motor control centres."
    ),
    "MCB": (
        "Miniature Circuit Breaker: A low-voltage thermo-magnetic switching device used for overload and "
        "short-circuit protection in low-current sub-circuits (typically up to 63 A or 100 A)."
    ),
    "MCCB": (
        "Moulded Case Circuit Breaker: A versatile circuit protection device for low-voltage applications "
        "with adjustable trip characteristics, commonly rated from 16 A up to 1600 A."
    ),
    "ACB": (
        "Air Circuit Breaker: A heavy-duty low-voltage breaker operating in air, equipped with "
        "microprocessor-based protection units for main transformer incomers and heavy bus couplers."
    ),
    "VCB": (
        "Vacuum Circuit Breaker: Medium-voltage circuit breaker using a sealed vacuum bottle as the arc "
        "quenching medium, widely deployed in HT panels (3.3 kV to 33 kV) for high reliability."
    ),
    "CT": (
        "Current Transformer: An instrument transformer that steps down high line currents to standardized "
        "safe values (e.g., 1 A or 5 A) for metering instruments and protective relays."
    ),
    "PT": (
        "Potential (Voltage) Transformer: An instrument transformer that steps down high system voltages "
        "to standard secondary levels (e.g., 110 V) for voltage measurement and protection relays."
    ),
    "Isolator": (
        "A mechanical disconnect switch that provides visible electrical isolation of de-energized circuits "
        "during maintenance. Operated only under no-load conditions."
    ),
    "Cable": (
        "Insulated electrical conductors (e.g., XLPE/PVC copper or aluminium) designed to safely transmit "
        "bulk electric power between transformers, switchgear panels, and end-use loads."
    )
}


def estimate_transformer_kva(load_kw: float, pf: float = 0.9) -> dict:
    """
    Computes an educational transformer sizing hint based on total connected load and power factor.

    Formula:
        Estimated kVA = Load (kW) / Power Factor (pf)

    Note:
        Educational sizing hint only — not a certified engineering calculation.
    """
    if pf <= 0 or pf > 1.0:
        pf = 0.9

    if load_kw <= 0:
        return {
            "estimated_kva": 0.0,
            "load_kw": load_kw,
            "pf": pf,
            "formula_str": "Load (kW) / Power Factor",
            "disclaimer": "Educational sizing hint only — not a certified engineering calculation."
        }

    estimated_kva = round(load_kw / pf, 2)
    return {
        "estimated_kva": estimated_kva,
        "load_kw": load_kw,
        "pf": pf,
        "formula_str": f"{load_kw} kW / {pf} pf = {estimated_kva} kVA",
        "disclaimer": "Educational sizing hint only — not a certified engineering calculation."
    }
