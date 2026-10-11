// SPDX-License-Identifier: MIT
// Planned pure functions. Test values are SIMULATED DATA, never sensor reads.
#include "rover_protocol.h"
#include <cmath>
#include <iomanip>
#include <locale>
#include <sstream>

namespace rover {
namespace {
bool finite(const Reading& reading) {
    return !reading.present || std::isfinite(reading.value);
}

void append(std::ostringstream& output, const Reading& reading, bool integer = false) {
    output << ',';
    if (reading.present) {
        if (integer) output << static_cast<uint32_t>(reading.value);
        else output << reading.value;
    }
}

bool number(const std::string& text, double& value) {
    // Decimal numbers only. Reject spaces, hex, NaN and trailing junk.
    if (text.empty() || text.find_first_not_of("0123456789+-.eE") != std::string::npos)
        return false;
    std::istringstream input(text);
    input.imbue(std::locale::classic());
    input >> std::noskipws >> value;
    return !input.fail() && input.eof() && std::isfinite(value);
}
}  // namespace

bool format_telemetry(const Telemetry& s, std::string& line) {
    line.clear();
    if (!std::isfinite(s.cmd_left) || !std::isfinite(s.cmd_right) ||
        !finite(s.gyro_z) || !finite(s.accel_x) || !finite(s.accel_y) ||
        !finite(s.soil_raw) || !finite(s.temp_c) || !finite(s.humidity_pct))
        return false;
    if (s.soil_raw.present && (s.soil_raw.value < 0 || s.soil_raw.value > 4095 ||
                              std::floor(s.soil_raw.value) != s.soil_raw.value))
        return false;
    if (s.humidity_pct.present && (s.humidity_pct.value < 0 || s.humidity_pct.value > 100))
        return false;

    std::ostringstream output;
    output.imbue(std::locale::classic());  // Decimal point, never a locale comma.
    output << std::fixed << std::setprecision(6);
    output << "T," << s.t_ms << ',' << s.cmd_left << ',' << s.cmd_right
           << ',' << s.enc_left << ',' << s.enc_right;
    append(output, s.gyro_z);
    append(output, s.accel_x);
    append(output, s.accel_y);
    append(output, s.soil_raw, true);
    append(output, s.temp_c);
    append(output, s.humidity_pct);
    output << '\n';
    const std::string candidate = output.str();
    if (candidate.size() > MAX_LINE_BYTES) return false;
    line = candidate;
    return true;
}

bool parse_command(const std::string& line, Command& command) {
    command = Command();
    if (line.empty() || line.size() > MAX_LINE_BYTES) return false;
    for (unsigned char byte : line) if (byte > 127 || byte == 0) return false;
    std::string text = line;
    if (!text.empty() && text.back() == '\n') text.pop_back();
    if (!text.empty() && text.back() == '\r') text.pop_back();
    if (text == "STOP") return true;
    if (text.compare(0, 2, "D,") != 0) return false;
    const std::size_t comma = text.find(',', 2);
    if (comma == std::string::npos || text.find(',', comma + 1) != std::string::npos)
        return false;
    double left, right;
    if (!number(text.substr(2, comma - 2), left) || !number(text.substr(comma + 1), right))
        return false;
    command.type = CommandType::Drive;
    command.left = left;
    command.right = right;
    return true;
}
}  // namespace rover
