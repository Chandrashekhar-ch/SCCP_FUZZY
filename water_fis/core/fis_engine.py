"""
fis_engine.py
=============
Mamdani Fuzzy Inference System engine for water potability.

Pipeline:
  1. Fuzzification   — crisp inputs → membership degrees
  2. Rule Evaluation — MIN implication per rule
  3. Aggregation     — MAX across all rules (per output term)
  4. Defuzzification — Centroid of Area → crisp WPI score

Author: SC_CProject
"""

import numpy as np
from typing import Optional
from .membership_functions import (
    build_all_mfs, get_membership, UNIVERSES, wpi_UoD
)
from .rule_base import RULES


class WaterPotabilityFIS:
    """
    Mamdani Fuzzy Inference System for real-time water potability
    classification from multi-sensor data.

    Inputs:
        ph (float)         : pH value       [0, 14]
        turbidity (float)  : Turbidity NTU  [0, 100]
        tds (float)        : TDS mg/L       [0, 1500]
        do (float)         : DO mg/L        [0, 20]

    Output:
        wpi (float)        : Water Potability Index  [0, 10]
        label (str)        : 'NON-POTABLE' | 'MARGINAL' | 'POTABLE'
        activated_rules (list) : Rules that fired with their strengths
    """

    # WPI class boundaries (from config / methodology)
    CLASSES = [
        (0.0,  3.5, "NON-POTABLE", "#EF4444"),
        (3.5,  6.5, "MARGINAL",    "#F59E0B"),
        (6.5, 10.0, "POTABLE",     "#22C55E"),
    ]

    def __init__(self):
        self.mfs = build_all_mfs()
        self._wpi_universe = wpi_UoD
        self._n_points = len(wpi_UoD)

    # ─────────────────────────────────────────────────────────────────
    #  STEP 1: FUZZIFICATION
    # ─────────────────────────────────────────────────────────────────
    def fuzzify(self, inputs: dict) -> dict:
        """
        Compute membership degrees for all linguistic terms of each input.

        Args:
            inputs: {'ph': float, 'turbidity': float, 'tds': float, 'do': float}

        Returns:
            membership_map: {'ph': {'NEUTRAL': 0.8, 'ACIDIC': 0.0, ...}, ...}
        """
        membership_map = {}
        for param, value in inputs.items():
            if param not in self.mfs:
                continue
            uod = UNIVERSES[param]
            membership_map[param] = {
                term: get_membership(value, uod, mf_arr)
                for term, mf_arr in self.mfs[param].items()
            }
        return membership_map

    # ─────────────────────────────────────────────────────────────────
    #  STEP 2: RULE EVALUATION (MIN implication)
    # ─────────────────────────────────────────────────────────────────
    def evaluate_rules(self, membership_map: dict) -> list:
        """
        Fire all rules. Compute rule strength via MIN of antecedent membership.

        Args:
            membership_map: Output of fuzzify()

        Returns:
            list of dicts: [{rule_id, strength, consequence, weight}, ...]
        """
        activated = []
        for rule in RULES:
            antecedent_values = []
            for param, term in rule["conditions"].items():
                if term is None:
                    continue  # "any" — not constrained
                mu = membership_map.get(param, {}).get(term, 0.0)
                antecedent_values.append(mu)

            if not antecedent_values:
                continue

            rule_strength = min(antecedent_values) * rule["weight"]

            if rule_strength > 0.0:
                activated.append({
                    "rule_id":    rule["id"],
                    "strength":   rule_strength,
                    "consequence":rule["consequence"],
                    "weight":     rule["weight"],
                    "rationale":  rule["rationale"],
                })
        return activated

    # ─────────────────────────────────────────────────────────────────
    #  STEP 3: IMPLICATION + AGGREGATION
    # ─────────────────────────────────────────────────────────────────
    def aggregate(self, activated_rules: list) -> np.ndarray:
        """
        Apply MIN implication to each rule's output MF,
        then MAX-aggregate across all rules.

        Args:
            activated_rules: Output of evaluate_rules()

        Returns:
            aggregated: np.ndarray over wpi_UoD — combined fuzzy output
        """
        aggregated = np.zeros(self._n_points)

        for fired in activated_rules:
            term = fired["consequence"]
            strength = fired["strength"]
            # Clip output MF at rule strength (MIN implication)
            clipped = np.fmin(strength, self.mfs["wpi"][term])
            # MAX aggregation
            aggregated = np.fmax(aggregated, clipped)

        return aggregated

    # ─────────────────────────────────────────────────────────────────
    #  STEP 4: DEFUZZIFICATION (Centroid of Area)
    # ─────────────────────────────────────────────────────────────────
    def defuzzify(self, aggregated: np.ndarray) -> float:
        """
        Compute the centroid (center of gravity) of the aggregated fuzzy set.

        WPI = ∫ μ(y)·y dy / ∫ μ(y) dy

        Returns:
            wpi (float): crisp Water Potability Index in [0, 10]
        """
        total_area = np.trapz(aggregated, self._wpi_universe)
        if total_area == 0.0:
            return 5.0  # Default: MARGINAL if no rules fire
        weighted   = np.trapz(aggregated * self._wpi_universe, self._wpi_universe)
        return float(np.clip(weighted / total_area, 0.0, 10.0))

    # ─────────────────────────────────────────────────────────────────
    #  CLASSIFY
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def classify(wpi: float) -> tuple:
        """Map WPI to linguistic class and color."""
        for low, high, label, color in WaterPotabilityFIS.CLASSES:
            if low <= wpi <= high:
                return label, color
        return "MARGINAL", "#F59E0B"

    # ─────────────────────────────────────────────────────────────────
    #  MAIN INFERENCE — Full pipeline in one call
    # ─────────────────────────────────────────────────────────────────
    def infer(self, ph: float, turbidity: float,
              tds: float, do: float) -> dict:
        """
        Run the complete Mamdani inference pipeline.

        Args:
            ph         : pH reading   [0, 14]
            turbidity  : NTU reading  [0, 100]
            tds        : TDS mg/L     [0, 1500]
            do         : DO mg/L      [0, 20]

        Returns:
            result dict with: wpi, label, color, activated_rules,
                              aggregated_mf, membership_map
        """
        inputs = {"ph": ph, "turbidity": turbidity, "tds": tds, "do": do}

        # Stage 1
        membership_map  = self.fuzzify(inputs)
        # Stage 2
        activated_rules = self.evaluate_rules(membership_map)
        # Stage 3
        aggregated      = self.aggregate(activated_rules)
        # Stage 4
        wpi             = self.defuzzify(aggregated)
        # Classify
        label, color    = self.classify(wpi)

        return {
            "inputs":          inputs,
            "membership_map":  membership_map,
            "activated_rules": activated_rules,
            "aggregated_mf":   aggregated.tolist(),
            "wpi":             round(wpi, 4),
            "label":           label,
            "color":           color,
            "n_rules_fired":   len(activated_rules),
        }


# ─────────────────────────────────────────────────────────────────
#  Quick demo
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = WaterPotabilityFIS()

    test_samples = [
        (7.0,  0.5, 320.0,  9.0, "Ideal drinking water"),
        (4.5, 60.0, 900.0,  1.5, "Severely contaminated"),
        (7.8,  3.0, 480.0,  7.2, "Borderline — slightly alkaline"),
        (6.8,  0.8, 250.0,  8.0, "Good quality groundwater"),
        (9.5,  0.5, 200.0,  8.0, "Overly alkaline (industrial)"),
    ]

    print(f"\n{'═'*72}")
    print("  WATER POTABILITY FIS — INFERENCE DEMO")
    print(f"{'═'*72}")
    header = f"  {'Scenario':<32} {'pH':>5} {'Turb':>6} {'TDS':>6} {'DO':>5}  WPI   CLASS"
    print(header)
    print(f"{'─'*72}")
    for ph, turb, tds, do, desc in test_samples:
        result = engine.infer(ph, turb, tds, do)
        print(
            f"  {desc:<32} {ph:>5.1f} {turb:>6.1f} {tds:>6.0f} {do:>5.1f} "
            f" {result['wpi']:>5.2f}  {result['label']}"
        )
    print(f"{'═'*72}\n")
