"""
ablation_study.py
=================
Conducts a systematic sensor ablation study to quantify the contribution of
each sensor parameter (pH, Turbidity, TDS, Dissolved Oxygen) to classification
accuracy and critical water safety (False-Potable Hazard Rate).

Author: SC_CProject
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

from water_fis.core.fis_engine import WaterPotabilityFIS

CLASS_ORDER = ["POTABLE", "MARGINAL", "NON_POTABLE"]

# Default neutral/safe replacement values when a sensor is ablated (missing)
DEFAULT_SAFE_FILL = {
    "ph": 7.0,          # Neutral pH
    "turbidity": 0.5,   # Clear
    "tds": 300.0,       # Pure/Acceptable
    "do": 8.5,          # High DO
}


def run_ablation_study(csv_path: str = "outputs/synthetic_dataset.csv",
                       output_dir: str = "outputs"):
    print("\n" + "="*75)
    print("  RUNNING SENSOR ABLATION & SAFETY RISK ANALYSIS")
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

    configs = [
        ("Full Multi-Sensor (All 4)",      []),
        ("w/o Dissolved Oxygen (DO)",      ["do"]),
        ("w/o Turbidity",                  ["turbidity"]),
        ("w/o Total Dissolved Solids (TDS)",["tds"]),
        ("w/o pH",                         ["ph"]),
        ("2-Sensor Minimal (pH + Turb)",   ["tds", "do"]),
    ]

    results = []

    print(f"  {'Configuration':<34} {'Accuracy':<10} {'F1-Macro':<10} {'False Potable % (Hazard)':<25}")
    print("-" * 75)

    for name, dropped in configs:
        y_pred = []
        for _, row in df.iterrows():
            params = {
                "ph": row["ph"] if "ph" not in dropped else DEFAULT_SAFE_FILL["ph"],
                "turbidity": row["turbidity"] if "turbidity" not in dropped else DEFAULT_SAFE_FILL["turbidity"],
                "tds": row["tds"] if "tds" not in dropped else DEFAULT_SAFE_FILL["tds"],
                "do": row["do"] if "do" not in dropped else DEFAULT_SAFE_FILL["do"],
            }
            res = engine.infer(params["ph"], params["turbidity"], params["tds"], params["do"])
            y_pred.append(res["label"].replace("-", "_"))

        y_pred_enc = le.transform(y_pred)
        acc = accuracy_score(y_true_enc, y_pred_enc) * 100
        f1 = f1_score(y_true_enc, y_pred_enc, average="macro") * 100

        # Calculate False Potable rate: True is NON_POTABLE or MARGINAL, but predicted POTABLE
        # In a safety critical system, this is the most dangerous error!
        cm = confusion_matrix(y_true_enc, y_pred_enc, labels=le.transform(CLASS_ORDER))
        # Index 0: POTABLE, 1: MARGINAL, 2: NON_POTABLE
        total_unsafe = cm[1].sum() + cm[2].sum()
        false_potable = cm[1][0] + cm[2][0]
        fp_rate = (false_potable / total_unsafe * 100) if total_unsafe > 0 else 0.0

        results.append({
            "name": name,
            "dropped_sensors": dropped,
            "accuracy": round(acc, 2),
            "f1_macro": round(f1, 2),
            "false_potable_rate": round(fp_rate, 2),
            "false_potable_count": int(false_potable),
            "total_unsafe_count": int(total_unsafe)
        })

        print(f"  {name:<34} {acc:>8.2f}% {f1:>8.2f}% {fp_rate:>18.2f}% ({false_potable}/{total_unsafe})")

    print("=" * 75)

    # Save JSON results
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "ablation_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[*] Results saved → {json_path}")

    # Plot Ablation Comparison Chart
    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    plot_path = os.path.join(fig_dir, "sensor_ablation.png")

    names = [r["name"].replace("w/o ", "- ").replace(" (All 4)", "") for r in results]
    accs = [r["accuracy"] for r in results]
    hazard_rates = [r["false_potable_rate"] for r in results]

    x = np.arange(len(names))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()

    rects1 = ax1.bar(x - width/2, accs, width, label='Classification Accuracy (%)', color='#0E7C86', alpha=0.9)
    rects2 = ax2.bar(x + width/2, hazard_rates, width, label='False Potable Hazard Rate (%)', color='#EF4444', alpha=0.85)

    ax1.set_ylabel('Accuracy (%)', color='#0E7C86', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Hazard: False Potable Rate (%)', color='#EF4444', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=15, ha='right', fontsize=9.5)
    ax1.set_ylim(0, 100)
    ax2.set_ylim(0, max(hazard_rates) * 1.3)

    plt.title("Sensor Ablation: Impact of Missing Sensors on Accuracy vs Safety Hazard", fontsize=12, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[*] Ablation plot saved → {plot_path}\n")

    return results


if __name__ == "__main__":
    run_ablation_study()
