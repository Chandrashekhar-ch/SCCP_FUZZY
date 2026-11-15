"""
build_unified_dataset.py
========================
Inspects, cleans, and merges newly added datasets in datasets/ to create:
1. 'outputs/unified_multisensor_water_dataset.csv' (2,487 complete 4-sensor + temp samples)
2. 'outputs/extended_smart_water_dataset.csv' (6,720 extended chemical IoT samples)

Applies sensor range validation, calculates Traditional WQI, runs Mamdani FIS,
and generates class labels.

Author: SC_CProject
"""

import os
import sys
import glob
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from water_fis.core.fis_engine import WaterPotabilityFIS
from water_fis.validation.wqi_comparator import calculate_traditional_wqi, classify_wqi


def inspect_all_datasets(data_dir: str = "datasets"):
    """Scans and profiles all CSV datasets in the datasets folder."""
    files = glob.glob(os.path.join(data_dir, "*.csv"))
    print("\n" + "="*75)
    print("  DATASET REPOSITORY AUDIT & SENSOR PARAMETER MAPPING")
    print("="*75)
    
    profiles = []
    for f in sorted(files):
        df = pd.read_csv(f)
        fname = os.path.basename(f)
        cols = list(df.columns)
        n_rows = len(df)
        
        # Check presence of key sensors
        has_ph = any('ph' in c.lower() for c in cols)
        has_turb = any('turb' in c.lower() or 'secchi' in c.lower() for c in cols)
        has_tds = any('tds' in c.lower() or 'solid' in c.lower() or 'cond' in c.lower() for c in cols)
        has_do = any('do' in c.lower() or 'oxygen' in c.lower() for c in cols)
        has_temp = any('temp' in c.lower() for c in cols)
        has_target = any('potab' in c.lower() or 'qual' in c.lower() or 'wqi' in c.lower() for c in cols)
        
        profiles.append({
            "filename": fname,
            "rows": n_rows,
            "columns": len(cols),
            "ph": has_ph,
            "turbidity": has_turb,
            "tds": has_tds,
            "do": has_do,
            "temp": has_temp,
            "target": has_target
        })
        
        status = "COMPATIBLE (All 4 Sensors)" if (has_ph and has_turb and has_tds and has_do) else "Partial / Auxiliary"
        print(f"  {fname:<38} | Rows: {n_rows:>5} | {status}")
    print("="*75)
    return profiles


