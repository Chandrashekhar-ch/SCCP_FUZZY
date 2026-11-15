"""
wqi_benchmark.py
================
Head-to-head empirical comparison between:
  1. Traditional Weighted Arithmetic Water Quality Index (Brown et al., 1970)
  2. Proposed Mamdani Fuzzy Inference System (Water Potability Index - WPI)

Demonstrates how Mamdani FIS overcomes the classic 'Eclipsing' and 'Ambiguity'
flaws inherent in arithmetic averaging indices.

Author: SC_CProject
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

from water_fis.core.fis_engine import WaterPotabilityFIS
from water_fis.validation.wqi_comparator import calculate_traditional_wqi, classify_wqi

CLASS_ORDER = ["POTABLE", "MARGINAL", "NON_POTABLE"]


def run_wqi_comparison(csv_path: str = "outputs/synthetic_dataset.csv",
                       output_dir: str = "outputs"):
    print("\n" + "="*75)
    print("  RUNNING TRADITIONAL WQI vs PROPOSED MAMDANI FIS COMPARISON")
    print("="*75)

    if not os.path.exists(csv_path):
        from water_fis.data.synthetic_generator import generate_dataset
        generate_dataset(output_path=csv_path)

    df = pd.read_csv(csv_path)
    engine = WaterPotabilityFIS()
    le = LabelEncoder()
    le.fit(CLASS_ORDER)
    y_true = df["oracle_class"].values
    y_true_enc = le.transform(y_true)

    # 1. Evaluate Mamdani FIS
    fis_preds = []
    fis_scores = []
    for _, r in df.iterrows():
        res = engine.infer(r['ph'], r['turbidity'], r['tds'], r['do'])
        fis_preds.append(res['label'].replace("-", "_"))
        fis_scores.append(res['wpi'])

    fis_preds_enc = le.transform(fis_preds)
    fis_acc = accuracy_score(y_true_enc, fis_preds_enc) * 100
    fis_f1 = f1_score(y_true_enc, fis_preds_enc, average="macro") * 100

    # 2. Evaluate Traditional WQI
    wqi_scores = []
    wqi_preds = []
    for _, r in df.iterrows():
        score = calculate_traditional_wqi(r)
        wqi_scores.append(score)
        wqi_preds.append(classify_wqi(score))

    wqi_preds_enc = le.transform(wqi_preds)
    wqi_acc = accuracy_score(y_true_enc, wqi_preds_enc) * 100
    wqi_f1 = f1_score(y_true_enc, wqi_preds_enc, average="macro") * 100

    # 3. Quantify Eclipsing Failures in Traditional WQI:
    # Cases where Ground Truth is NON_POTABLE (lethal single parameter),
    # but Traditional WQI averages it out to POTABLE!
    cm_wqi = confusion_matrix(y_true_enc, wqi_preds_enc, labels=le.transform(CLASS_ORDER))
    cm_fis = confusion_matrix(y_true_enc, fis_preds_enc, labels=le.transform(CLASS_ORDER))

    # True NON_POTABLE (index 2) predicted as POTABLE (index 0)
    wqi_eclipsing_errors = int(cm_wqi[2][0])
    fis_eclipsing_errors = int(cm_fis[2][0])

    print(f"\n  {'Metric':<35} {'Traditional WQI':<20} {'Proposed Mamdani FIS':<20}")
    print("-" * 75)
    print(f"  {'Classification Accuracy':<35} {wqi_acc:>15.2f}% {fis_acc:>19.2f}%")
    print(f"  {'Macro F1-Score':<35} {wqi_f1:>15.2f}% {fis_f1:>19.2f}%")
    print(f"  {'Eclipsing Failures (Lethal → Safe)':<35} {wqi_eclipsing_errors:>16d} {fis_eclipsing_errors:>20d}")
    print("=" * 75)

    results = {
        "traditional_wqi": {
            "accuracy": round(wqi_acc, 2),
            "f1_macro": round(wqi_f1, 2),
            "eclipsing_errors": wqi_eclipsing_errors,
            "confusion_matrix": cm_wqi.tolist()
        },
        "mamdani_fis": {
            "accuracy": round(fis_acc, 2),
            "f1_macro": round(fis_f1, 2),
            "eclipsing_errors": fis_eclipsing_errors,
            "confusion_matrix": cm_fis.tolist()
        }
    }

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "wqi_comparison.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[*] Results saved → {json_path}")

    # Plot Comparison Bar Chart
    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    plot_path = os.path.join(fig_dir, "fis_vs_wqi.png")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))

    # Plot 1: Accuracy & F1
    x = np.arange(2)
    width = 0.35
    ax1.bar(x - width/2, [wqi_acc, wqi_f1], width, label='Traditional WQI', color='#F59E0B')
    ax1.bar(x + width/2, [fis_acc, fis_f1], width, label='Mamdani FIS (Proposed)', color='#0E7C86')
    ax1.set_ylabel('Score (%)', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Accuracy', 'F1-Macro'], fontsize=11)
    ax1.set_ylim(0, 100)
    ax1.set_title("Classification Efficacy", fontsize=12, fontweight='bold')
    ax1.legend(loc='lower left')
    ax1.grid(axis='y', linestyle='--', alpha=0.6)

    # Plot 2: Safety Failures (Eclipsing)
    ax2.bar(['Traditional WQI', 'Mamdani FIS'], [wqi_eclipsing_errors, fis_eclipsing_errors],
            color=['#EF4444', '#22C55E'], width=0.5)
    ax2.set_ylabel('Number of Eclipsing Errors (Lethal → Safe)', fontsize=11, fontweight='bold')
    ax2.set_title("Critical Safety Vulnerability (Eclipsing Problem)", fontsize=12, fontweight='bold')
    ax2.grid(axis='y', linestyle='--', alpha=0.6)

    for i, v in enumerate([wqi_eclipsing_errors, fis_eclipsing_errors]):
        ax2.text(i, v + (max(wqi_eclipsing_errors, 1)*0.02), str(v), ha='center', fontweight='bold', fontsize=11)

    fig.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[*] Comparison figure saved → {plot_path}\n")

    return results


if __name__ == "__main__":
    run_wqi_comparison()
