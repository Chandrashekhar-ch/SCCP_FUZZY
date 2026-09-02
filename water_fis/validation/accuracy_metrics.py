"""
accuracy_metrics.py
===================
Detailed evaluation metrics: confusion matrices, per-class F1, and boundary analysis.
"""
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pandas as pd

def print_detailed_metrics(y_true, y_pred, labels=None):
    """Prints a detailed classification report and confusion matrix."""
    print("\n--- Detailed Metrics ---")
    print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, labels=labels))
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels) if labels else pd.DataFrame(cm)
    print(cm_df)
    print("------------------------\n")
