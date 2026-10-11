# SPDX-License-Identifier: MIT
"""Planned serial recording. Only SIMULATED inputs have been tested."""

from datetime import datetime, timezone
from uuid import uuid4

from shared.data_format import parse_telemetry
from pi.line_buffer import LineBuffer
from pi.run_files import RunFiles


def reset_reason(previous, current):
    if previous is None:
        return None
    if current["t_ms"] <= previous["t_ms"]:
        return "time_not_increasing: possible reboot, rollover or repeated packet"
    if current["enc_left"] < previous["enc_left"] or current["enc_right"] < previous["enc_right"]:
        return "encoder_count_decreased: possible reset or rollover"
    return None


def record_chunks(chunks, output_root, data_source="simulation", report=print):
    """Save complete valid frames. A regression starts a separate run folder."""
    if data_source not in ("simulation", "hardware"):
        raise ValueError("choose simulation or hardware explicitly")
    # Windows can return the same clock reading twice. Keep sessions unique.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    session_id = f"{stamp}_serial_{uuid4().hex}"
    frames = LineBuffer()
    stats = {"rows_written": 0, "malformed_lines": 0, "splits": 0, "runs": []}
    current = previous = None
    pending_bad = 0
    end_reason = "input_finished"

    def malformed():
        nonlocal pending_bad
        stats["malformed_lines"] += 1
        if current:
            current.metadata["malformed_lines"] += 1
        else:
            pending_bad += 1

    try:
        for chunk in chunks:
            for line in frames.feed(chunk):
                if line is None:
                    malformed()
                    continue
                try:
                    row = parse_telemetry(line.decode("ascii"))
                except (UnicodeDecodeError, ValueError):
                    malformed()
                    continue
                reason = reset_reason(previous, row)
                if reason:
                    current.close(reason)
                    current = None
                    stats["splits"] += 1
                    report(f"SPLIT: {reason}. Starting a new run; no rows joined across it.")
                if current is None:
                    current = RunFiles(output_root, session_id, len(stats["runs"]) + 1,
                                       data_source, row, reason or "first_valid_line")
                    current.metadata["malformed_lines"] += pending_bad
                    pending_bad = 0
                    stats["runs"].append(current.folder)
                current.write(row)
                stats["rows_written"] += 1
                previous = row
    except KeyboardInterrupt:
        end_reason = "interrupted"
        raise
    except Exception:
        end_reason = "error: recording stopped; no automatic reconnect"
        raise
    finally:
        if frames.finish():
            malformed()
        if current:
            current.close(end_reason)
    return stats
