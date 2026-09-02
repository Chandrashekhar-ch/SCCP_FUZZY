"""
kaggle_benchmark.py
===================
Downloads the real-world Kaggle Water Quality dataset from a public GitHub repository,
maps the columns to our FIS inputs (pH, Turbidity, TDS), handles missing values,
and compares the Mamdani FIS performance against standard ML classifiers on real data.

Since the Kaggle dataset does not contain Dissolved Oxygen (DO), we assume a safe 
constant (DO = 8.0 mg/L) for the FIS so that it evaluates potability strictly based 
on pH, Turbidity, and TDS.

Author: SC_CProject
"""

import os
import pandas as pd
import urllib.request
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

from water_fis.core.fis_engine import WaterPotabilityFIS

KAGGLE_URL = "https://raw.githubusercontent.com/fenago/datasets/main/water_potability.csv"
DATA_PATH  = "outputs/kaggle_water_potability.csv"

def fetch_dataset():
    """Downloads the dataset if not already present."""
    if not os.path.exists(DATA_PATH):
        print(f"[*] Downloading real-world dataset from {KAGGLE_URL} ...")
        urllib.request.urlretrieve(KAGGLE_URL, DATA_PATH)
        print("[*] Download complete.")
    return pd.read_csv(DATA_PATH)

def preprocess_kaggle_data(df: pd.DataFrame):
    """
    Cleans the dataset and maps it to our feature space.
    Target: 'Potability' (1 = POTABLE, 0 = NON_POTABLE)
    """
    print(f"[*] Original dataset size: {len(df)}")
    
    # Drop rows with missing values in our key columns
    df = df.dropna(subset=['ph', 'Turbidity', 'Solids', 'Potability']).copy()
    print(f"[*] Size after dropping NaNs: {len(df)}")
    
    # Map to our FIS names
    df = df.rename(columns={
        'ph': 'ph',
        'Turbidity': 'turbidity',
        'Solids': 'tds'
    })
    
    # Add dummy DO (safe value so it doesn't trigger non-potable rules)
    df['do'] = 8.0 
    
    # Map target strings for reporting
    df['target_str'] = df['Potability'].map({1: 'POTABLE', 0: 'NON_POTABLE'})
    
    return df

def run_ml_classifiers(df: pd.DataFrame):
    """Trains and evaluates standard ML classifiers on the Kaggle data."""
    X = df[['ph', 'turbidity', 'tds', 'do']].values
    y = df['Potability'].values # 0 or 1
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    classifiers = {
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
        "KNN (k=7)": KNeighborsClassifier(n_neighbors=7),
        "SVM (RBF)": SVC(kernel="rbf", C=1.0, gamma="scale", random_state=42)
    }
    
    results = {}
    for name, clf in classifiers.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        f1  = f1_score(y_test, y_pred, average="macro")
        results[name] = {
            "accuracy": round(acc * 100, 2),
            "f1_macro": round(f1 * 100, 2)
        }
    return results

def evaluate_fis(df: pd.DataFrame):
    """Evaluates the proposed Mamdani FIS on the Kaggle dataset."""
    engine = WaterPotabilityFIS()
    
    y_true = []
    y_pred = []
    
    for _, row in df.iterrows():
        # True label: 1 = POTABLE, 0 = NON_POTABLE
        y_true.append(row['Potability'])
        
        # FIS Inference
        res = engine.infer(
            ph=row['ph'], 
            turbidity=row['turbidity'], 
            tds=row['tds'], 
            do=row['do']
        )
        
        # Map FIS output to binary (POTABLE -> 1, MARGINAL/NON-POTABLE -> 0)
        # Note: Kaggle dataset is strictly binary, so we treat MARGINAL as 0 (unsafe/requires treatment)
        pred_label = 1 if res['label'] == 'POTABLE' else 0
        y_pred.append(pred_label)
        
    acc = accuracy_score(y_true, y_pred)
    f1  = f1_score(y_true, y_pred, average="macro")
    
    return {
        "accuracy": round(acc * 100, 2),
        "f1_macro": round(f1 * 100, 2)
    }

def print_comparison(ml_res, fis_res):
    print(f"\n{'═'*65}")
    print("  KAGGLE DATASET BENCHMARK (Real-World Data)")
    print(f"{'─'*65}")
    print(f"  {'Method':<25} {'Accuracy':>10} {'F1-Macro':>10}")
    print(f"{'─'*65}")
    
    print(f"  {'Mamdani FIS (Proposed)':<25} {fis_res['accuracy']:>9.2f}% {fis_res['f1_macro']:>9.2f}%")
    
    for name, res in ml_res.items():
        print(f"  {name:<25} {res['accuracy']:>9.2f}% {res['f1_macro']:>9.2f}%")
    print(f"{'═'*65}\n")

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    df_raw = fetch_dataset()
    df_clean = preprocess_kaggle_data(df_raw)
    
    print("[*] Running ML benchmarks...")
    ml_results = run_ml_classifiers(df_clean)
    
    print("[*] Running FIS inference (this may take a moment)...")
    fis_results = evaluate_fis(df_clean)
    
    print_comparison(ml_results, fis_results)
