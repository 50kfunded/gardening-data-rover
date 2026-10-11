# SPDX-License-Identifier: MIT
"""Untested hardware writer. Computer tests and invented inputs must use simulation."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from shared.data_format import COLUMNS, SCHEMA_VERSION, SIMULATION_NOTICE, TELEMETRY_HZ


class RunFiles:
    def __init__(self, root, session_id, part, data_source, first_row, start_reason):
        now = datetime.now(timezone.utc)
        suffix = "sim" if data_source == "simulation" else "hw_untested"
        run_id = f"{session_id}_part{part:03d}_{suffix}"
        self.folder = Path(root) / run_id
        self.folder.mkdir(parents=True, exist_ok=False)  # Never overwrite a run.
        (self.folder / "photos").mkdir()
        self.metadata = {
            "schema_version": SCHEMA_VERSION, "csv_format_version": 2,
            "run_id": run_id, "session_id": session_id, "part": part,
            "date": now.isoformat(timespec="microseconds"), "data_source": data_source,
            "hardware_status": "untested", "surface": None, "battery_type": None,
            "pid_gains": {"left": None, "right": None},
            "notes": ("SIMULATED DATA: invented serial test input, no hardware measurements."
                      if data_source == "simulation" else
                      "Untested hardware logger. Source selected by the operator; not validated."),
            "telemetry_hz": TELEMETRY_HZ, "command_unit": "rad/s",
            "timebase": "controller_boot_ms", "controller_first_ms": first_row["t_ms"],
            "first_received_unix_s": now.timestamp(),
            "time_anchor_status": "receive time only; UART latency and clock drift unmeasured",
            "calibration": {"ticks_per_revolution_left": None,
                            "ticks_per_revolution_right": None, "wheel_radius_left_m": None,
                            "wheel_radius_right_m": None, "track_width_m": None},
            "start_reason": start_reason, "end_reason": None,
            "rows_written": 0, "malformed_lines": 0,
        }
        self.output = (self.folder / "telemetry.csv").open("w", newline="", encoding="utf-8")
        notice = (SIMULATION_NOTICE if data_source == "simulation" else
                  "# HARDWARE DATA: untested logger; validate readings before use.")
        self.output.write(notice + "\n")
        self.writer = csv.DictWriter(self.output, fieldnames=COLUMNS, lineterminator="\n")
        try:
            self.writer.writeheader()
            self.output.flush()
            self.save_metadata()
        except Exception:
            self.output.close()
            raise

    def save_metadata(self):
        temporary = self.folder / "meta.json.tmp"
        temporary.write_text(json.dumps(self.metadata, indent=2, allow_nan=False) + "\n",
                             encoding="utf-8")
        temporary.replace(self.folder / "meta.json")

    def write(self, row):
        self.writer.writerow(row)  # None becomes an empty cell, not zero.
        self.output.flush()
        self.metadata["rows_written"] += 1
        self.metadata["controller_last_ms"] = row["t_ms"]

    def close(self, reason):
        try:
            self.metadata["end_reason"] = reason
            self.metadata["ended_at"] = datetime.now(timezone.utc).isoformat()
            self.save_metadata()
        finally:
            self.output.close()
