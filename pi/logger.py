# SPDX-License-Identifier: MIT
"""Planned serial logger. Hardware operation is untested; loopback is SIMULATED DATA."""

import argparse
import time
from pathlib import Path

from pi.config import PROJECT_DIR, add_link_arguments, open_serial, settings_from_args
from pi.recorder import record_chunks


def read_chunks(port, duration_s):
    """A timeout gives no bytes. It does not end the pending line."""
    deadline = time.monotonic() + duration_s
    while time.monotonic() < deadline:
        yield port.read(64)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_link_arguments(parser)
    parser.add_argument("--duration", type=float, help="record for this many seconds")
    parser.add_argument("--output-root", type=Path, default=PROJECT_DIR / "runs")
    args = parser.parse_args()
    try:
        settings = settings_from_args(args)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print("SIMULATED DATA ONLY" if settings.data_source == "simulation" else
          "PLANNED LOGGER: hardware operation is untested")
    try:
        with open_serial(settings) as port:
            stats = record_chunks(read_chunks(port, settings.duration_s), args.output_root,
                                  settings.data_source)
    except KeyboardInterrupt:
        parser.exit(130, "Stopped. Any opened run has been closed and marked interrupted.\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"FAIL: recording stopped, no automatic reconnect: {error}\n")
    print(f"Saved {stats['rows_written']} rows; dropped {stats['malformed_lines']} malformed lines; "
          f"split {stats['splits']} times.")
    for folder in stats["runs"]:
        print(f"Run: {folder.name}")
    if not stats["rows_written"]:
        parser.exit(1, "FAIL: no valid telemetry received. Milestone 1 only prints a USB counter.\n")
    print("No hardware milestone is passed by this logger.")


if __name__ == "__main__":
    main()
