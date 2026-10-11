// SPDX-License-Identifier: MIT
// Planned milestone 1. No motors, sensors or real telemetry are connected.
#include <Arduino.h>
#include "rover_protocol.h"

uint32_t counter = 0;

void setup() {
    // This board's Arduino core maps Serial to LPUART1, PA2 TX / PA3 RX.
    // The default board routing connects it to the ST-LINK virtual COM port.
    Serial.begin(115200);
    // USART1 on D1 PC4 TX / D0 PC5 RX is reserved for the later Radxa link.
    // Leave it uninitialised here. This milestone only prints the counter.
    Serial.println("PLANNED MILESTONE 1: counter only, no sensor data");
}

void loop() {
    Serial.print("Counter: ");
    Serial.println(counter++);
    delay(1000);  // One visible count per second. This is not the control loop.
}
