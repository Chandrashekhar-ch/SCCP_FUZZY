"""
preprocessor.py
===============
Sensor data preprocessing for the Water Potability FIS.

Operations:
  1. Temperature compensation (pH, DO are temperature-dependent)
  2. Moving average noise filter (window = 10 samples)
  3. Range clamping (clip to sensor universe bounds)
  4. Outlier detection (Z-score based)

Calibration formulas sourced from:
  - DFRobot SEN0161 (pH sensor datasheet)
  - DFRobot SEN0237 (DO sensor datasheet)
  - USGS Water Quality Standards

Author: SC_CProject
"""

import numpy as np
from collections import deque


# ── Temperature compensation constants ────────────────────────────
# pH correction: ~0.003 pH units per °C deviation from 25°C
PH_TEMP_COEFFICIENT    = 0.003   # pH/°C
REFERENCE_TEMP_C       = 25.0   # Calibration reference temperature

# DO saturation at various temps (simplified from Benson & Krause, 1984)
# DO_sat(T) ≈ 14.62 - 0.3898*T + 0.006969*T^2 - 0.00005696*T^3  [mg/L]
DO_SAT_COEFFS = [14.62, -0.3898, 0.006969, -0.00005696]

# Sensor safe operating ranges (from DFRobot datasheets)
SENSOR_BOUNDS = {
    "ph":        (0.0,  14.0),
    "turbidity": (0.0, 100.0),
    "tds":       (0.0, 1500.0),
    "do":        (0.0,  20.0),
    "temperature": (0.0, 50.0),
}


