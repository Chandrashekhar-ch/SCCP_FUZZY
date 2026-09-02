"""
data_loader.py
==============
Loads historical CSV data or captures live serial data for offline analysis.
"""
import pandas as pd
import json

def load_csv(filepath: str) -> pd.DataFrame:
    """Load sensor data from a CSV file."""
    return pd.read_csv(filepath)

def parse_json_lines(filepath: str) -> pd.DataFrame:
    """Parse a file containing JSON lines (e.g. captured from serial logs)."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
    return pd.DataFrame(data)
