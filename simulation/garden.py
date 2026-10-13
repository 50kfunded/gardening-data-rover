# SPDX-License-Identifier: MIT
"""Several weeks of SIMULATED garden visits. No hardware or plant model."""

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pi.recorder import reset_reason
from shared.data_format import COLUMNS, SAMPLE_MS, SCHEMA_VERSION, SIMULATION_NOTICE, TELEMETRY_HZ, parse_telemetry

NOTICE = "SIMULATED DATA: fictional garden dates, readings and faults; hardware untested."
BATCH_SAMPLES = 9


@dataclass(frozen=True)
class GardenConfig:
    weeks: int = 6
    seed: int = 42
    drift_counts_per_day: float = 2.0
    faults: bool = True
    changes: bool = True
    rain_days: tuple[int, ...] = (3, 10, 17, 28, 35)

    def __post_init__(self):
        if isinstance(self.weeks, bool) or not isinstance(self.weeks, int) or not 1 <= self.weeks <= 12:
            raise ValueError("weeks must be an integer from 1 to 12")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise ValueError("seed must be an integer")
        if (isinstance(self.drift_counts_per_day, bool)
                or not isinstance(self.drift_counts_per_day, (int, float))
                or not math.isfinite(self.drift_counts_per_day)
                or abs(self.drift_counts_per_day) > 20):
            raise ValueError("drift must be finite and at most 20 counts/day in magnitude")
        if not isinstance(self.faults, bool) or not isinstance(self.changes, bool):
            raise ValueError("faults and changes must be booleans")
        if any(isinstance(day, bool) or not isinstance(day, int) or day < 0 for day in self.rain_days):
            raise ValueError("rain days must be non-negative integer day offsets")


def garden_batches(config=GardenConfig()):
    """Yield hourly nine-row 10 Hz bursts, with truth labels outside telemetry."""
    rng = random.Random(config.seed)
    boot_hour = 0
    for day in range(config.weeks * 7):
        for hour in range(24):
            elapsed_hour = day * 24 + hour
            labels = []
            if config.faults and (day == 31 or (day == 30 and 4 <= hour < 10)):
                yield day, hour, [], ["telemetry_gap"]
                continue
            if config.faults and day == 32 and hour == 12:
                boot_hour = elapsed_hour
                labels.append("controller_reboot")

            # Invented daily recharge/drying cycle; not soil physics or irrigation advice.
            daylight_hours = min(12, max(0, hour - 6))
            drying = 1.2
            if config.changes and 14 <= day <= 20:
                drying = 3.2
                labels.append("faster_drying")
            moisture = 70 - drying * daylight_hours + 0.4 * math.sin(day * 0.7)
            if config.changes and 21 <= day <= 23:
                moisture = 94 - 0.1 * daylight_hours
                labels.append("wet_period")
            raining = day in config.rain_days and hour >= 5
            if raining:
                moisture = min(98, moisture + 18)
                labels.append("rain_event")
            temp = 18 + 6 * math.sin((hour - 8) * math.tau / 24) + 0.04 * day
            humidity = 65 - 15 * math.sin((hour - 8) * math.tau / 24) + (12 if raining else 0)
            raw_centre = 3000 - 20 * moisture + day * config.drift_counts_per_day
            if config.drift_counts_per_day:
                labels.append("slow_sensor_drift")

            rows = []
            for sample in range(BATCH_SAMPLES):
                raw = round(raw_centre + rng.gauss(0, 2))
                if config.faults:
                    if day in (24, 25):
                        raw = 1800
                        labels.append("stuck_sensor")
                    elif day == 26:
                        raw += (-160, -120, -80, -40, 0, 40, 80, 120, 160)[sample]
                        labels.append("noisy_sensor")
                    elif day == 27 and sample == 0:
                        raw = 3900 if hour % 2 else 100
                        labels.append("spike")
                    if day == 29 and 8 <= hour < 16:
                        raw = None
                        labels.append("soil_dropout")
                raw = None if raw is None else max(0, min(4095, raw))
                boot_ms = ((elapsed_hour - boot_hour) * 3_600_000 + (sample + 1) * SAMPLE_MS) % (2**32)
                cells = [boot_ms, 0, 0, 0, 0, 0, 0, 0, raw,
                         round(temp + rng.gauss(0, 0.05), 2),
                         round(max(0, min(100, humidity + rng.gauss(0, 0.1))), 2)]
                line = "T," + ",".join("" if value is None else str(value) for value in cells) + "\n"
                rows.append(parse_telemetry(line))
            yield day, hour, rows, sorted(set(labels))


