# SPDX-License-Identifier: MIT
"""SIMULATED DATA ONLY: invent messages with no motor, sensor or PID model."""

import math

from shared.data_format import SAMPLE_MS
from simulation.settings import SAMPLE_COUNT


def telemetry_lines():
    """Yield 30 simulated seconds immediately; do not wait in real time."""
    enc_left = 0
    enc_right = 0
    for sample in range(1, SAMPLE_COUNT + 1):
        t_ms = sample * SAMPLE_MS
        # Pretend to drive after 2 seconds, then stop for the last 2 seconds.
        driving = 2000 < t_ms <= 28000
        command = math.tau if driving else 0.0  # rad/s; tau = 2*pi.
        if driving:
            enc_left += 2
            # Invent a slightly slower right wheel for later data inspection.
            enc_right += 1 if sample % 5 == 0 else 2

        # These are made-up readings, not outputs from physical equations.
        gyro_z = 0.02 * math.sin(sample / 10) if driving else 0.0
        accel_x = 0.05 * math.sin(sample / 8)
        accel_y = 0.03 * math.cos(sample / 8)
        soil_raw = 1800 + sample % 40
        temp_c = 21.0 + 0.1 * math.sin(sample / 50)
        humidity_pct = 50.0 + math.sin(sample / 30)
        yield (
            f"T,{t_ms},{command:.6f},{command:.6f},{enc_left},{enc_right},"
            f"{gyro_z:.4f},{accel_x:.4f},{accel_y:.4f},{soil_raw},"
            f"{temp_c:.2f},{humidity_pct:.2f}\n"
        )
