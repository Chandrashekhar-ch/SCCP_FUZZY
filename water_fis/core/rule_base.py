"""
rule_base.py
============
45-rule Mamdani FIS rule base for water potability classification.
Rules encode WHO/BIS expert knowledge as IF-THEN statements.

Rule Structure:
    {
      "id": int,
      "conditions": {"ph": term, "turbidity": term, "tds": term, "do": term},
      "consequence": WPI_term,
      "weight": float [0,1],
      "rationale": str
    }

Grounding:
  - WHO Guidelines for Drinking-Water Quality, 4th Ed. (2022)
  - BIS IS 10500:2012
  - Mamdani, E.H. (1975). Application of fuzzy algorithms. IEE Proc.

Author: SC_CProject
"""

# Each condition key maps to a linguistic term from membership_functions.py
# A value of None means "any" (that parameter is not constrained in that rule)

RULES = [

    # ══════════════════════════════════════════════════════════════════
    # GROUP 1: FULLY POTABLE (all parameters in safe zone)  → POTABLE
    # ══════════════════════════════════════════════════════════════════
    {
        "id": 1,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "HIGH"},
        "consequence": "POTABLE", "weight": 1.0,
        "rationale": "Ideal drinking water — all parameters in optimal WHO range"
    },
    {
        "id": 2,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "PURE", "do": "HIGH"},
        "consequence": "POTABLE", "weight": 1.0,
        "rationale": "Very pure, well-oxygenated, neutral water"
    },
    {
        "id": 3,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "ACCEPTABLE"},
        "consequence": "POTABLE", "weight": 0.95,
        "rationale": "Good quality water — WHO compliant all parameters"
    },
    {
        "id": 4,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "HIGH"},
        "consequence": "POTABLE", "weight": 0.92,
        "rationale": "Slightly alkaline but all other parameters excellent"
    },
    {
        "id": 5,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "ACCEPTABLE"},
        "consequence": "POTABLE", "weight": 0.90,
        "rationale": "BIS permissible alkalinity, clear and acceptable DO"
    },
    {
        "id": 6,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "PURE", "do": "ACCEPTABLE"},
        "consequence": "POTABLE", "weight": 0.93,
        "rationale": "RO/treated water — very pure, neutral, adequately oxygenated"
    },
    {
        "id": 7,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "HIGH"},
        "consequence": "POTABLE", "weight": 0.88,
        "rationale": "Slightly acidic natural spring water — borderline safe"
    },
    {
        "id": 8,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "CLEAR", "tds": "PURE", "do": "HIGH"},
        "consequence": "POTABLE", "weight": 0.85,
        "rationale": "Mildly acidic, very pure, well-oxygenated (natural spring type)"
    },

    # ══════════════════════════════════════════════════════════════════
    # GROUP 2: HARD NON-POTABILITY TRIGGERS (single-parameter failure)
    # ══════════════════════════════════════════════════════════════════
    {
        "id": 9,
        "conditions": {"ph": "ACIDIC", "turbidity": None, "tds": None, "do": None},
        "consequence": "NON_POTABLE", "weight": 1.0,
        "rationale": "pH < 5.0: corrosive, dissolves metals, WHO critical failure"
    },
    {
        "id": 10,
        "conditions": {"ph": "ALKALINE", "turbidity": None, "tds": None, "do": None},
        "consequence": "NON_POTABLE", "weight": 1.0,
        "rationale": "pH > 9.0: caustic, bitter taste, WHO critical failure"
    },
    {
        "id": 11,
        "conditions": {"ph": None, "turbidity": "VERY_TURBID", "tds": None, "do": None},
        "consequence": "NON_POTABLE", "weight": 1.0,
        "rationale": ">50 NTU: shields pathogens from disinfection — WHO critical"
    },
    {
        "id": 12,
        "conditions": {"ph": None, "turbidity": None, "tds": "VERY_HIGH", "do": None},
        "consequence": "NON_POTABLE", "weight": 1.0,
        "rationale": "TDS >750 mg/L: exceeds BIS permissible, health concern"
    },
    {
        "id": 13,
        "conditions": {"ph": None, "turbidity": None, "tds": None, "do": "VERY_LOW"},
        "consequence": "NON_POTABLE", "weight": 1.0,
        "rationale": "DO <2 mg/L: anaerobic, high microbial contamination risk"
    },

    # ══════════════════════════════════════════════════════════════════
    # GROUP 3: DUAL-PARAMETER FAILURES → NON_POTABLE
    # ══════════════════════════════════════════════════════════════════
    {
        "id": 14,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "TURBID", "tds": "HIGH", "do": None},
        "consequence": "NON_POTABLE", "weight": 0.90,
        "rationale": "Combined pH and turbidity/TDS degradation = unacceptable"
    },
    {
        "id": 15,
        "conditions": {"ph": None, "turbidity": "TURBID", "tds": "HIGH", "do": "LOW"},
        "consequence": "NON_POTABLE", "weight": 0.88,
        "rationale": "Turbid + high TDS + stagnant (low DO) — high contamination risk"
    },
    {
        "id": 16,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": None, "tds": "VERY_HIGH", "do": "LOW"},
        "consequence": "NON_POTABLE", "weight": 0.85,
        "rationale": "Elevated alkalinity with excessive minerals and low oxygen"
    },
    {
        "id": 17,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": None, "tds": "VERY_HIGH", "do": None},
        "consequence": "NON_POTABLE", "weight": 0.88,
        "rationale": "Acidic AND excessive dissolved solids — industrial contamination"
    },

    # ══════════════════════════════════════════════════════════════════
    # GROUP 4: MARGINAL — One parameter slightly out of range
    # ══════════════════════════════════════════════════════════════════
    {
        "id": 18,
        "conditions": {"ph": "NEUTRAL", "turbidity": "SLIGHTLY_TURBID", "tds": "ACCEPTABLE", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.80,
        "rationale": "Good pH/TDS/DO but borderline turbidity — treatment advisable"
    },
    {
        "id": 19,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "HIGH", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.78,
        "rationale": "Excellent pH/clarity but TDS approaching BIS limit"
    },
    {
        "id": 20,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "LOW"},
        "consequence": "MARGINAL", "weight": 0.75,
        "rationale": "Good parameters but low DO suggests stagnation risk"
    },
    {
        "id": 21,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "SLIGHTLY_TURBID", "tds": "ACCEPTABLE", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.72,
        "rationale": "Two parameters at BIS permissible boundary"
    },
    {
        "id": 22,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.70,
        "rationale": "Slightly acidic — acceptable for now but pH correction needed"
    },
    {
        "id": 23,
        "conditions": {"ph": "NEUTRAL", "turbidity": "SLIGHTLY_TURBID", "tds": "HIGH", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.68,
        "rationale": "Good pH but turbidity + TDS both elevated"
    },
    {
        "id": 24,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "CLEAR", "tds": "HIGH", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.72,
        "rationale": "Slightly hard water (high TDS + alkaline) — taste concern"
    },
    {
        "id": 25,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "SLIGHTLY_TURBID", "tds": "ACCEPTABLE", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.65,
        "rationale": "Two borderline values — combined effect pushes to marginal"
    },
    {
        "id": 26,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "HIGH", "do": "HIGH"},
        "consequence": "MARGINAL", "weight": 0.74,
        "rationale": "High TDS only failure — mineralised groundwater"
    },
    {
        "id": 27,
        "conditions": {"ph": "NEUTRAL", "turbidity": "SLIGHTLY_TURBID", "tds": "PURE", "do": "HIGH"},
        "consequence": "MARGINAL", "weight": 0.76,
        "rationale": "Slight turbidity in otherwise excellent water"
    },
    {
        "id": 28,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "CLEAR", "tds": "PURE", "do": "LOW"},
        "consequence": "MARGINAL", "weight": 0.70,
        "rationale": "Pure but stagnant — low DO is the only concern"
    },
    {
        "id": 29,
        "conditions": {"ph": "NEUTRAL", "turbidity": "TURBID", "tds": "ACCEPTABLE", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.62,
        "rationale": "Turbidity is main concern; other params okay"
    },
    {
        "id": 30,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "CLEAR", "tds": "HIGH", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.65,
        "rationale": "Mildly acidic and high TDS — both near-boundary"
    },

    # ══════════════════════════════════════════════════════════════════
    # GROUP 5: TURBID + ACCEPTABLE OTHER → MARGINAL/NON_POTABLE
    # ══════════════════════════════════════════════════════════════════
    {
        "id": 31,
        "conditions": {"ph": "NEUTRAL", "turbidity": "TURBID", "tds": "ACCEPTABLE", "do": "HIGH"},
        "consequence": "MARGINAL", "weight": 0.58,
        "rationale": "Turbid but good chemistry — may be treatable"
    },
    {
        "id": 32,
        "conditions": {"ph": "NEUTRAL", "turbidity": "TURBID", "tds": "HIGH", "do": "LOW"},
        "consequence": "NON_POTABLE", "weight": 0.85,
        "rationale": "Turbid + high TDS + low DO — stagnant contaminated water"
    },
    {
        "id": 33,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "TURBID", "tds": "HIGH", "do": "LOW"},
        "consequence": "NON_POTABLE", "weight": 0.88,
        "rationale": "Hard, turbid, stagnant water — unsuitable"
    },
    {
        "id": 34,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "TURBID", "tds": "ACCEPTABLE", "do": "LOW"},
        "consequence": "NON_POTABLE", "weight": 0.82,
        "rationale": "Turbid acidic water with stagnation — unsafe"
    },

    # ══════════════════════════════════════════════════════════════════
    # GROUP 6: EXTREME SCENARIOS
    # ══════════════════════════════════════════════════════════════════
    {
        "id": 35,
        "conditions": {"ph": "ACIDIC", "turbidity": "VERY_TURBID", "tds": "VERY_HIGH", "do": "VERY_LOW"},
        "consequence": "NON_POTABLE", "weight": 1.0,
        "rationale": "Worst-case scenario — severely contaminated (industrial/sewage)"
    },
    {
        "id": 36,
        "conditions": {"ph": "ALKALINE", "turbidity": "TURBID", "tds": "VERY_HIGH", "do": "VERY_LOW"},
        "consequence": "NON_POTABLE", "weight": 1.0,
        "rationale": "Highly alkaline, turbid, mineral-laden, anaerobic — unusable"
    },
    {
        "id": 37,
        "conditions": {"ph": "NEUTRAL", "turbidity": "CLEAR", "tds": "PURE", "do": "VERY_LOW"},
        "consequence": "NON_POTABLE", "weight": 0.88,
        "rationale": "Anoxic distilled water — anaerobic risk overrides physical clarity"
    },

    # ══════════════════════════════════════════════════════════════════
    # GROUP 7: MIXED CONDITIONS → MARGINAL
    # ══════════════════════════════════════════════════════════════════
    {
        "id": 38,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "SLIGHTLY_TURBID", "tds": "HIGH", "do": "LOW"},
        "consequence": "MARGINAL", "weight": 0.55,
        "rationale": "Four mild deviations — borderline, treatment strongly advised"
    },
    {
        "id": 39,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "SLIGHTLY_TURBID", "tds": "HIGH", "do": "LOW"},
        "consequence": "MARGINAL", "weight": 0.55,
        "rationale": "Alkaline + slightly turbid + high TDS + low DO"
    },
    {
        "id": 40,
        "conditions": {"ph": "NEUTRAL", "turbidity": "SLIGHTLY_TURBID", "tds": "ACCEPTABLE", "do": "LOW"},
        "consequence": "MARGINAL", "weight": 0.65,
        "rationale": "Good pH and TDS but turbidity + stagnation concern"
    },
    {
        "id": 41,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "SLIGHTLY_TURBID", "tds": "PURE", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.72,
        "rationale": "Pure water but slightly alkaline and turbid"
    },
    {
        "id": 42,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "CLEAR", "tds": "PURE", "do": "HIGH"},
        "consequence": "POTABLE", "weight": 0.82,
        "rationale": "Very pure, oxygenated; mild acidity tolerable per some standards"
    },
    {
        "id": 43,
        "conditions": {"ph": "SLIGHTLY_ALKALINE", "turbidity": "CLEAR", "tds": "ACCEPTABLE", "do": "LOW"},
        "consequence": "MARGINAL", "weight": 0.68,
        "rationale": "Borderline alkaline with stagnation (low DO)"
    },
    {
        "id": 44,
        "conditions": {"ph": "NEUTRAL", "turbidity": "TURBID", "tds": "PURE", "do": "LOW"},
        "consequence": "MARGINAL", "weight": 0.60,
        "rationale": "Turbid (silt/clay) but chemically pure — filtration needed"
    },
    {
        "id": 45,
        "conditions": {"ph": "SLIGHTLY_ACIDIC", "turbidity": "SLIGHTLY_TURBID", "tds": "PURE", "do": "ACCEPTABLE"},
        "consequence": "MARGINAL", "weight": 0.70,
        "rationale": "Natural acidic rainwater with slight turbidity — marginal"
    },
]


def get_rule_count() -> int:
    return len(RULES)


def get_rules_by_consequence(consequence: str) -> list:
    """Filter rules by their output class."""
    return [r for r in RULES if r["consequence"] == consequence]


def summarise_rule_base():
    """Print a summary of the rule base statistics."""
    total = len(RULES)
    counts = {}
    for r in RULES:
        c = r["consequence"]
        counts[c] = counts.get(c, 0) + 1
    print(f"\n{'─'*55}")
    print(f"  RULE BASE SUMMARY  ({total} rules total)")
    print(f"{'─'*55}")
    for cls, n in counts.items():
        print(f"  {cls:<18} : {n:>3} rules ({n/total*100:.1f}%)")
    print(f"{'─'*55}\n")


if __name__ == "__main__":
    summarise_rule_base()
    print("Sample Rule #1:")
    import json
    print(json.dumps(RULES[0], indent=2))