def _save_part(root, run_id, rows, reason, generated):
    folder = root / run_id
    folder.mkdir(exist_ok=False)
    (folder / "photos").mkdir()
    metadata = {
        "schema_version": SCHEMA_VERSION, "csv_format_version": 2,
        "run_id": run_id, "date": generated.isoformat(), "data_source": "simulation",
        "hardware_status": "untested", "surface": "simulated; one fictional soil location",
        "battery_type": "none", "pid_gains": {"left": None, "right": None},
        "notes": NOTICE + " Hourly visits, nine 10 Hz samples each; not continuous telemetry.",
        "telemetry_hz": TELEMETRY_HZ, "command_unit": "rad/s",
        "timebase": "controller_boot_ms", "controller_first_ms": rows[0]["t_ms"],
        "controller_last_ms": rows[-1]["t_ms"], "first_received_unix_s": generated.timestamp(),
        "time_anchor_status": "generation time only; fictional timeline is in scenario.json",
        "start_reason": reason, "end_reason": "simulated_visit_group_finished",
        "rows_written": len(rows), "malformed_lines": 0,
        "calibration": {"ticks_per_revolution_left": None, "ticks_per_revolution_right": None,
                        "wheel_radius_left_m": None, "wheel_radius_right_m": None, "track_width_m": None},
    }
    (folder / "meta.json").write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (folder / "telemetry.csv").open("w", newline="", encoding="utf-8") as output:
        output.write(SIMULATION_NOTICE + "\n")
        writer = csv.DictWriter(output, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_garden(output_dir, config=GardenConfig()):
    """Make a new directory, preserving the existing telemetry/metadata versions."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=False)
    start = datetime(2026, 1, 5, tzinfo=timezone.utc)  # Fictional Monday, never a real garden visit.
    generated = datetime.now(timezone.utc)
    manifest = {
        "scenario_format_version": 1, "data_source": "simulation", "notice": NOTICE,
        "hardware_status": "untested", "location": "one fictional soil location",
        "start_utc": start.isoformat(),
        "end_utc": (start + timedelta(weeks=config.weeks)).isoformat(),
        "visit_interval_s": 3600, "batch_samples": BATCH_SAMPLES,
        "seed": config.seed, "runs": [], "injected_events": [],
    }
    current_day = None
    rows = []
    first_time = None
    reason = "first_valid_line"
    part = 0

    def save():
        nonlocal part, rows
        if not rows:
            return
        part += 1
        run_id = f"garden_day{current_day:03d}_part{part:03d}_sim"
        _save_part(root, run_id, rows, reason, generated)
        manifest["runs"].append({"run_id": run_id,
                                 "first_observation_utc": first_time.isoformat(),
                                 "controller_first_ms": rows[0]["t_ms"]})
        rows = []

    for day, hour, batch, labels in garden_batches(config):
        visit = start + timedelta(days=day, hours=hour)
        if labels:
            manifest["injected_events"].append({"at_utc": visit.isoformat(), "labels": labels})
        if not batch:
            continue
        split = reset_reason(rows[-1], batch[0]) if rows else None
        if day != current_day or split:
            save()
            reason = split or "scheduled_day_group"
            current_day = day
        if not rows:
            first_time = visit + timedelta(milliseconds=SAMPLE_MS)
        rows.extend(batch)
    save()
    (root / "scenario.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("runs/garden_sim"))
    parser.add_argument("--weeks", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    try:
        root = write_garden(args.output_dir, GardenConfig(weeks=args.weeks, seed=args.seed))
    except (OSError, ValueError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print(NOTICE)
    print(f"Created {args.weeks} fictional weeks in {root}. No real waiting or hardware.")
    print("scenario.json provides the fake clock and visit schedule; meta.json dates are generation times.")
    print(f'Next: python3 -m analysis.weekly_report "{root}" --dry-raw 3000 --wet-raw 1000')
    print("Those calibration endpoints are invented for this fixture, not hardware settings.")


if __name__ == "__main__":
    main()
