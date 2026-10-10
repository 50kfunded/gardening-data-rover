# SPDX-License-Identifier: MIT
"""Settings for the 30-second SIMULATION, separate from the shared data contract."""

from shared.data_format import TELEMETRY_HZ

DURATION_S = 30
SAMPLE_COUNT = DURATION_S * TELEMETRY_HZ
