# SPDX-License-Identifier: MIT
"""Planned command sender. No motor control or acknowledgement exists yet."""

import argparse
import math

from shared.data_format import MAX_LINE_BYTES
from pi.config import add_link_arguments, open_serial, settings_from_args


def command_bytes(kind, left=None, right=None):
    """Make the existing D/STOP text. Speeds are rad/s, not PWM values."""
    if kind == "STOP" and left is None and right is None:
        return b"STOP\n"
    if kind != "D" or left is None or right is None:
        raise ValueError("use STOP or D with two speeds")
    values = (float(left), float(right))
    if not all(math.isfinite(value) for value in values):
        raise ValueError("speed must be finite")
    line = f"D,{values[0]:.6f},{values[1]:.6f}\n".encode("ascii")
    if len(line) > MAX_LINE_BYTES:
        raise ValueError("command exceeds 256 bytes, including its newline")
    return line


def send_command(port, kind, left=None, right=None):
    """Reuse an already-open handle when the future run script needs both directions."""
    line = command_bytes(kind, left, right)
    if port.write(line) != len(line):
        raise OSError("incomplete command write; no retry or acknowledgement assumed")
    port.flush()
    return line


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_link_arguments(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("STOP")
    drive = subparsers.add_parser("D")
    drive.add_argument("left", type=float)
    drive.add_argument("right", type=float)
    args = parser.parse_args()
    try:
        settings = settings_from_args(args)
        # Validate first, so bad input never opens a real port.
        command_bytes(args.command, getattr(args, "left", None), getattr(args, "right", None))
        with open_serial(settings) as port:
            line = send_command(port, args.command, getattr(args, "left", None),
                                getattr(args, "right", None))
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    label = "SIMULATED command" if settings.data_source == "simulation" else "UNTESTED command"
    print(f"{label}: {line.decode('ascii').strip()}; no acknowledgement checked.")
    print("Milestone 1 firmware ignores commands. No hardware milestone has passed.")


if __name__ == "__main__":
    main()
