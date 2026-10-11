// SPDX-License-Identifier: MIT
// SIMULATED command text only. No command reaches a motor.
#include <unity.h>
#include "rover_protocol.h"

void setUp() {}
void tearDown() {}

void stop_clears_a_previous_drive() {
    rover::Command c;
    TEST_ASSERT_TRUE(rover::parse_command("D,2,-3\n", c));
    TEST_ASSERT_TRUE(rover::parse_command("STOP\r\n", c));
    TEST_ASSERT_TRUE(c.type == rover::CommandType::Stop);
    TEST_ASSERT_EQUAL_DOUBLE(0, c.left);
    TEST_ASSERT_EQUAL_DOUBLE(0, c.right);
}

void drive_accepts_signed_decimal_speeds() {
    rover::Command c;
    TEST_ASSERT_TRUE(rover::parse_command("D,6.283185,-2e-1\n", c));
    TEST_ASSERT_TRUE(c.type == rover::CommandType::Drive);
    TEST_ASSERT_DOUBLE_WITHIN(.000001, 6.283185, c.left);
    TEST_ASSERT_DOUBLE_WITHIN(.000001, -.2, c.right);
}

void bad_commands_do_not_keep_a_drive() {
    const char* bad[] = {"", "stop", "D,1", "D,,2", "D,1,2,3", "D,NaN,0",
                        "D,inf,0", "D,1x,0", "D,0x10,1", "D, 1,2", "STOP\nD,1,2"};
    rover::Command c;
    for (const char* line : bad) {
        rover::parse_command("D,1,2", c);
        TEST_ASSERT_FALSE(rover::parse_command(line, c));
        TEST_ASSERT_TRUE(c.type == rover::CommandType::Stop);
    }
    TEST_ASSERT_FALSE(rover::parse_command(std::string("D,1,2\0", 6), c));
    TEST_ASSERT_FALSE(rover::parse_command("D,1,\xff", c));
}

void the_limit_includes_the_line_ending() {
    rover::Command c;
    const std::string line = "D," + std::string(251, '0') + ",0\n";
    TEST_ASSERT_EQUAL_UINT(256, line.size());
    TEST_ASSERT_TRUE(rover::parse_command(line, c));
    TEST_ASSERT_FALSE(rover::parse_command(line + "\n", c));
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(stop_clears_a_previous_drive);
    RUN_TEST(drive_accepts_signed_decimal_speeds);
    RUN_TEST(bad_commands_do_not_keep_a_drive);
    RUN_TEST(the_limit_includes_the_line_ending);
    return UNITY_END();
}
