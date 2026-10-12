// SPDX-License-Identifier: MIT
// Planned milestone 1. No motors, sensors or real telemetry are connected.
#include <Arduino.h>
#include "rover_protocol.h"

uint32_t counter = 0;

void setup() {
    // Arduino-Pico maps Serial to the BB48's native USB serial connection.
    // 115200 is the monitor setting; it does not clock the USB transport.
    Serial.begin(115200);
    // UART0 (Serial1) on GPIO0 TX / GPIO1 RX is reserved for the Radxa.
    // Leave it and all motor/sensor pins uninitialised for this milestone.
    Serial.println("PLANNED MILESTONE 1: counter only, no sensor data");
}

void loop() {
    Serial.print("Counter: ");
    Serial.println(counter++);
    delay(1000);  // One visible count per second. This is not the control loop.
}
