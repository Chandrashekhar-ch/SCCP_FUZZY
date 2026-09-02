"""
main.py
=======
Water Potability FIS - Project Entry Point

Modes:
  python main.py simulate    -> Real-time dashboard with synthetic data stream
  python main.py validate    -> Generate dataset + run FIS + ML benchmarks
  python main.py demo        -> Run FIS inference demo on 5 test cases
  python main.py mf          -> Show membership function sanity check

Author: SC_CProject
"""
import sys, io
# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os

def run_simulate():
    """Start the real-time dashboard in simulation mode."""
    from water_fis.dashboard.server import start_server
    start_server(simulation=True, host="127.0.0.1", port=5050)


def run_demo():
    """Quick FIS inference demo on hardcoded test cases."""
    from water_fis.core.fis_engine import WaterPotabilityFIS
    engine = WaterPotabilityFIS()

    test_cases = [
        (7.0,  0.5, 320.0,  9.0, "Ideal drinking water"),
        (4.5, 60.0, 900.0,  1.5, "Severely contaminated"),
        (7.8,  3.0, 480.0,  7.2, "Borderline - alkaline tendency"),
        (6.8,  0.8, 250.0,  8.0, "Good quality groundwater"),
        (9.5,  0.5, 200.0,  8.0, "Overly alkaline (industrial)"),
        (7.1,  8.0, 520.0,  5.5, "Slightly degraded surface water"),
    ]

    print("\n" + "="*74)
    print("  WATER POTABILITY FIS - INFERENCE DEMO")
    print("="*74)
    hdr = f"  {'Scenario':<34} {'pH':>4} {'Turb':>5} {'TDS':>6} {'DO':>5}  WPI   CLASS"
    print(hdr)
    print("-"*74)
    for ph, turb, tds, do, desc in test_cases:
        result = engine.infer(ph, turb, tds, do)
        icon   = "[SAFE]" if result["label"] == "POTABLE" else ("[WARN]" if result["label"] == "MARGINAL" else "[DANGER]")
        print(
            f"  {desc:<34} {ph:>4.1f} {turb:>5.1f} {tds:>6.0f} {do:>5.1f}"
            f"  {result['wpi']:>5.2f}  {icon} {result['label']}"
        )
    print("="*74 + "\n")


def run_validate():
    """Generate synthetic dataset and run full validation benchmark."""
    import os
    CSV_PATH = "outputs/synthetic_dataset.csv"

    # Step 1: Generate dataset
    print("\n[1/3] Generating synthetic dataset...")
    from water_fis.data.synthetic_generator import generate_dataset
    generate_dataset(n_samples=5000, output_path=CSV_PATH)

    # Step 2: FIS benchmark
    print("[2/3] Running FIS + ML benchmark...")
    from water_fis.validation.ml_benchmark import run_full_benchmark
    run_full_benchmark(CSV_PATH, output_dir="outputs")

    print("[3/3] Done! Check outputs/benchmark_results.json for full results.")


def run_kaggle():
    """Download and benchmark against the real-world Kaggle dataset."""
    from water_fis.validation.kaggle_benchmark import fetch_dataset, preprocess_kaggle_data, run_ml_classifiers, evaluate_fis, print_comparison
    import os
    
    os.makedirs("outputs", exist_ok=True)
    df_raw = fetch_dataset()
    df_clean = preprocess_kaggle_data(df_raw)
    
    print("[*] Running ML benchmarks...")
    ml_results = run_ml_classifiers(df_clean)
    
    print("[*] Running FIS inference (this may take a moment)...")
    fis_results = evaluate_fis(df_clean)
    
    print_comparison(ml_results, fis_results)



def run_mf_check():
    """Show membership function sanity check."""
    from water_fis.core.membership_functions import (
        build_all_mfs, get_membership, UNIVERSES
    )
    import sys, io
    if sys.stdout.encoding not in ('utf-8','UTF-8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    mfs = build_all_mfs()
    tests = [
        ("ph",        7.0,  "Neutral pH"),
        ("ph",        4.5,  "Acidic"),
        ("ph",        9.0,  "Alkaline"),
        ("turbidity", 0.5,  "Clear"),
        ("turbidity", 60.0, "Very Turbid"),
        ("tds",       300., "Acceptable TDS"),
        ("tds",       1200.,"Very High TDS"),
        ("do",        8.0,  "Good DO"),
        ("do",        1.5,  "Very Low DO"),
    ]
    print(f"\n{'═'*60}")
    print("  MEMBERSHIP FUNCTION CHECK")
    print(f"{'═'*60}")
    for param, val, desc in tests:
        print(f"\n  {desc} [{param}={val}]")
        uod = UNIVERSES[param]
        for term, mf in mfs[param].items():
            mu  = get_membership(val, uod, mf)
            bar = "█" * int(mu * 25)
            print(f"    {term:<22} μ={mu:.3f}  {bar}")
    print(f"{'═'*60}\n")


def run_rule_summary():
    """Print rule base summary."""
    from water_fis.core.rule_base import summarise_rule_base
    summarise_rule_base()


# ── CLI dispatch ───────────────────────────────────────────────────
COMMANDS = {
    "simulate": (run_simulate,   "Launch real-time dashboard (simulation mode)"),
    "demo":     (run_demo,       "Run FIS inference on test cases"),
    "validate": (run_validate,   "Generate dataset + run full benchmark"),
    "kaggle":   (run_kaggle,     "Benchmark against real-world Kaggle dataset"),
    "mf":       (run_mf_check,   "Membership function sanity check"),
    "rules":    (run_rule_summary,"Print rule base summary"),
}

def print_help():
    print(f"\n  Water Potability FIS — Command Reference")
    print(f"  {'─'*45}")
    for cmd, (_, desc) in COMMANDS.items():
        print(f"    python main.py {cmd:<12} {desc}")
    print()


if __name__ == "__main__":
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "help"
    if cmd in COMMANDS:
        COMMANDS[cmd][0]()
    else:
        print_help()
