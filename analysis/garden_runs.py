# SPDX-License-Identifier: MIT
"""Read SIMULATED runs on an explicit observation schedule; hardware untested."""

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analysis.read_run import read_run


def utc_time(value):
    result = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(result, datetime) or result.utcoffset() is None:
        raise ValueError("observation times need an explicit timezone")
    return result.astimezone(timezone.utc)


@dataclass(frozen=True)
class Schedule:
    start: datetime
    end: datetime
    interval_s: int = 3600
    batch_samples: int = 9

    def __post_init__(self):
        object.__setattr__(self, "start", utc_time(self.start))
        object.__setattr__(self, "end", utc_time(self.end))
        if self.start >= self.end or (self.end - self.start).total_seconds() > 366 * 86400:
            raise ValueError("need a positive observation window, at most 366 days")
        for name in ("interval_s", "batch_samples"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.interval_s < 60 or self.interval_s > 86400 or 86400 % self.interval_s:
            raise ValueError("visit interval must divide a day, from 60 to 86400 seconds")
        if self.batch_samples > 1000 or (self.batch_samples - 1) * 0.1 >= self.interval_s:
            raise ValueError("batch is too large for the visit interval")
        if self.start.time().isoformat() != "00:00:00" or self.end.time().isoformat() != "00:00:00":
            raise ValueError("use whole UTC days, from midnight to midnight (end exclusive)")


@dataclass(frozen=True)
class Observation:
    at: datetime
    row: dict
    run_id: str


@dataclass(frozen=True)
class RunBoundary:
    at: datetime
    reason: str


def observations_from_run(folder, *, first_observation_utc=None):
    """Map one increasing boot clock, never interpolate across a reboot."""
    metadata, rows = read_run(folder)
    if not rows:
        raise ValueError("empty run: represent a missing visit in the schedule instead")
    if metadata.get("timebase") != "controller_boot_ms":
        raise ValueError("unsupported boot-time basis")
    if first_observation_utc is not None:
        first_at = utc_time(first_observation_utc)
        first_ms = rows[0]["t_ms"]
    elif "first_received_unix_s" in metadata and "controller_first_ms" in metadata:
        anchor = metadata["first_received_unix_s"]
        if isinstance(anchor, bool) or not isinstance(anchor, (int, float)) or not math.isfinite(anchor):
            raise ValueError("invalid receive-time anchor")
        first_at = datetime.fromtimestamp(anchor, timezone.utc)
        first_ms = metadata["controller_first_ms"]
        if first_ms != rows[0]["t_ms"]:
            raise ValueError("first controller anchor doesn't match the first row")
    elif "started_unix_s" in metadata and "controller_t0_ms" in metadata:
        anchor = metadata["started_unix_s"]
        if isinstance(anchor, bool) or not isinstance(anchor, (int, float)) or not math.isfinite(anchor):
            raise ValueError("invalid start-time anchor")
        first_at = datetime.fromtimestamp(anchor, timezone.utc)
        first_ms = metadata["controller_t0_ms"]
        if isinstance(first_ms, bool) or not isinstance(first_ms, int) or not 0 <= first_ms <= rows[0]["t_ms"]:
            raise ValueError("invalid controller start anchor")
    else:
        raise ValueError("not enough data: run has no usable time anchor")

    previous = None
    output = []
    for row in rows:
        if previous and (row["t_ms"] <= previous["t_ms"]
                         or row["enc_left"] < previous["enc_left"]
                         or row["enc_right"] < previous["enc_right"]):
            raise ValueError("unsplit controller regression: split runs before analysis")
        output.append(Observation(first_at + timedelta(milliseconds=row["t_ms"] - first_ms),
                                  row, metadata["run_id"]))
        previous = row
    reason = metadata.get("start_reason", "")
    if not isinstance(reason, str):
        raise ValueError("run start reason must be text")
    boundary = (RunBoundary(output[0].at, reason) if reason.startswith(("time_not_increasing", "encoder_count_decreased"))
                else None)
    return output, boundary


def load_scenario(folder):
    """Read the simulation sidecar, never use its injected-event truth as evidence."""
    root = Path(folder).resolve()
    manifest = json.loads((root / "scenario.json").read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict) or manifest.get("scenario_format_version") != 1
            or manifest.get("data_source") != "simulation"
            or not isinstance(manifest.get("notice"), str)
            or not manifest["notice"].startswith("SIMULATED DATA:")
            or manifest.get("hardware_status") != "untested"):
        raise ValueError("expected a labelled SIMULATED, hardware-untested scenario")
    schedule = Schedule(manifest["start_utc"], manifest["end_utc"],
                        manifest["visit_interval_s"], manifest["batch_samples"])
    entries = manifest.get("runs")
    if not isinstance(entries, list):
        raise ValueError("scenario runs must be a list")
    observations = []
    boundaries = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid run entry")
        name = entry.get("run_id")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+_sim", name) or name in seen:
            raise ValueError("run IDs must be unique safe simulation folder names")
        seen.add(name)
        run_folder = (root / name).resolve()
        if run_folder.parent != root:
            raise ValueError("run must stay inside the scenario directory")
        rows, boundary = observations_from_run(run_folder, first_observation_utc=entry["first_observation_utc"])
        if entry.get("controller_first_ms") != rows[0].row["t_ms"]:
            raise ValueError("fictional anchor doesn't match the run's first boot time")
        observations.extend(rows)
        if boundary:
            boundaries.append(boundary)
    return schedule, observations, boundaries
