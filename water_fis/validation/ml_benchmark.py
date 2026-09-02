"""
ml_benchmark.py
===============
Benchmarks the FIS against Machine Learning classifiers:
  - Random Forest (scikit-learn)
  - K-Nearest Neighbours
  - Support Vector Machine (RBF kernel)

Outputs confusion matrices, F1 scores, accuracy, and comparison table.

Author: SC_CProject
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score
)
import os, json


FEATURE_COLS = ["ph", "turbidity", "tds", "do"]
TARGET_COL   = "oracle_class"
CLASS_ORDER  = ["POTABLE", "MARGINAL", "NON_POTABLE"]


def load_data(csv_path: str) -> tuple:
    df = pd.read_csv(csv_path)
    X  = df[FEATURE_COLS].values
    y  = df[TARGET_COL].values
    return X, y, df


def train_and_evaluate_ml(csv_path: str,
                          test_size: float = 0.20,
                          random_state: int = 42) -> dict:
    """
    Train RF, KNN, SVM on the synthetic dataset and report metrics.

    Returns:
        results dict: {classifier_name: {accuracy, f1_macro, report, cm}}
    """
    X, y, _ = load_data(csv_path)
    le       = LabelEncoder()
    y_enc    = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=test_size,
        random_state=random_state, stratify=y_enc
    )

    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    classifiers = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=10,
            random_state=random_state, n_jobs=-1
        ),
        "KNN (k=7)": KNeighborsClassifier(n_neighbors=7, metric="euclidean"),
        "SVM (RBF)": SVC(kernel="rbf", C=10.0, gamma="scale",
                         random_state=random_state),
    }

    results = {}
    for name, clf in classifiers.items():
        clf.fit(X_train, y_train)
        y_pred    = clf.predict(X_test)
        acc       = accuracy_score(y_test, y_pred)
        f1_macro  = f1_score(y_test, y_pred, average="macro")
        cv_scores = cross_val_score(clf, X, y_enc, cv=5, scoring="accuracy", n_jobs=-1)
        cm        = confusion_matrix(y_test, y_pred)
        report    = classification_report(
            y_test, y_pred,
            target_names=le.classes_,
            output_dict=True
        )
        results[name] = {
            "accuracy":        round(acc * 100, 2),
            "f1_macro":        round(f1_macro * 100, 2),
            "cv_mean":         round(cv_scores.mean() * 100, 2),
            "cv_std":          round(cv_scores.std() * 100, 2),
            "confusion_matrix":cm.tolist(),
            "report":          report,
            "classes":         le.classes_.tolist(),
        }

    return results


def evaluate_fis_on_dataset(csv_path: str) -> dict:
    """
    Run the FIS on the synthetic dataset and compute metrics.
    FIS output is classified and compared against oracle labels.
    """
    from water_fis.core.fis_engine import WaterPotabilityFIS

    engine = WaterPotabilityFIS()
    _, _, df = load_data(csv_path)

    y_true, y_pred = [], []
    for _, row in df.iterrows():
        result = engine.infer(
            ph=row["ph"], turbidity=row["turbidity"],
            tds=row["tds"], do=row["do"]
        )
        fis_class = result["label"].replace("-", "_")  # NON-POTABLE → NON_POTABLE
        y_true.append(row[TARGET_COL])
        y_pred.append(fis_class)

    # Encode
    le = LabelEncoder()
    le.fit(CLASS_ORDER)
    y_true_enc = le.transform(y_true)
    y_pred_enc = le.transform(y_pred)

    acc      = accuracy_score(y_true_enc, y_pred_enc)
    f1_macro = f1_score(y_true_enc, y_pred_enc, average="macro")
    cm       = confusion_matrix(y_true_enc, y_pred_enc)
    report   = classification_report(
        y_true_enc, y_pred_enc,
        target_names=le.classes_, output_dict=True
    )
    return {
        "accuracy":        round(acc * 100, 2),
        "f1_macro":        round(f1_macro * 100, 2),
        "cv_mean":         "N/A",
        "cv_std":          "N/A",
        "confusion_matrix":cm.tolist(),
        "report":          report,
        "classes":         le.classes_.tolist(),
    }


def print_comparison_table(all_results: dict):
    print(f"\n{'═'*75}")
    print("  CLASSIFIER COMPARISON (vs Synthetic Dataset)")
    print(f"{'─'*75}")
    print(f"  {'Method':<22} {'Accuracy':>10} {'F1-Macro':>10} {'CV Acc (5-fold)':>18}")
    print(f"{'─'*75}")
    for name, res in all_results.items():
        cv = f"{res['cv_mean']}% ± {res['cv_std']}%" if res['cv_mean'] != 'N/A' else "  —  "
        print(
            f"  {name:<22} {res['accuracy']:>9.2f}% {res['f1_macro']:>9.2f}%  {cv:>18}"
        )
    print(f"{'═'*75}\n")


def run_full_benchmark(csv_path: str,
                       output_dir: str = "outputs") -> dict:
    """
    Run complete benchmark: ML classifiers + FIS, save JSON results.

    Returns:
        Combined results dict
    """
    print("\n[BM] Training ML classifiers...")
    ml_results  = train_and_evaluate_ml(csv_path)

    print("[BM] Evaluating FIS on dataset...")
    fis_result  = evaluate_fis_on_dataset(csv_path)

    all_results = {"Mamdani FIS (Proposed)": fis_result, **ml_results}
    print_comparison_table(all_results)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "benchmark_results.json")
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"[BM] Results saved → {out_path}")
    return all_results


if __name__ == "__main__":
    CSV = "outputs/synthetic_dataset.csv"
    if not os.path.exists(CSV):
        from water_fis.data.synthetic_generator import generate_dataset
        generate_dataset(output_path=CSV)
    run_full_benchmark(CSV)
