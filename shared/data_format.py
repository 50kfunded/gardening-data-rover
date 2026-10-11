# SPDX-License-Identifier: MIT
"""Shared telemetry contract; currently used only with SIMULATED laptop data."""

import math

COLUMNS = (
    "t_ms", "cmd_left", "cmd_right", "enc_left", "enc_right",
    "gyro_z", "accel_x", "accel_y", "soil_raw", "temp_c", "humidity_pct",
)
INTEGER_FIELDS = {"t_ms", "enc_left", "enc_right", "soil_raw"}
OPTIONAL_FIELDS = set(COLUMNS[5:])  # Missing sensor readings become empty CSV cells.
SCHEMA_VERSION = 2  # Run metadata uses controller names; telemetry fields are unchanged.
TELEMETRY_HZ = 10
SAMPLE_MS = 1000 // TELEMETRY_HZ
MAX_LINE_BYTES = 256
SIMULATION_NOTICE = (
    "# SIMULATED DATA: invented readings; no hardware or real garden measurements."
)


def parse_telemetry(line):
    """Turn T,... into named numbers; check structure and basic numeric ranges."""
    if not line.isascii() or len(line) > MAX_LINE_BYTES:
        raise ValueError("telemetry must be ASCII and at most 256 bytes")
    fields = line.rstrip("\r\n").split(",")
    if len(fields) != len(COLUMNS) + 1 or fields[0] != "T":
        raise ValueError("expected T followed by exactly 11 fields")

    row = {}
    for name, raw in zip(COLUMNS, fields[1:]):
        if raw == "" and name in OPTIONAL_FIELDS:
            row[name] = None
            continue
        try:
            value = int(raw) if name in INTEGER_FIELDS else float(raw)
        except ValueError as error:
            raise ValueError(f"{name}: expected a number, got {raw!r}") from error
        if not math.isfinite(value):
            raise ValueError(f"{name}: NaN and infinity are not readings")
        if name in INTEGER_FIELDS and not 0 <= value <= 4_294_967_295:
            raise ValueError(f"{name}: expected an unsigned 32-bit integer")
        if name == "soil_raw" and value > 4095:
            raise ValueError("soil_raw: expected a 12-bit ADC value (0..4095)")
        if name == "humidity_pct" and not 0 <= value <= 100:
            raise ValueError("humidity_pct: expected 0..100")
        row[name] = value
    return row
