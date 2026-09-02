"""
synthetic_generator.py
======================
Generates a labeled synthetic dataset for FIS training/validation.

Strategy:
  - Draws samples from realistic statistical distributions per class
  - Adds Gaussian sensor noise (σ = 3% of range)
  - Labels using WHO/BIS rule-based oracle (hard thresholds)
  - Outputs: CSV with 5,000 samples + class distribution report

Distributions based on:
  WHO (2022), BIS IS 10500:2012, Kaggle Water Quality Dataset analysis

Author: SC_CProject
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime


# ── Class-conditional distributions ───────────────────────────────
# Each entry: (mean, std, clip_low, clip_high)
DISTRIBUTIONS = {
    "POTABLE": {
        "ph":        (7.05, 0.35,  6.5,  8.5),
        "turbidity": (0.60, 0.40,  0.0,  5.0),
        "tds":       (320., 100., 50.0, 500.),
        "do":        (8.50, 1.00,  6.5, 14.0),
        "temperature":(24., 3.00, 15.0, 35.0),
    },
    "MARGINAL": {
        "ph":        (7.50, 0.70,  6.0,  9.2),
        "turbidity": (8.00, 5.00,  1.0, 30.0),
        "tds":       (520., 120., 200., 750.),
        "do":        (5.50, 1.20,  3.0,  8.0),
        "temperature":(26., 4.00, 18.0, 38.0),
    },
    "NON_POTABLE": {
        # Mix of acidic, alkaline, turbid, high TDS, low DO
        "ph":        (5.00, 2.50,  0.0, 14.0),
        "turbidity": (55.0, 25.0,  5.0,100.0),
        "tds":       (900., 250., 500.,1500.),
        "do":        (2.00, 1.20,  0.0,  4.5),
        "temperature":(28., 5.00, 10.0, 45.0),
    },
}

NOISE_SIGMA_PCT = 3.0  # % of full range

RANGES = {
    "ph":         (0.,  14.),
    "turbidity":  (0., 100.),
    "tds":        (0.,1500.),
    "do":         (0.,  20.),
    "temperature":(0.,  50.),
}


def _add_noise(value: float, param: str) -> float:
    lo, hi = RANGES[param]
    sigma = NOISE_SIGMA_PCT / 100.0 * (hi - lo)
    return float(np.clip(value + np.random.normal(0, sigma), lo, hi))


def _oracle_label(ph, turbidity, tds, do) -> str:
    """
    Hard-threshold oracle labeler based on WHO/BIS limits.
    Used as ground-truth for dataset labeling.
    """
    # Hard NON-POTABLE conditions
    if ph < 5.5 or ph > 9.0:
        return "NON_POTABLE"
    if turbidity > 40.0:
        return "NON_POTABLE"
    if tds > 1000.0:
        return "NON_POTABLE"
    if do < 2.5:
        return "NON_POTABLE"

    # Hard POTABLE conditions
    if (6.5 <= ph <= 8.5 and turbidity <= 1.0 and
            tds <= 500.0 and do >= 6.5):
        return "POTABLE"

    # MARGINAL: everything else
    return "MARGINAL"


def generate_dataset(n_samples: int = 5000,
                     class_dist: dict = None,
                     random_seed: int = 42,
                     output_path: str = "outputs/synthetic_dataset.csv") -> pd.DataFrame:
    """
    Generate a synthetic labeled water quality dataset.

    Args:
        n_samples   : Total number of samples
        class_dist  : {'POTABLE': 0.40, 'MARGINAL': 0.35, 'NON_POTABLE': 0.25}
        random_seed : Reproducibility seed
        output_path : CSV save path

    Returns:
        pandas DataFrame with columns:
          [ph, turbidity, tds, do, temperature, true_class, oracle_class]
    """
    if class_dist is None:
        class_dist = {"POTABLE": 0.40, "MARGINAL": 0.35, "NON_POTABLE": 0.25}

    np.random.seed(random_seed)
    records = []

    for cls, fraction in class_dist.items():
        n_cls = int(n_samples * fraction)
        dist  = DISTRIBUTIONS[cls]

        for _ in range(n_cls):
            raw = {}
            for param in ["ph", "turbidity", "tds", "do", "temperature"]:
                mu, sigma, lo, hi = dist[param]
                val = np.clip(np.random.normal(mu, sigma), lo, hi)
                raw[param] = _add_noise(val, param)

            oracle = _oracle_label(
                raw["ph"], raw["turbidity"], raw["tds"], raw["do"]
            )
            records.append({
                **raw,
                "true_class":   cls,
                "oracle_class": oracle,
            })

    # Shuffle
    df = pd.DataFrame(records).sample(frac=1, random_state=random_seed).reset_index(drop=True)
    df["sample_id"] = df.index + 1

    # Round for readability
    for col in ["ph", "turbidity", "tds", "do", "temperature"]:
        df[col] = df[col].round(3)

    # Save
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    df.to_csv(output_path, index=False)

    _print_report(df, output_path)
    return df


def _print_report(df: pd.DataFrame, path: str):
    print(f"\n{'═'*60}")
    print(f"  SYNTHETIC DATASET GENERATED")
    print(f"  Path    : {path}")
    print(f"  Samples : {len(df)}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'─'*60}")
    print(f"  {'Class':<14} {'Count':>7} {'%':>6}")
    print(f"{'─'*60}")
    for cls in ["POTABLE", "MARGINAL", "NON_POTABLE"]:
        n = (df["true_class"] == cls).sum()
        print(f"  {cls:<14} {n:>7}  {n/len(df)*100:>5.1f}%")
    print(f"{'─'*60}")
    print(f"  Parameter Statistics (mean ± std):")
    for col in ["ph", "turbidity", "tds", "do"]:
        print(f"    {col:<12}: {df[col].mean():>7.2f} ± {df[col].std():.2f}")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    df = generate_dataset(
        n_samples=5000,
        output_path="../../outputs/synthetic_dataset.csv"
    )
    print(df.head(10).to_string())
