# How to Run: Water Potability FIS Project

This guide provides step-by-step instructions on how to set up the environment and run all the different modes of the Fuzzy Inference System (FIS) project.

---

## 1. Initial Setup

### Prerequisites
Make sure you have **Python 3.10+** installed on your system.

### Install Dependencies
Open your terminal in the project directory (`SC_CProject`) and run:
```powershell
# It is highly recommended to use a virtual environment, though optional:
# python -m venv .venv
# .venv\Scripts\activate

# Install all required Python packages
pip install -r requirements.txt
pip install python-pptx seaborn
```
*(Note: If you run into encoding issues on Windows, you can force UTF-8 output by prefixing commands with `$env:PYTHONIOENCODING='utf-8';`)*

---

## 2. Running the Core Application

We use `main.py` as the central entry point for the entire project.

### 🌐 A. Real-Time Dashboard (Simulation Mode)
To launch the interactive web dashboard that visualizes the FIS engine in real-time:
```powershell
python main.py simulate
```
* **Action:** Open your web browser and navigate to **http://127.0.0.1:5050**
* **Features:** Live WPI arc gauge, animated rule evaluation, and real-time sensor plotting.

### ⚡ B. Quick Terminal Demo
To run a quick sanity check of the FIS engine against 6 hard-coded water scenarios (e.g., "Ideal drinking water", "Severely contaminated"):
```powershell
python main.py demo
```

### 📏 C. Membership Function Visualization
To print out the calculated membership degrees (μ) for specific inputs, showing how the Fuzzification stage works:
```powershell
python main.py mf
```

### 📜 D. Rule Base Summary
To print all 45 WHO/BIS-grounded fuzzy rules to the console:
```powershell
python main.py rules
```

---

## 3. Running Benchmarks & Validations

The project compares our Fuzzy Logic approach against traditional Machine Learning models (Random Forest, SVM, KNN).

### 🧪 A. Synthetic Dataset Validation
This command generates a 5,000-sample synthetic dataset with sensor noise and evaluates the FIS against standard ML models:
```powershell
python main.py validate
```
* **Outputs:** 
  - `outputs/synthetic_dataset.csv`
  - `outputs/benchmark_results.json`

### 🌍 B. Real-World (Kaggle) Dataset Benchmark
This command downloads a real-world water potability dataset from a public GitHub repository and runs the benchmark to prove the FIS engine's viability on noisy, real data:
```powershell
python main.py kaggle
```
* **Outputs:** 
  - `outputs/kaggle_water_potability.csv`

---

## 4. Generating Academic Outputs

The project includes scripts to auto-generate plots and a PowerPoint presentation.

### 📊 A. Generate Plots
To generate high-resolution PNG images of the Membership Functions and Benchmark results:
```powershell
python water_fis/validation/plot_figures.py
```
* **Outputs:** Saved to `outputs/figures/`

### 📽️ B. Generate PowerPoint Presentation
To auto-generate a `.pptx` presentation summarizing the project and embedding the generated plots:
```powershell
python docs/generate_ppt.py
```
* **Outputs:** `outputs/Water_Potability_FIS_Presentation.pptx`

---

## 5. Hardware Deployment (ESP32)

If you are transitioning from the simulation dashboard to real hardware:
1. Open the Arduino IDE.
2. Load the sketch located at: `water_fis/hardware/esp32_firmware.ino`
3. Flash the code to your ESP32 board.
4. In `water_fis/dashboard/server.py`, change `simulation=True` to `simulation=False` and update the COM port to match your ESP32.
5. Run `python main.py simulate` to read live data from the physical sensors!
