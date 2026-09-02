"""
serial_reader.py
================
Hardware serial bridge: reads sensor packets from ESP32 via UART.

Expected packet format (newline-terminated JSON from ESP32):
    {"ph":7.12,"turb":1.4,"tds":315.0,"do":8.3,"temp":26.2}

Author: SC_CProject
"""

import json, serial, time

_ser = None
_port = "COM3"
_baud = 115200


def init_serial(port: str = "COM3", baud: int = 115200, timeout: float = 2.0):
    global _ser, _port, _baud
    _port, _baud = port, baud
    try:
        _ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(2)  # Allow ESP32 to reset
        print(f"[Serial] Connected to {port} @ {baud} baud")
        return True
    except serial.SerialException as e:
        print(f"[Serial] Failed to connect: {e}")
        return False


def read_serial_packet() -> dict | None:
    """
    Read one JSON packet from the serial port.

    Returns:
        dict: {'ph': float, 'turbidity': float, 'tds': float,
               'do': float, 'temperature': float}
        None: on error or no data
    """
    global _ser
    if _ser is None or not _ser.is_open:
        return None
    try:
        line = _ser.readline().decode("utf-8").strip()
        if not line:
            return None
        raw = json.loads(line)
        # Normalize key names
        return {
            "ph":          float(raw.get("ph",   7.0)),
            "turbidity":   float(raw.get("turb", 1.0)),
            "tds":         float(raw.get("tds",  300.0)),
            "do":          float(raw.get("do",   8.0)),
            "temperature": float(raw.get("temp", 25.0)),
        }
    except (json.JSONDecodeError, ValueError, serial.SerialException):
        return None


def close_serial():
    global _ser
    if _ser and _ser.is_open:
        _ser.close()
        print("[Serial] Connection closed.")
