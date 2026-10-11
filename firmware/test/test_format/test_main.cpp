// SPDX-License-Identifier: MIT
// SIMULATED DATA ONLY. These checks cannot pass a hardware milestone.
#include <unity.h>
#include "rover_protocol.h"
#include <limits>

void setUp() {}
void tearDown() {}

void missing_readings_stay_empty() {
    rover::Telemetry s;
    s.t_ms = 100;
    std::string line;
    TEST_ASSERT_TRUE(rover::format_telemetry(s, line));
    TEST_ASSERT_EQUAL_STRING("T,100,0.000000,0.000000,0,0,,,,,,\n", line.c_str());
}

void readings_keep_the_contract_order() {
    rover::Telemetry s;
    s.t_ms = 1000; s.cmd_left = 6.283185; s.cmd_right = -1;
    s.enc_left = 20; s.enc_right = 18;
    s.gyro_z.present = s.accel_x.present = s.accel_y.present = true;
    s.soil_raw.present = s.temp_c.present = s.humidity_pct.present = true;
    s.gyro_z.value = .01; s.accel_x.value = .02;
    s.soil_raw.value = 1800; s.temp_c.value = 21.5; s.humidity_pct.value = 48;
    std::string line;
    TEST_ASSERT_TRUE(rover::format_telemetry(s, line));
    TEST_ASSERT_EQUAL_STRING(
        "T,1000,6.283185,-1.000000,20,18,0.010000,0.020000,0.000000,1800,21.500000,48.000000\n",
        line.c_str());
}

void invalid_values_are_rejected() {
    rover::Telemetry s;
    std::string line = "stale";
    s.soil_raw.present = true; s.soil_raw.value = 4096;
    TEST_ASSERT_FALSE(rover::format_telemetry(s, line));
    TEST_ASSERT_TRUE(line.empty());
    s.soil_raw.value = 1.5;
    TEST_ASSERT_FALSE(rover::format_telemetry(s, line));
    s.soil_raw.present = false; s.humidity_pct.present = true; s.humidity_pct.value = 101;
    TEST_ASSERT_FALSE(rover::format_telemetry(s, line));
    s.humidity_pct.present = false; s.cmd_left = std::numeric_limits<double>::infinity();
    TEST_ASSERT_FALSE(rover::format_telemetry(s, line));
}

void too_long_a_line_is_not_truncated() {
    rover::Telemetry s;
    s.cmd_left = 1e250;
    std::string line;
    TEST_ASSERT_FALSE(rover::format_telemetry(s, line));
    TEST_ASSERT_TRUE(line.empty());
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(missing_readings_stay_empty);
    RUN_TEST(readings_keep_the_contract_order);
    RUN_TEST(invalid_values_are_rejected);
    RUN_TEST(too_long_a_line_is_not_truncated);
    return UNITY_END();
}
