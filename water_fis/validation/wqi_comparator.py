"""
wqi_comparator.py
=================
Compares the Fuzzy Inference System (WPI) with the traditional Weighted Arithmetic Water Quality Index (WQI).
"""
import pandas as pd

# Standard values (Sn) and Ideal values (Vio) based on BIS IS 10500 / WHO
# Weights (Wn) = K / Sn, where K is a proportionality constant
STANDARDS = {
    'ph': {'Sn': 8.5, 'Vio': 7.0, 'Wn': 0.1176},
    'turbidity': {'Sn': 5.0, 'Vio': 0.0, 'Wn': 0.2000},
    'tds': {'Sn': 500.0, 'Vio': 0.0, 'Wn': 0.0020},
    'do': {'Sn': 6.0, 'Vio': 14.6, 'Wn': 0.1667} 
}

def calculate_traditional_wqi(row) -> float:
    """Calculates weighted arithmetic WQI for a single row."""
    qi_wn_sum = 0
    wn_sum = 0
    
    for param, vals in STANDARDS.items():
        val = row.get(param, 0)
        sn = vals['Sn']
        vio = vals['Vio']
        wn = vals['Wn']
        
        # Calculate Quality Rating (qi)
        if param == 'ph':
            qi = 100 * ((val - vio) / (sn - vio))
        else:
            qi = 100 * (val / sn)
        
        qi_wn_sum += qi * wn
        wn_sum += wn
        
    if wn_sum == 0: return 0
    wqi = qi_wn_sum / wn_sum
    return wqi

def classify_wqi(wqi: float) -> str:
    """Classifies traditional WQI score."""
    if wqi < 50: return "POTABLE" 
    elif wqi < 100: return "MARGINAL" 
    else: return "NON_POTABLE" 
