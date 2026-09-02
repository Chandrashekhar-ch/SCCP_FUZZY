"""
server.py
=========
Flask + Flask-SocketIO WebSocket server for the real-time dashboard.

Modes:
  simulation=True  → streams synthetic data from SyntheticStream
  simulation=False → reads from ESP32 via serial port (hardware mode)

Run:
    python -m water_fis.dashboard.server
    # Open http://127.0.0.1:5050 in browser

Author: SC_CProject
"""

import os, time, json, threading, random
import numpy as np
from datetime import datetime
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit

from water_fis.core.fis_engine import WaterPotabilityFIS
from water_fis.data.preprocessor import SensorPreprocessor

# ── App setup ─────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")

app       = Flask(__name__, static_folder=STATIC_DIR, template_folder=STATIC_DIR)
app.config["SECRET_KEY"] = "water-fis-2026"
socketio  = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ── FIS Engine & Preprocessor ─────────────────────────────────────
fis_engine    = WaterPotabilityFIS()
preprocessor  = SensorPreprocessor(window=10)

# ── Simulation state ───────────────────────────────────────────────
class SyntheticStream:
    """
    Generates realistic synthetic water quality readings
    that vary smoothly over time (simulates a field sensor).
    """
    # Target values (drift towards these over time)
    _targets = {"ph": 7.1, "turbidity": 1.2, "tds": 310.0, "do": 8.5, "temperature": 26.0}
    _current = {"ph": 7.1, "turbidity": 1.2, "tds": 310.0, "do": 8.5, "temperature": 26.0}
    _tick = 0
    _scenario_timer = 0
    _scenario = "normal"

    BOUNDS = {
        "ph": (0., 14.), "turbidity": (0., 100.),
        "tds": (0., 1500.), "do": (0., 20.), "temperature": (0., 50.)
    }
    NOISE = {
        "ph": 0.05, "turbidity": 0.15, "tds": 2.0,
        "do": 0.08, "temperature": 0.10
    }

    # Scenario presets for demo variety
    SCENARIOS = {
        "normal":      {"ph":7.1, "turbidity":1.0, "tds":320., "do":8.5,  "temperature":25.},
        "acidic":      {"ph":4.8, "turbidity":5.0, "tds":450., "do":7.0,  "temperature":27.},
        "turbid":      {"ph":7.2, "turbidity":65., "tds":500., "do":6.5,  "temperature":26.},
        "contaminated":{"ph":5.2, "turbidity":55., "tds":900., "do":2.0,  "temperature":30.},
        "hard_water":  {"ph":8.8, "turbidity":2.0, "tds":750., "do":7.2,  "temperature":24.},
        "potable":     {"ph":7.0, "turbidity":0.5, "tds":280., "do":9.0,  "temperature":23.},
    }

    @classmethod
    def next(cls) -> dict:
        cls._tick += 1
        cls._scenario_timer += 1

        # Rotate scenario every ~45 seconds for demo
        if cls._scenario_timer >= 45:
            cls._scenario_timer = 0
            keys = list(cls.SCENARIOS.keys())
            idx  = keys.index(cls._scenario)
            cls._scenario = keys[(idx + 1) % len(keys)]
            cls._targets  = dict(cls.SCENARIOS[cls._scenario])

        # Drift toward target (first-order lag)
        for p in cls._current:
            lo, hi = cls.BOUNDS[p]
            drift = (cls._targets[p] - cls._current[p]) * 0.08
            noise = np.random.normal(0, cls.NOISE[p])
            cls._current[p] = float(np.clip(cls._current[p] + drift + noise, lo, hi))

        return dict(cls._current)


# ── Broadcast loop ─────────────────────────────────────────────────
_streaming = False

def broadcast_loop(simulation: bool = True, interval: float = 1.0):
    global _streaming
    _streaming = True
    while _streaming:
        try:
            if simulation:
                raw = SyntheticStream.next()
            else:
                from water_fis.dashboard.serial_reader import read_serial_packet
                raw = read_serial_packet()
                if raw is None:
                    time.sleep(interval)
                    continue

            # Preprocess
            cleaned = preprocessor.process(**raw)

            # FIS Inference
            result = fis_engine.infer(
                ph=cleaned["ph"], turbidity=cleaned["turbidity"],
                tds=cleaned["tds"], do=cleaned["do"]
            )

            # Build payload
            payload = {
                "timestamp":       datetime.now().isoformat(),
                "raw":             raw,
                "processed":       cleaned,
                "wpi":             result["wpi"],
                "label":           result["label"],
                "color":           result["color"],
                "n_rules_fired":   result["n_rules_fired"],
                "membership_map":  result["membership_map"],
                "activated_rules": [
                    {"id": r["rule_id"], "strength": round(r["strength"], 3),
                     "consequence": r["consequence"]}
                    for r in result["activated_rules"][:10]  # top 10
                ],
                "scenario":        SyntheticStream._scenario if simulation else "live",
            }

            socketio.emit("sensor_update", payload)

        except Exception as e:
            socketio.emit("error", {"message": str(e)})

        time.sleep(interval)


# ── Routes ─────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


# ── Socket events ──────────────────────────────────────────────────
@socketio.on("connect")
def on_connect():
    emit("connected", {"message": "Water Potability FIS Dashboard connected."})

@socketio.on("disconnect")
def on_disconnect():
    pass

@socketio.on("set_scenario")
def on_set_scenario(data):
    scenario = data.get("scenario", "normal")
    if scenario in SyntheticStream.SCENARIOS:
        SyntheticStream._scenario = scenario
        SyntheticStream._targets  = dict(SyntheticStream.SCENARIOS[scenario])
        emit("scenario_set", {"scenario": scenario})

@socketio.on("manual_infer")
def on_manual_infer(data):
    """Allow manual one-shot inference from the dashboard sliders."""
    try:
        cleaned = preprocessor.process(
            ph=float(data["ph"]),
            turbidity=float(data["turbidity"]),
            tds=float(data["tds"]),
            do=float(data["do"]),
            temperature=float(data.get("temperature", 25.0)),
        )
        result = fis_engine.infer(**{k: cleaned[k] for k in ["ph","turbidity","tds","do"]})
        emit("manual_result", {
            "wpi":   result["wpi"],
            "label": result["label"],
            "color": result["color"],
            "n_rules_fired": result["n_rules_fired"],
        })
    except Exception as e:
        emit("error", {"message": str(e)})


# ── Entry point ────────────────────────────────────────────────────
def start_server(simulation: bool = True, host: str = "127.0.0.1",
                 port: int = 5050, update_interval: float = 1.0):
    thread = threading.Thread(
        target=broadcast_loop,
        args=(simulation, update_interval),
        daemon=True
    )
    thread.start()
    print(f"\n  Water Potability FIS Dashboard")
    print(f"  URL: http://{host}:{port}")
    print(f"  Mode: {'SIMULATION' if simulation else 'LIVE SENSOR'}")
    print(f"  Press Ctrl+C to stop.\n")
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    start_server(simulation=True)
