// SPDX-License-Identifier: MIT
// Planned milestone 1. No motors, sensors or real telemetry are connected.
#include <Arduino.h>
#include "rover_protocol.h"

constexpr int LINK_RX = 16;
constexpr int LINK_TX = 17;
uint32_t counter = 0;

void setup() {
    Serial.begin(115200);  // USB serial monitor on the DevKit.
    Serial2.begin(115200, SERIAL_8N1, LINK_RX, LINK_TX);
    // Serial2 is reserved for later. This milestone does not read or write it.
    Serial.println("PLANNED MILESTONE 1: counter only, no sensor data");
}

void loop() {
    Serial.print("Counter: ");
    Serial.println(counter++);
    delay(1000);  // One visible count per second. This is not the control loop.
}
