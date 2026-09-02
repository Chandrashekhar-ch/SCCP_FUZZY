# Fuzzy Inference System for Real-Time Water Potability Classification
### From Low-Cost Multi-Sensor Data

> **A Mamdani Fuzzy Inference System that classifies drinking water safety in real-time using four low-cost IoT sensors — no lab equipment required.**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Sensor Selection & Hardware](#3-sensor-selection--hardware)
4. [FIS Design](#4-fuzzy-inference-system-design)
5. [Installation](#5-installation)
6. [Usage](#6-usage)
7. [Dashboard](#7-real-time-dashboard)
8. [Validation & Results](#8-validation--results)
9. [Project Structure](#9-project-structure)
10. [Standards & References](#10-standards--references)

---

## 1. Project Overview

### Motivation
Conventional water quality monitoring relies on periodic laboratory tests — a process that is expensive, slow, and geographically constrained. This project demonstrates that a **Fuzzy Inference System (FIS)** deployed on a low-cost IoT platform can provide **real-time, interpretable water potability decisions** with nuanced, graded outputs that surpass simple threshold-based methods.

### What This System Does
- **Reads** four sensor inputs: pH, Turbidity, TDS, Dissolved Oxygen
- **Applies** temperature compensation and noise filtering (moving average)
- **Infers** a crisp **Water Potability Index (WPI)** on a 0–10 scale via Mamdani FIS
- **Classifies** output as: 🔴 `NON-POTABLE` | 🟡 `MARGINAL` | 🟢 `POTABLE`
- **Visualises** all results in a premium real-time web dashboard

### Why Fuzzy Logic?
| Approach | Weakness |
|---|---|
| Hard-threshold classifier | Cliff-edge effect at boundaries — tiny measurement change → drastic class jump |
| Neural network (black box) | Not interpretable — cannot be audited or trusted for safety-critical decisions |
| **Mamdani FIS (this project)** | Graded membership, human-readable rules, WHO/BIS grounded, real-time capable |

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     SENSOR LAYER                             │
│  [pH] [Turbidity] [TDS] [DO] [Temperature (compensator)]    │
└────────────────────┬─────────────────────────────────────────┘
                     │ Raw analog/digital readings
┌────────────────────▼─────────────────────────────────────────┐
│              PREPROCESSING (preprocessor.py)                │
│  Temperature compensation → Outlier rejection (Z-score)     │
│  → Moving average filter (N=10) → Range clamping            │
└────────────────────┬─────────────────────────────────────────┘
                     │ Cleaned crisp inputs
┌────────────────────▼─────────────────────────────────────────┐
│         MAMDANI FIS ENGINE (fis_engine.py)                   │
│                                                              │
│  Stage 1: Fuzzification                                      │
│    → Compute μ(x) for all linguistic terms of each input    │
│                                                              │
│  Stage 2: Rule Evaluation (45 rules)                         │
│    → Strength = MIN(antecedent μ values) × weight           │
│                                                              │
│  Stage 3: Implication + Aggregation                          │
│    → Clip output MF at rule strength (MIN implication)      │
│    → MAX across all rule outputs                             │
│                                                              │
│  Stage 4: Defuzzification (Centroid of Area)                 │
│    → WPI = ∫ μ(y)·y dy / ∫ μ(y) dy    ∈ [0, 10]            │
└────────────────────┬─────────────────────────────────────────┘
                     │ WPI score + label + membership data
┌────────────────────▼─────────────────────────────────────────┐
│          REAL-TIME DASHBOARD (Flask + Socket.IO)             │
│  Arc gauge, sensor cards, trend charts, rule activation,     │
│  membership visualization, manual inference panel            │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Sensor Selection & Hardware

### Selected Sensors (DFRobot Gravity Series)

| # | Parameter | Sensor | Cost (INR) | WHO/BIS Limit |
|---|---|---|---|---|
| 1 | **pH** | DFRobot SEN0161 | ~₹1,200 | 6.5 – 8.5 |
| 2 | **Turbidity** | DFRobot SEN0189 | ~₹800 | < 1 NTU (WHO), < 5 NTU (BIS) |
| 3 | **TDS** | DFRobot SEN0244 | ~₹700 | < 500 mg/L (BIS desirable) |
| 4 | **DO** | DFRobot SEN0237 | ~₹2,500 | > 6 mg/L (health benchmark) |
| 5 | **Temperature** | DS18B20 (compensator) | ~₹150 | Calibration use only |

**Total hardware cost: ~₹5,350** (< ₹8,000 low-cost threshold)

### Microcontroller
- **ESP32** (built-in Wi-Fi, 12-bit ADC, 240 MHz dual-core)
- Serial → Python bridge at 115,200 baud
- Packet format: `{"ph":7.12,"turb":1.4,"tds":315.0,"do":8.3,"temp":26.2}`

### Temperature Compensation
- **pH**: ΔpH = 0.003 × (T − 25°C) — corrects for Nernstian drift
- **DO**: DO_corrected = DO_raw × (DO_sat(25°C) / DO_sat(T)) — Benson & Krause model

---

## 4. Fuzzy Inference System Design

### 4.1 FIS Type: Mamdani

**Implication:** MIN | **Aggregation:** MAX | **Defuzzification:** Centroid of Area

### 4.2 Input Variables & Membership Functions

#### pH [0, 14]
| Term | Type | Parameters |
|---|---|---|
| ACIDIC | Trapezoid | [0, 0, 5.0, 6.5] |
| SLIGHTLY_ACIDIC | Triangle | [5.5, 6.5, 7.2] |
| NEUTRAL | Triangle | [6.5, 7.0, 7.8] |
| SLIGHTLY_ALKALINE | Triangle | [7.2, 8.0, 8.8] |
| ALKALINE | Trapezoid | [8.2, 9.0, 14, 14] |

#### Turbidity [0, 100 NTU]
| Term | Type | Parameters |
|---|---|---|
| CLEAR | Trapezoid | [0, 0, 1, 5] |
| SLIGHTLY_TURBID | Triangle | [2, 10, 25] |
| TURBID | Triangle | [15, 40, 70] |
| VERY_TURBID | Trapezoid | [50, 75, 100, 100] |

#### TDS [0, 1500 mg/L]
| Term | Type | Parameters |
|---|---|---|
| PURE | Trapezoid | [0, 0, 100, 300] |
| ACCEPTABLE | Triangle | [150, 350, 550] |
| HIGH | Triangle | [450, 650, 900] |
| VERY_HIGH | Trapezoid | [750, 1000, 1500, 1500] |

#### DO [0, 20 mg/L]
| Term | Type | Parameters |
|---|---|---|
| VERY_LOW | Trapezoid | [0, 0, 2, 4] |
| LOW | Triangle | [3, 5, 7.5] |
| ACCEPTABLE | Triangle | [6, 8.5, 11] |
| HIGH | Trapezoid | [9, 11, 20, 20] |

### 4.3 Output: Water Potability Index [0, 10]
| Term | Type | Parameters | Class |
|---|---|---|---|
| NON_POTABLE | Trapezoid | [0, 0, 2, 3.5] | 🔴 Unsafe |
| MARGINAL | Triangle | [3, 5, 7] | 🟡 Treatment needed |
| POTABLE | Trapezoid | [6.5, 8, 10, 10] | 🟢 Safe |

### 4.4 Rule Base (45 Rules)

Rules are organized into 7 logical groups:

| Group | # Rules | Logic |
|---|---|---|
| Fully Potable (all parameters safe) | 8 | → POTABLE |
| Hard non-potability triggers (single param failure) | 5 | → NON-POTABLE |
| Dual-parameter failures | 4 | → NON-POTABLE |
| Single-parameter boundary violation | 13 | → MARGINAL |
| Turbid + mixed parameters | 4 | → MARGINAL / NON-POTABLE |
| Extreme scenarios | 3 | → NON-POTABLE |
| Multi-parameter boundary cases | 8 | → MARGINAL |

**Sample Rules:**
```
R1: IF (pH=NEUTRAL) AND (Turbidity=CLEAR) AND (TDS=ACCEPTABLE) AND (DO=HIGH)
    THEN WPI = POTABLE  [weight=1.0]

R9: IF (pH=ACIDIC)   THEN WPI = NON_POTABLE  [weight=1.0]   ← Critical trigger

R18: IF (pH=NEUTRAL) AND (Turbidity=SLIGHTLY_TURBID) AND (TDS=ACCEPTABLE) AND (DO=ACCEPTABLE)
     THEN WPI = MARGINAL  [weight=0.80]
```

### 4.5 Defuzzification

**Centroid of Area (CoA):**
```
         ∫ μ_agg(y) · y dy
WPI  =  ──────────────────────
              ∫ μ_agg(y) dy
```

---

## 5. Installation

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone / navigate to project
cd d:\Projects_D\TY_D\SC\SC_CProject

# 2. Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 6. Usage

```bash
# Real-time dashboard (simulation mode — no hardware needed)
python main.py simulate

# Quick FIS demo on 6 test cases
python main.py demo

# Generate 5,000-sample dataset + run full ML benchmark
python main.py validate

# Membership function sanity check
python main.py mf

# Rule base summary
python main.py rules
```

---

## 7. Real-Time Dashboard

After running `python main.py simulate`, open **http://127.0.0.1:5050**

### Dashboard Features

| Panel | Description |
|---|---|
| **WPI Arc Gauge** | Animated arc showing current WPI (0–10) with color zones |
| **Sensor Cards** | Live readings for pH, Turbidity, TDS, DO with status bars |
| **WPI Trend Chart** | 60-second rolling time-series of WPI |
| **Parameter Trends** | Normalized sensor values over time |
| **Membership Visualization** | Current μ(x) for all linguistic terms of each parameter |
| **Active Rules** | Which of the 45 rules are firing and at what strength |
| **Manual Inference** | Slider-based one-shot inference to explore the FIS |
| **Scenario Selector** | Switch between 6 demo scenarios in real-time |

### Scenarios Available
- 🏞️ **Normal** — Typical groundwater
- ✅ **Ideal Potable** — Perfect drinking water
- ⚗️ **Acidic** — Low pH (industrial runoff)
- 🌊 **Turbid** — High suspended particles
- 🪨 **Hard Water** — High TDS + alkaline
- ☠️ **Contaminated** — Worst-case: all parameters fail

---

## 8. Validation & Results

### Method
The FIS is validated against 5,000 synthetic samples labeled by a WHO/BIS hard-threshold oracle, and compared against three ML classifiers.

### Expected Results

| Method | Accuracy | F1-Macro | Interpretable |
|---|---|---|---|
| **Mamdani FIS (proposed)** | ~85–90% | ~83–88% | ✅ Yes |
| Random Forest | ~92–95% | ~91–94% | ❌ No |
| KNN (k=7) | ~88–91% | ~87–90% | ❌ No |
| SVM (RBF) | ~90–93% | ~89–92% | ❌ No |

> **Note:** FIS trades ~5% accuracy for full interpretability — each decision is traceable to specific WHO/BIS-grounded rules. For safety-critical, regulatory, and community-use applications, this interpretability advantage is critical.

### Boundary Region Advantage
FIS is specifically better than threshold classifiers in the **MARGINAL zone** (WPI 3.5–6.5) where hard thresholds produce abrupt, unrealistic decisions. The graded membership approach produces smooth, gradual transitions.

### Run Validation
```bash
python main.py validate
# Output: outputs/benchmark_results.json
```

---

## 9. Project Structure

```
SC_CProject/
├── main.py                          ← Entry point (all modes)
├── config.yaml                      ← Sensor ranges, FIS params, WHO/BIS limits
├── requirements.txt
│
├── water_fis/
│   ├── core/
│   │   ├── membership_functions.py  ← All fuzzy MF definitions
│   │   ├── rule_base.py             ← 45-rule WHO/BIS rule base
│   │   └── fis_engine.py            ← Mamdani FIS engine
│   │
│   ├── data/
│   │   ├── preprocessor.py          ← Temp compensation, noise filter
│   │   └── synthetic_generator.py  ← 5,000-sample labeled dataset generator
│   │
│   ├── validation/
│   │   └── ml_benchmark.py          ← FIS vs. RF/KNN/SVM comparison
│   │
│   ├── dashboard/
│   │   ├── server.py                ← Flask + Socket.IO WebSocket server
│   │   ├── serial_reader.py         ← ESP32 serial bridge (hardware mode)
│   │   └── static/
│   │       ├── index.html           ← Dashboard UI
│   │       ├── style.css            ← Premium dark theme
│   │       └── app.js               ← Real-time client logic
│   │
│   └── hardware/
│       └── esp32_firmware.ino       ← Arduino ESP32 firmware (optional)
│
├── outputs/                         ← Generated datasets + benchmark results
└── docs/                            ← Additional documentation
```

---

## 10. Standards & References

| Standard / Source | Usage |
|---|---|
| WHO Guidelines for Drinking-Water Quality, 4th Ed. (2022) | pH [6.5–8.5], Turbidity [<1 NTU] limits |
| BIS IS 10500:2012 | TDS [500/2000 mg/L], pH [6.5–8.5] Indian standards |
| Zadeh, L.A. (1965). *Fuzzy sets.* Information and Control | FIS mathematical foundation |
| Mamdani, E.H. (1975). *Application of fuzzy algorithms.* IEE Proc. | Mamdani FIS methodology |
| Benson & Krause (1984). DO saturation equations | Temperature-DO compensation |
| DFRobot SEN0161, SEN0189, SEN0244, SEN0237 datasheets | Sensor specs |
| `scikit-fuzzy` Python library | FIS implementation |

---

## License
This project is for educational and research purposes.  
Standards references: WHO 2022, BIS IS 10500:2012.

---

*Fuzzy Inference System for Water Potability Classification · SC_CProject · 2026*
