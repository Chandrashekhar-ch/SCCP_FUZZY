/*
 * esp32_firmware.ino
 * ==================
 * Reads analog/digital sensors and broadcasts JSON over serial.
 * Sensors: pH, Turbidity, TDS, DO (simulated/analog), DS18B20 Temp.
 */

#include <ArduinoJson.h>

const int PIN_PH = 32;
const int PIN_TURB = 33;
const int PIN_TDS = 34;
const int PIN_DO = 35;
const int PIN_TEMP = 4; // Assuming DS18B20 on pin 4

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // ESP32 12-bit ADC
}

void loop() {
  // Read analog values (0-4095) and map/convert to actual units
  float ph = map(analogRead(PIN_PH), 0, 4095, 0, 1400) / 100.0;
  float turb = map(analogRead(PIN_TURB), 0, 4095, 0, 1000) / 10.0;
  float tds = map(analogRead(PIN_TDS), 0, 4095, 0, 1500);
  float do_val = map(analogRead(PIN_DO), 0, 4095, 0, 200) / 10.0;
  float temp = 25.0; // Placeholder for actual DS18B20 reading
  
  // Constrain just in case
  ph = constrain(ph, 0.0, 14.0);
  turb = constrain(turb, 0.0, 100.0);
  tds = constrain(tds, 0.0, 1500.0);
  do_val = constrain(do_val, 0.0, 20.0);

  // Construct JSON
  StaticJsonDocument<200> doc;
  doc["ph"] = ph;
  doc["turb"] = turb;
  doc["tds"] = tds;
  doc["do"] = do_val;
  doc["temp"] = temp;

  // Output
  serializeJson(doc, Serial);
  Serial.println();
  
  delay(1000); // 1 Hz sampling
}
