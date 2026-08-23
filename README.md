# GridSelect ⚡
### Power Systems Equipment & Procurement Decision Platform

---

## 📌 What is GridSelect?

> **GridSelect** is a rule-based Power Systems procurement and supplier-evaluation platform. It takes an electrical project requirement, converts it into an equipment list, generates an RFQ, compares supplier quotations on technical and commercial criteria, simulates negotiation, and produces a transparent procurement recommendation.

---

## 🎯 Why This Project?

This project bridges the gap between **electrical power systems engineering** and **techno-commercial procurement operations**. It simulates the core responsibilities of a Power Systems Graduate Engineer / Sourcing Specialist:

### Technical Engineering Depth
- **Power System Equipment Awareness:** Transformers, HT/LT Switchgear Panels, Circuit Breakers (MCB, MCCB, ACB, VCB), Power Cables, Instrument Transformers (CT/PT), and Air-Break Isolators.
- **Electrical Specification Conditioning:** Rating matching (kVA/kW), Voltage class verification (primary & secondary levels), feeder counts, and protection requirements.
- **Technical Bid Evaluation (TBE):** Automated rule-based compliance checking and detection of critical technical mismatches (e.g. undersized transformers).

### Commercial Sourcing & Procurement Rigor
- **Structured RFQ Generation:** Formal document packaging with technical schedules and commercial bidding terms.
- **Commercial Bid Evaluation (CBE):** Transparent multi-factor weighted scoring across Price, Technical Compliance, Delivery Schedule, Quality Certifications, and Warranty.
- **Value Creation & Negotiation:** Interactive price discount simulator with dynamic rank shift analysis.
- **Explainable Decision Support:** Clear distinction between *Lowest Quoted Price* and *Best Overall Recommendation*.

---

## 🔄 End-to-End Workflow

```
PROJECT REQUIREMENT (01)
        ↓
EQUIPMENT REQUIREMENT (02)
        ↓
RFQ GENERATION (03)
        ↓
SUPPLIER QUOTATIONS (04)
        ↓
TECHNICAL EVALUATION (05)
        ↓
COMMERCIAL EVALUATION (06)
        ↓
NEGOTIATION (07)
        ↓
FINAL RECOMMENDATION (08)
```

---

## 🎙️ Interview Talking Points

### Comprehensive Summary
> *"I built GridSelect to understand the technical-commercial workflow of power-system procurement. The application starts with an electrical project requirement, converts it into a structured equipment requirement, generates an RFQ, compares supplier quotations on technical and commercial criteria, simulates negotiation and produces a final procurement recommendation. I deliberately kept the decision logic rule-based and transparent rather than adding ML because I wanted to understand the actual procurement decision process."*

### Key Concept Elevator Pitch
> *"The key idea is that the cheapest quotation should not automatically win. GridSelect first checks technical suitability and then combines price, delivery, quality and warranty to support a transparent commercial decision."*

### Why No Machine Learning?
> *"Procurement decisions in high-stakes infrastructure must be fully auditable and explainable to project owners, auditors, and engineering teams. I used deterministic rules and transparent weighted scoring models so that any stakeholder can inspect exactly why a specific supplier was recommended without relying on black-box heuristics."*

---

## 🛠️ Technology Stack

- **Core Application:** Python 3.10+
- **Interactive UI Framework:** Streamlit
- **Data Manipulation & Analysis:** Pandas, NumPy
- **Interactive Visualizations:** Plotly (Bar Charts, Radar Charts)
- **Data Storage:** Structured CSV files & Streamlit Session State
- **Document Export:** Markdown (`.md`)

> **Note:** No ML, database, backend, external API, LLM, or internet-dependent services are used. All logic executes locally and deterministically.

---

## 🚀 Quick Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
streamlit run app.py
```
The application will launch locally at `http://localhost:8501`.

---

## 📁 Repository Structure

```
gridselect/
│
├── app.py                             # Landing page, executive KPI metrics, visual workflow
│
├── pages/
│   ├── 01_Project_Requirement.py      # Step 1: Electrical baseline & commercial constraints
│   ├── 02_Equipment_Requirement.py    # Step 2: Structured equipment schedule & glossary
│   ├── 03_RFQ_Generator.py            # Step 3: Formal RFQ generation & Markdown export
│   ├── 04_Supplier_Quotations.py      # Step 4: Demo CSV loader & manual bid ingestion
│   ├── 05_Technical_Evaluation.py     # Step 5: Spec compliance check & mismatch flagging
│   ├── 06_Commercial_Evaluation.py    # Step 6: 5-factor weighted scoring & Plotly visuals
│   ├── 07_Negotiation.py              # Step 7: Price discount simulator & rank recomputation
│   └── 08_Final_Recommendation.py     # Step 8: Executive decision cards & final report export
│
├── modules/
│   ├── __init__.py
│   ├── electrical_calculations.py     # Equipment glossary & sizing hints
│   ├── equipment_logic.py             # Line item generation & status validation
│   ├── evaluation_logic.py            # Technical spec comparisons & commercial scoring
│   ├── quotation_logic.py             # CSV loading & quotation input validation
│   ├── negotiation_logic.py           # Discount math & non-destructive rank updates
│   └── ui_helpers.py                  # Theme styling, page guards, sidebar & disclaimers
│
├── data/
│   ├── demo_equipment.csv             # Catalog equipment metadata
│   └── demo_suppliers.csv             # Hypothetical supplier quotations (A, B, C)
│
├── requirements.txt                   # Minimal required dependencies
├── README.md                          # Project documentation and interview guide
└── .gitignore                         # Python/Streamlit build artifacts
```

---

## ⚠️ Disclaimer

> **Educational prototype only.** Equipment selection, technical specifications, procurement decisions and electrical designs for real installations require qualified engineering review, applicable standards and project-specific validation. Supplier and pricing data in this prototype are hypothetical.
