// SPDX-License-Identifier: MIT
// Planned protocol helpers. No Arduino, GPIO, serial or motor calls here.
#pragma once
#include <cstddef>
#include <cstdint>
#include <string>

namespace rover {
constexpr std::size_t MAX_LINE_BYTES = 256;  // Includes the newline.

struct Reading {
    bool present = false;
    double value = 0;
};

struct Telemetry {
    uint32_t t_ms = 0;
    double cmd_left = 0;
    double cmd_right = 0;
    uint32_t enc_left = 0;
    uint32_t enc_right = 0;
    Reading gyro_z, accel_x, accel_y, soil_raw, temp_c, humidity_pct;
};

enum class CommandType { Stop, Drive };
struct Command {
    CommandType type = CommandType::Stop;
    double left = 0;
    double right = 0;
};

// On failure, no partial line or stale drive command is returned.
bool format_telemetry(const Telemetry& sample, std::string& line);
bool parse_command(const std::string& line, Command& command);
}  // namespace rover
