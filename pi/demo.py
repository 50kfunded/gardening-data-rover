# SPDX-License-Identifier: MIT
"""SIMULATED DATA ONLY: save a loopback demo. No real serial port is opened."""

import argparse
from pathlib import Path

from pi.config import PROJECT_DIR, Settings, open_serial
from pi.recorder import record_chunks
from simulation.fake_controller import telemetry_lines


def invented_chunks():
    # Write and read one line at a time, so loopback's small buffer cannot fill.
    with open_serial(Settings("loop://", "simulation")) as port:
        for line in telemetry_lines():
            payload = line.encode("ascii")
            port.write(payload)
            yield port.read(len(payload))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=PROJECT_DIR / "runs")
    args = parser.parse_args()
    print("SIMULATED DATA ONLY: invented input through pyserial loop://.")
    stats = record_chunks(invented_chunks(), args.output_root, "simulation")
    for folder in stats["runs"]:
        print(f"Created simulated run: {folder.name}")
    print(f"Saved {stats['rows_written']} simulated rows; {stats['malformed_lines']} malformed lines.")
    print("No hardware, physics or timing result. No hardware milestone has passed.")


if __name__ == "__main__":
    main()