def build_unified_multisensor_dataset(output_path: str = "outputs/unified_multisensor_water_dataset.csv"):
    """
    Combines the 3 datasets that feature physical multi-sensor measurements
    for all 4 primary inputs (pH, Turbidity, TDS, DO) and Temperature.
    """
    print("\n[*] Assembling Unified 4-Sensor Benchmark Dataset...")
    engine = WaterPotabilityFIS()
    dfs = []
    
    # 1. water_quality_ml.csv (2,000 samples)
    p1 = "datasets/water_quality_ml.csv"
    if os.path.exists(p1):
        df1 = pd.read_csv(p1)
        d1 = pd.DataFrame({
            "ph": df1["pH"].round(2),
            "turbidity": df1["Turbidity"].round(2),
            "tds": df1["TDS"].round(1),
            "do": df1["Dissolved_Oxygen"].round(2),
            "temperature": df1["Temperature"].round(1),
            "oracle_class": df1["Water_Quality"].map({2: "POTABLE", 1: "MARGINAL", 0: "NON_POTABLE"}),
            "dataset_source": "water_quality_ml"
        })
        dfs.append(d1)
        print(f"    - Ingested {len(d1)} samples from water_quality_ml.csv")

    # 2. water_quality_analytics.csv (400 samples)
    p2 = "datasets/water_quality_analytics.csv"
    if os.path.exists(p2):
        df2 = pd.read_csv(p2)
        d2 = pd.DataFrame({
            "ph": df2["pH"].round(2),
            "turbidity": df2["Turbidity_NTU"].round(2),
            "tds": df2["TDS_mg_L"].round(1),
            "do": df2["DO_mg_L"].round(2),
            "temperature": df2["Temperature_C"].round(1),
            "oracle_class": df2["Water_Quality"].map({"Good": "POTABLE", "Moderate": "MARGINAL", "Poor": "NON_POTABLE"}),
            "dataset_source": "water_quality_analytics"
        })
        dfs.append(d2)
        print(f"    - Ingested {len(d2)} samples from water_quality_analytics.csv")

    # 3. water_quality_dataset.csv (103 samples)
    p3 = "datasets/water_quality_dataset.csv"
    if os.path.exists(p3):
        df3 = pd.read_csv(p3).dropna(subset=["pH", "Turbidity [NTU]", "TDS [mg/l]", "DO [mg/l]", "Temp [°C]"])
        d3 = pd.DataFrame({
            "ph": df3["pH"].round(2),
            "turbidity": df3["Turbidity [NTU]"].round(2),
            "tds": df3["TDS [mg/l]"].round(1),
            "do": df3["DO [mg/l]"].round(2),
            "temperature": df3["Temp [°C]"].round(1),
            "oracle_class": df3["Water quality"].map({"EXCELLENT": "POTABLE", "GOOD": "POTABLE", "FAIR": "MARGINAL", "POOR": "NON_POTABLE"}),
            "dataset_source": "water_quality_field"
        })
        dfs.append(d3)
        print(f"    - Ingested {len(d3)} samples from water_quality_dataset.csv")

    if not dfs:
        print("[!] No compatible datasets found.")
        return None

    unified = pd.concat(dfs, ignore_index=True)

    # Sensor dynamic range sanity clamping
    unified["ph"] = unified["ph"].clip(0.0, 14.0)
    unified["turbidity"] = unified["turbidity"].clip(0.0, 100.0)
    unified["tds"] = unified["tds"].clip(0.0, 1500.0)
    unified["do"] = unified["do"].clip(0.0, 20.0)

    # Binary potability flag
    unified["is_potable"] = (unified["oracle_class"] == "POTABLE").astype(int)

    # Compute Traditional WQI and Mamdani FIS WPI for all records
    print("[*] Computing Traditional WQI & Mamdani FIS scores for all records...")
    wqi_scores = []
    wqi_classes = []
    fis_scores = []
    fis_classes = []

    for _, row in unified.iterrows():
        # Traditional WQI
        w = calculate_traditional_wqi(row)
        wqi_scores.append(round(w, 2))
        wqi_classes.append(classify_wqi(w))
        
        # Mamdani FIS
        res = engine.infer(row["ph"], row["turbidity"], row["tds"], row["do"])
        fis_scores.append(res["wpi"])
        fis_classes.append(res["label"].replace("-", "_"))

    unified["traditional_wqi"] = wqi_scores
    unified["traditional_wqi_class"] = wqi_classes
    unified["fis_wpi"] = fis_scores
    unified["fis_class"] = fis_classes

    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    unified.to_csv(output_path, index=False)
    print(f"\n[+] Successfully generated Unified Multi-Sensor Dataset!")
    print(f"    File: {output_path}")
    print(f"    Total Records: {len(unified)}")
    print(f"    Class Breakdown: {unified['oracle_class'].value_counts().to_dict()}")
    print(f"    FIS Predictions: {unified['fis_class'].value_counts().to_dict()}")
    
    return unified


def export_extended_smart_dataset(output_path: str = "outputs/extended_smart_water_dataset.csv"):
    """
    Cleans and standardizes smart_water_quality.csv (6,720 rows) for extended
    multi-chemical analysis.
    """
    src = "datasets/smart_water_quality.csv"
    if not os.path.exists(src):
        return None
    df = pd.read_csv(src)
    
    # Standardize column naming
    clean = pd.DataFrame({
        "timestamp": df["Timestamp"],
        "location": df["Location"],
        "ph": df["ph"].round(2),
        "turbidity": df["Turbidity"].round(2),
        "tds_solids": df["Solids"].round(1),
        "conductivity": df["Conductivity"].round(1),
        "hardness": df["Hardness"].round(1),
        "chloramines": df["Chloramines"].round(2),
        "sulfate": df["Sulfate"].round(1),
        "organic_carbon": df["Organic_carbon"].round(2),
        "trihalomethanes": df["Trihalomethanes"].round(2),
        "wqi": df["WQI"].round(1),
        "is_potable": df["Potability"]
    })
    clean.to_csv(output_path, index=False)
    print(f"[+] Exported Extended Smart Water Dataset ({len(clean)} rows) → {output_path}")
    return clean


if __name__ == "__main__":
    inspect_all_datasets()
    build_unified_multisensor_dataset()
    export_extended_smart_dataset()