class SensorPreprocessor:
    """
    Real-time preprocessing pipeline for multi-sensor water quality data.

    Usage:
        preprocessor = SensorPreprocessor(window=10)
        cleaned = preprocessor.process(
            ph=7.2, turbidity=1.5, tds=300.0, do=8.0, temperature=28.0
        )
    """

    def __init__(self, window: int = 10, outlier_zscore: float = 3.0):
        """
        Args:
            window       : Moving average window size (samples)
            outlier_zscore: Z-score threshold for outlier rejection
        """
        self.window = window
        self.outlier_thresh = outlier_zscore
        # Circular buffers for each sensor
        self._buffers = {
            param: deque(maxlen=window)
            for param in ["ph", "turbidity", "tds", "do"]
        }
        self._sample_count = 0

    # ─────────────────────────────────────────────────────────────────
    #  TEMPERATURE COMPENSATION
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def compensate_ph(raw_ph: float, temp_c: float) -> float:
        """
        Correct pH for temperature deviation from 25°C calibration point.

        ΔpH = k × (T - T_ref)
        pH_corrected = raw_pH - ΔpH
        """
        delta = PH_TEMP_COEFFICIENT * (temp_c - REFERENCE_TEMP_C)
        return float(np.clip(raw_ph - delta, 0.0, 14.0))

    @staticmethod
    def do_saturation(temp_c: float) -> float:
        """Theoretical DO saturation at temperature T (mg/L, freshwater, 1 atm)."""
        c = DO_SAT_COEFFS
        return c[0] + c[1]*temp_c + c[2]*temp_c**2 + c[3]*temp_c**3

    @staticmethod
    def compensate_do(raw_do: float, temp_c: float) -> float:
        """
        Normalise DO reading to equivalent at 25°C.
        DO_corrected = raw_DO × (DO_sat(25) / DO_sat(T))
        """
        sat_25  = SensorPreprocessor.do_saturation(REFERENCE_TEMP_C)
        sat_t   = SensorPreprocessor.do_saturation(temp_c)
        if sat_t <= 0:
            return raw_do
        corrected = raw_do * (sat_25 / sat_t)
        return float(np.clip(corrected, 0.0, 20.0))

    # ─────────────────────────────────────────────────────────────────
    #  OUTLIER REJECTION (Z-score)
    # ─────────────────────────────────────────────────────────────────
    def _is_outlier(self, value: float, param: str) -> bool:
        buf = list(self._buffers[param])
        if len(buf) < 3:
            return False
        mean = np.mean(buf)
        std  = np.std(buf)
        if std < 1e-6:
            return False
        z = abs((value - mean) / std)
        return z > self.outlier_thresh

    # ─────────────────────────────────────────────────────────────────
    #  MOVING AVERAGE FILTER
    # ─────────────────────────────────────────────────────────────────
    def _update_and_average(self, param: str, value: float) -> float:
        # Replace outliers with last known good value
        if self._is_outlier(value, param) and len(self._buffers[param]) > 0:
            value = self._buffers[param][-1]  # hold last value
        self._buffers[param].append(value)
        return float(np.mean(self._buffers[param]))

    # ─────────────────────────────────────────────────────────────────
    #  RANGE CLAMPING
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    def clamp(value: float, param: str) -> float:
        lo, hi = SENSOR_BOUNDS.get(param, (None, None))
        if lo is not None:
            return float(np.clip(value, lo, hi))
        return value

    # ─────────────────────────────────────────────────────────────────
    #  MAIN PROCESS CALL
    # ─────────────────────────────────────────────────────────────────
    def process(self, ph: float, turbidity: float,
                tds: float, do: float,
                temperature: float = 25.0) -> dict:
        """
        Full preprocessing pipeline for one sensor reading.

        Args:
            ph          : Raw pH reading
            turbidity   : Raw turbidity (NTU)
            tds         : Raw TDS (mg/L)
            do          : Raw dissolved oxygen (mg/L)
            temperature : Water temperature (°C) — used for compensation

        Returns:
            dict with 'ph', 'turbidity', 'tds', 'do' (all cleaned/compensated)
        """
        self._sample_count += 1

        # 1. Clamp to sensor range
        ph          = self.clamp(ph, "ph")
        turbidity   = self.clamp(turbidity, "turbidity")
        tds         = self.clamp(tds, "tds")
        do          = self.clamp(do, "do")
        temperature = self.clamp(temperature, "temperature")

        # 2. Temperature compensation
        ph_comp = self.compensate_ph(ph, temperature)
        do_comp = self.compensate_do(do, temperature)

        # 3. Moving average filter + outlier rejection
        ph_clean   = self._update_and_average("ph", ph_comp)
        turb_clean = self._update_and_average("turbidity", turbidity)
        tds_clean  = self._update_and_average("tds", tds)
        do_clean   = self._update_and_average("do", do_comp)

        return {
            "ph":        round(ph_clean,   3),
            "turbidity": round(turb_clean, 3),
            "tds":       round(tds_clean,  3),
            "do":        round(do_clean,   3),
            "temperature": temperature,
            "sample_n":  self._sample_count,
        }

    def reset(self):
        """Clear all buffers (e.g., on sensor reconnect)."""
        for buf in self._buffers.values():
            buf.clear()
        self._sample_count = 0


def add_sensor_noise(value: float, sigma_pct: float, bound_lo: float, bound_hi: float) -> float:
    """Simulate sensor noise: Gaussian noise at sigma_pct% of the range."""
    noise = np.random.normal(0, sigma_pct / 100.0 * (bound_hi - bound_lo))
    return float(np.clip(value + noise, bound_lo, bound_hi))


if __name__ == "__main__":
    pp = SensorPreprocessor(window=5)
    print("\n── PREPROCESSOR DEMO ──")
    print(f"  Raw pH=7.0 at 30°C → Compensated: {pp.compensate_ph(7.0, 30.0):.3f}")
    print(f"  DO saturation at 25°C: {pp.do_saturation(25.0):.3f} mg/L")
    print(f"  DO saturation at 30°C: {pp.do_saturation(30.0):.3f} mg/L")
    print(f"  DO=8.0 at 30°C → Compensated: {pp.compensate_do(8.0, 30.0):.3f}")

    # Simulate 10 readings
    for i in range(10):
        result = pp.process(7.0 + np.random.normal(0, 0.1), 1.2, 310.0, 8.5, 28.0)
        print(f"  Sample {i+1:02d}: ph={result['ph']:.3f}  turb={result['turbidity']:.2f}"
              f"  tds={result['tds']:.1f}  do={result['do']:.3f}")
