"""
membership_functions.py
=======================
Fuzzy membership functions for the Water Potability FIS.
Parameters: pH, Turbidity, TDS, DO | Output: WPI

Standards: WHO Guidelines (2022), BIS IS 10500:2012
Author: SC_CProject
"""

import numpy as np
import skfuzzy as fuzz

# ── Universe of Discourse ──────────────────────────────────────────
pH_UoD    = np.arange(0.0,  14.01,  0.01)
turb_UoD  = np.arange(0.0, 100.01,  0.10)
tds_UoD   = np.arange(0.0, 1500.1,  0.50)
do_UoD    = np.arange(0.0,  20.01,  0.01)
wpi_UoD   = np.arange(0.0,  10.01,  0.01)

UNIVERSES = {
    "ph": pH_UoD, "turbidity": turb_UoD,
    "tds": tds_UoD, "do": do_UoD, "wpi": wpi_UoD,
}

# ── pH MFs ─────────────────────────────────────────────────────────
# WHO safe: 6.5–8.5  |  BIS: 6.5–8.5 desirable
def build_ph_mf():
    return {
        "ACIDIC":            fuzz.trapmf(pH_UoD, [0.0,  0.0,  5.0,  6.5]),
        "SLIGHTLY_ACIDIC":   fuzz.trimf( pH_UoD, [5.5,  6.5,  7.2]),
        "NEUTRAL":           fuzz.trimf( pH_UoD, [6.5,  7.0,  7.8]),
        "SLIGHTLY_ALKALINE": fuzz.trimf( pH_UoD, [7.2,  8.0,  8.8]),
        "ALKALINE":          fuzz.trapmf(pH_UoD, [8.2,  9.0, 14.0, 14.0]),
    }

# ── Turbidity MFs ──────────────────────────────────────────────────
# WHO ideal: <1 NTU  |  BIS permissible: <5 NTU
def build_turbidity_mf():
    return {
        "CLEAR":          fuzz.trapmf(turb_UoD, [ 0.0,  0.0,  1.0,  5.0]),
        "SLIGHTLY_TURBID":fuzz.trimf( turb_UoD, [ 2.0, 10.0, 25.0]),
        "TURBID":         fuzz.trimf( turb_UoD, [15.0, 40.0, 70.0]),
        "VERY_TURBID":    fuzz.trapmf(turb_UoD, [50.0, 75.0,100.0,100.0]),
    }

# ── TDS MFs ────────────────────────────────────────────────────────
# BIS desirable: 500 mg/L  |  BIS permissible: 2000 mg/L
def build_tds_mf():
    return {
        "PURE":       fuzz.trapmf(tds_UoD, [  0.0,   0.0, 100.0, 300.0]),
        "ACCEPTABLE": fuzz.trimf( tds_UoD, [150.0, 350.0, 550.0]),
        "HIGH":       fuzz.trimf( tds_UoD, [450.0, 650.0, 900.0]),
        "VERY_HIGH":  fuzz.trapmf(tds_UoD, [750.0,1000.0,1500.0,1500.0]),
    }

# ── DO MFs ─────────────────────────────────────────────────────────
# Healthy: >6 mg/L  |  <2 mg/L = anaerobic / microbial risk
def build_do_mf():
    return {
        "VERY_LOW":   fuzz.trapmf(do_UoD, [0.0,  0.0,  2.0,  4.0]),
        "LOW":        fuzz.trimf( do_UoD, [3.0,  5.0,  7.5]),
        "ACCEPTABLE": fuzz.trimf( do_UoD, [6.0,  8.5, 11.0]),
        "HIGH":       fuzz.trapmf(do_UoD, [9.0, 11.0, 20.0, 20.0]),
    }

# ── WPI Output MFs ─────────────────────────────────────────────────
# 0–10 scale: 0=worst, 10=best
def build_wpi_mf():
    return {
        "NON_POTABLE": fuzz.trapmf(wpi_UoD, [0.0, 0.0, 2.0, 3.5]),
        "MARGINAL":    fuzz.trimf( wpi_UoD, [3.0, 5.0, 7.0]),
        "POTABLE":     fuzz.trapmf(wpi_UoD, [6.5, 8.0,10.0,10.0]),
    }

def build_all_mfs() -> dict:
    """Build and return all membership function dictionaries."""
    return {
        "ph":        build_ph_mf(),
        "turbidity": build_turbidity_mf(),
        "tds":       build_tds_mf(),
        "do":        build_do_mf(),
        "wpi":       build_wpi_mf(),
    }

def get_membership(value: float, universe: np.ndarray, mf_array: np.ndarray) -> float:
    """Interpolate μ(value) for a given MF. Returns float in [0,1]."""
    value = float(np.clip(value, universe[0], universe[-1]))
    return float(np.interp(value, universe, mf_array))


if __name__ == "__main__":
    mfs = build_all_mfs()
    tests = [
        ("ph", pH_UoD, 7.0, "Neutral pH"),
        ("ph", pH_UoD, 4.5, "Acidic pH"),
        ("turbidity", turb_UoD, 0.5, "Clear water"),
        ("do", do_UoD, 1.5, "Very low DO"),
    ]
    print("\n── MF SANITY CHECK ──")
    for param, uod, val, desc in tests:
        print(f"\n  {desc} [{param}={val}]")
        for term, mf in mfs[param].items():
            mu = get_membership(val, uod, mf)
            print(f"    {term:<22} μ = {mu:.3f}  {'█'*int(mu*20)}")
