# Hardware Setup Guide

## 1. Components Required
* ESP32 Development Board
* DFRobot Analog pH Sensor (SEN0161)
* DFRobot Analog Turbidity Sensor (SEN0189)
* DFRobot Analog TDS Sensor (SEN0244)
* DFRobot Analog Dissolved Oxygen Sensor (SEN0237)
* DS18B20 Digital Temperature Sensor
* Jumper wires, breadboard

## 2. Wiring Diagram
* **pH Sensor**: VCC to 3.3V, GND to GND, Signal to GPIO 32
* **Turbidity Sensor**: VCC to 3.3V, GND to GND, Signal to GPIO 33
* **TDS Sensor**: VCC to 3.3V, GND to GND, Signal to GPIO 34
* **DO Sensor**: VCC to 3.3V, GND to GND, Signal to GPIO 35
* **Temp Sensor (DS18B20)**: VCC to 3.3V, GND to GND, Data to GPIO 4 (with 4.7k pull-up resistor)

## 3. Firmware Upload
1. Install Arduino IDE.
2. Install ESP32 board support and `ArduinoJson` library.
3. Open `water_fis/hardware/esp32_firmware.ino`.
4. Select your ESP32 board and COM port.
5. Compile and upload.

## 4. Calibration
Refer to the individual DFRobot sensor wikis for specific calibration fluid procedures (e.g., pH 4.0 and 7.0 buffer solutions).
