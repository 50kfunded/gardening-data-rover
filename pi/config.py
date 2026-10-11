# SPDX-License-Identifier: MIT
"""Planned serial settings. A port must always be chosen explicitly."""

import json
import math
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    serial_port: str
    data_source: str = "simulation"
    duration_s: float = 30

    def __post_init__(self):
        if not isinstance(self.serial_port, str) or not self.serial_port.strip():
            raise ValueError("set serial_port in a local config or pass --port; there is no default")
        if self.data_source not in ("simulation", "hardware"):
            raise ValueError("data_source must be simulation or hardware")
        if "://" in self.serial_port and self.serial_port != "loop://":
            raise ValueError("only local serial ports and loop:// are supported")
        if self.serial_port == "loop://" and self.data_source != "simulation":
            raise ValueError("loop:// is SIMULATED DATA, never hardware")
        if not isinstance(self.duration_s, (int, float)) or isinstance(self.duration_s, bool):
            raise ValueError("duration_s must be a positive number")
        if not math.isfinite(self.duration_s) or self.duration_s <= 0:
            raise ValueError("duration_s must be a positive finite number")


def add_link_arguments(parser):
    parser.add_argument("--config", type=Path, help="local JSON settings file")
    parser.add_argument("--port", help="explicit COM port, Linux device or loop://")
    parser.add_argument("--source", choices=("simulation", "hardware"))


def settings_from_args(args):
    values = {}
    if args.config:
        values = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(values, dict) or set(values) - {"serial_port", "data_source", "duration_s"}:
            raise ValueError("config must contain only serial_port, data_source and duration_s")
    values = dict(values)
    if args.port is not None:
        values["serial_port"] = args.port
    if args.source is not None:
        values["data_source"] = args.source
    if getattr(args, "duration", None) is not None:
        values["duration_s"] = args.duration
    return Settings(**{"serial_port": None, **values})


def open_serial(settings):
    import serial
    return serial.serial_for_url(settings.serial_port, baudrate=115200, timeout=0.1,
                                 write_timeout=1, bytesize=8, parity="N", stopbits=1)
