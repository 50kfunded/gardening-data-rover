# SPDX-License-Identifier: MIT
"""SIMULATED DATA ONLY: save invented readings using Python's standard library."""

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from shared.data_format import (
    COLUMNS, SCHEMA_VERSION, SIMULATION_NOTICE, TELEMETRY_HZ,
    parse_telemetry,
)
from simulation.fake_controller import telemetry_lines
from simulation.settings import DURATION_S, SAMPLE_COUNT

PROJECT_DIR = Path(__file__).resolve().parents[1]


def write_run(output_root, run_id=None):
    """Create a new simulation folder. Never overwrite an earlier run."""
    started = datetime.now(timezone.utc)
    run_id = run_id or started.strftime("%Y%m%dT%H%M%S_%fZ_sim")
    if not re.fullmatch(r"[A-Za-z0-9_-]+_sim", run_id):
        raise ValueError("run_id must contain letters, digits, _ or - and end in _sim")
    run_dir = Path(output_root) / run_id
    # Refuse any existing run folder, even one whose photos folder is missing.
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "photos").mkdir()

    metadata = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "date": started.isoformat(timespec="microseconds"),
        "data_source": "simulation",
        "csv_format_version": 2,
        "surface": "simulated; no physical surface",
        "battery_type": "none",
        "pid_gains": {"left": None, "right": None},
        "notes": "SIMULATED DATA: invented readings. No garden, hardware, physics or PID model.",
        "telemetry_hz": TELEMETRY_HZ,
        "duration_s": DURATION_S,
        "expected_rows": SAMPLE_COUNT,
        "timebase": "controller_boot_ms",
        "controller_t0_ms": 0,
        "started_unix_s": started.timestamp(),
        "command_unit": "rad/s",
        "calibration": {
            "ticks_per_revolution_left": None,
            "ticks_per_revolution_right": None,
            "wheel_radius_left_m": None,
            "wheel_radius_right_m": None,
            "track_width_m": None,
        },
    }
    with (run_dir / "meta.json").open("w", encoding="utf-8") as output:
        json.dump(metadata, output, indent=2, allow_nan=False)
        output.write("\n")

    with (run_dir / "telemetry.csv").open("w", newline="", encoding="utf-8") as output:
        # Label the CSV itself, so copying it without meta.json cannot hide its source.
        output.write(SIMULATION_NOTICE + "\n")
        writer = csv.DictWriter(output, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        for line in telemetry_lines():
            writer.writerow(parse_telemetry(line))
    return run_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=PROJECT_DIR / "runs")
    parser.add_argument("--run-id", help="optional safe folder name ending in _sim")
    arguments = parser.parse_args()
    try:
        run_dir = write_run(arguments.output_root, arguments.run_id)
    except (OSError, ValueError) as error:
        parser.exit(1, f"FAIL: {error}\n")

    print(f"Created: {run_dir}")
    print(f"Wrote {SAMPLE_COUNT} simulated samples covering {DURATION_S} seconds.")
    print("SIMULATION ONLY: no hardware was connected. photos/ is empty.")
    print(f'Next: python -m simulation.verify_run "{run_dir}"')


if __name__ == "__main__":
    main()
