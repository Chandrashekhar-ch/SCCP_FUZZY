"""
sensitivity_analysis.py
=======================
Evaluates the noise-robustness of the Mamdani Fuzzy Inference System compared
to Hard-Threshold logic and Supervised ML (Random Forest) under increasing
sensor measurement noise (0% to 15% Gaussian jitter).

Author: SC_CProject
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from water_fis.core.fis_engine import WaterPotabilityFIS
from water_fis.data.synthetic_generator import RANGES, _oracle_label


def hard_threshold_classifier(row) -> str:
    """Rigid Boolean logic classifier using strict WHO/BIS cutoffs."""
    ph = row['ph']
    turb = row['turbidity']
    tds = row['tds']
    do = row['do']

    if ph < 6.5 or ph > 8.5:
        return "NON_POTABLE"
    if turb > 5.0:
        return "NON_POTABLE"
    if tds > 500.0:
        return "NON_POTABLE"
    if do < 6.0:
        return "NON_POTABLE"
    return "POTABLE"


def add_noise_to_df(df: pd.DataFrame, noise_pct: float) -> pd.DataFrame:
    """Injects zero-mean Gaussian noise proportional to sensor dynamic range."""
    df_noisy = df.copy()
    if noise_pct == 0.0:
        return df_noisy

    for param, (lo, hi) in RANGES.items():
        if param in df_noisy.columns:
            sigma = (noise_pct / 100.0) * (hi - lo)
            noise = np.random.normal(0, sigma, size=len(df_noisy))
            df_noisy[param] = np.clip(df_noisy[param] + noise, lo, hi)
    return df_noisy


def run_sensitivity_analysis(csv_path: str = "outputs/synthetic_dataset.csv",
                             output_dir: str = "outputs"):
    print("\n" + "="*70)
    print("  RUNNING SENSITIVITY & NOISE ROBUSTNESS ANALYSIS")
    print("="*70)

    if not os.path.exists(csv_path):
        from water_fis.data.synthetic_generator import generate_dataset
        generate_dataset(output_path=csv_path)

    df_clean = pd.read_csv(csv_path)
    feature_cols = ["ph", "turbidity", "tds", "do"]
    y_true = df_clean["oracle_class"].values

    # Train Random Forest on clean data (simulating pre-trained factory model)
    le = LabelEncoder()
    le.fit(["POTABLE", "MARGINAL", "NON_POTABLE"])
    y_true_enc = le.transform(y_true)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(df_clean[feature_cols].values, y_true_enc)

    engine = WaterPotabilityFIS()

    noise_levels = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0]
    results = {
        "noise_levels": noise_levels,
        "fis_accuracy": [],
        "fis_f1": [],
        "hard_threshold_accuracy": [],
        "rf_accuracy": []
    }

    print(f"  {'Noise (%)':<12} {'FIS Acc':<14} {'FIS F1':<14} {'Hard-Thresh Acc':<18} {'RF Acc':<12}")
    print("-" * 70)

    for noise in noise_levels:
        np.random.seed(42)
        df_noisy = add_noise_to_df(df_clean, noise)

        # 1. Mamdani FIS Evaluation
        fis_preds = []
        for _, r in df_noisy.iterrows():
            res = engine.infer(r['ph'], r['turbidity'], r['tds'], r['do'])
            label_norm = res['label'].replace("-", "_")
            fis_preds.append(label_norm)
        fis_preds_enc = le.transform(fis_preds)
        fis_acc = accuracy_score(y_true_enc, fis_preds_enc) * 100
        fis_f1 = f1_score(y_true_enc, fis_preds_enc, average='macro') * 100

        # 2. Hard-Threshold Evaluation (mapped to binary/ternary)
        ht_preds = [hard_threshold_classifier(r) for _, r in df_noisy.iterrows()]
        ht_preds_enc = le.transform(ht_preds)
        ht_acc = accuracy_score(y_true_enc, ht_preds_enc) * 100

        # 3. Random Forest Evaluation on noisy data
        rf_preds_enc = rf.predict(df_noisy[feature_cols].values)
        rf_acc = accuracy_score(y_true_enc, rf_preds_enc) * 100

        results["fis_accuracy"].append(round(fis_acc, 2))
        results["fis_f1"].append(round(fis_f1, 2))
        results["hard_threshold_accuracy"].append(round(ht_acc, 2))
        results["rf_accuracy"].append(round(rf_acc, 2))

        print(f"  {noise:>6.1f}%      {fis_acc:>8.2f}%     {fis_f1:>8.2f}%       {ht_acc:>10.2f}%       {rf_acc:>8.2f}%")

    print("=" * 70)

    # Save JSON results
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "sensitivity_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[*] Results saved → {json_path}")

    # Plot Noise Robustness Curve
    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    plot_path = os.path.join(fig_dir, "noise_robustness.png")

    plt.figure(figsize=(9, 5.5))
    plt.plot(noise_levels, results["fis_accuracy"], 'o-', color='#0E7C86', linewidth=2.5, label='Mamdani FIS (Graded Membership)')
    plt.plot(noise_levels, results["rf_accuracy"], 's--', color='#3B82F6', linewidth=2, label='Random Forest (Clean-trained)')
    plt.plot(noise_levels, results["hard_threshold_accuracy"], '^:', color='#EF4444', linewidth=2, label='Hard Threshold (Boolean Logic)')

    plt.title("Sensor Noise Robustness & Graceful Degradation", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Gaussian Sensor Noise (% of Dynamic Range)", fontsize=11)
    plt.ylabel("Classification Accuracy (%)", fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10, loc='lower left')
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[*] Robustness curve saved → {plot_path}\n")

    return results


if __name__ == "__main__":
    run_sensitivity_analysis()

