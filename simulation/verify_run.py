# SPDX-License-Identifier: MIT
"""SIMULATION ONLY: check a saved fake run. This cannot pass a hardware milestone."""

import argparse
from datetime import datetime
from pathlib import Path

from analysis.read_run import read_run
from shared.data_format import SAMPLE_MS, TELEMETRY_HZ
from simulation.settings import DURATION_S, SAMPLE_COUNT

PROJECT_DIR = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(run_dir):
    run_dir = Path(run_dir)
    metadata, rows = read_run(run_dir)
    require(metadata["data_source"] == "simulation", "expected simulated data")
    for field in ("date", "surface", "battery_type", "pid_gains", "notes"):
        require(field in metadata, f"meta.json is missing {field}")
    require(datetime.fromisoformat(metadata["date"]).utcoffset() is not None,
            "date must include its timezone")
    require(metadata["command_unit"] == "rad/s", "wrong command unit")
    require(metadata["telemetry_hz"] == TELEMETRY_HZ and metadata["duration_s"] == DURATION_S,
            "this milestone expects 30 simulated seconds at 10 Hz")
    require(metadata["expected_rows"] == SAMPLE_COUNT, "expected_rows must be 300")
    require((run_dir / "photos").is_dir(), "photos/ folder is missing")
    # Git cannot track an empty folder; the committed example uses a text placeholder.
    require(all(path.name == ".gitkeep" and path.is_file()
                for path in (run_dir / "photos").iterdir()),
            "simulation photos/ must contain no photos")

    previous_ms = metadata["controller_t0_ms"]
    previous_left = previous_right = 0
    for sample_number, row in enumerate(rows, start=1):
        require(row["t_ms"] - previous_ms == SAMPLE_MS,
                f"sample {sample_number}: missing, repeated or out-of-order sample")
        require(row["enc_left"] >= previous_left and row["enc_right"] >= previous_right,
                f"sample {sample_number}: raw pulse counts went backwards")
        previous_ms = row["t_ms"]
        previous_left, previous_right = row["enc_left"], row["enc_right"]

    require(len(rows) == SAMPLE_COUNT, f"expected 300 rows, found {len(rows)}")
    if metadata.get("csv_format_version", 1) == 1:
        print("LEGACY SIMULATION: this older CSV has no source notice; keep meta.json with it.")
    print("PASS: 300 valid rows, 11 columns, timestamps 100 ms apart.")
    print("PASS: raw encoder counts never decrease; metadata and photos/ are present.")
    print("SIMULATION ONLY: this does not test real sensors, UART, motors or timing.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_folder", help="the folder printed by python -m simulation.simulate_run")
    arguments = parser.parse_args()
    run_dir = Path(arguments.run_folder)
    if not run_dir.is_absolute():
        run_dir = PROJECT_DIR / run_dir
    try:
        verify(run_dir)
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        print(f"FAIL: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
