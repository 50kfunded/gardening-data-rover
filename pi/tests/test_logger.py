# SPDX-License-Identifier: MIT
"""SIMULATED DATA ONLY: exercise the logger with loopback and fake chunks."""

import csv
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from pi.config import Settings, open_serial
from pi.demo import invented_chunks
from pi.recorder import record_chunks
from shared.data_format import COLUMNS, SIMULATION_NOTICE


def fake_line(t_ms=100, left=0, right=0):
    return f"T,{t_ms},0,0,{left},{right},,,,,,\n".encode("ascii")


def read_files(folder):
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    with (folder / "telemetry.csv").open(newline="", encoding="utf-8") as source:
        notice = source.readline().rstrip("\n")
        rows = list(csv.DictReader(source))
    return meta, notice, rows


class LoggerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="rover-serial-test-")
        self.root = Path(self.temporary.name)
        self.reports = []

    def tearDown(self):
        self.temporary.cleanup()

    def record(self, chunks):
        return record_chunks(chunks, self.root, "simulation", self.reports.append)

    def test_pyserial_loopback_saves_the_same_11_columns_and_missing_cells(self):
        payload = fake_line() + fake_line(200, 1, 2)
        with open_serial(Settings("loop://")) as port:
            port.write(payload)
            chunks = [port.read(7) for _ in range((len(payload) + 6) // 7)]
        result = self.record(chunks)
        meta, notice, rows = read_files(result["runs"][0])
        self.assertEqual(2, result["rows_written"])
        self.assertEqual(list(COLUMNS), list(rows[0]))
        self.assertEqual("", rows[0]["soil_raw"])
        self.assertEqual("0.0", rows[0]["cmd_left"])
        self.assertEqual(SIMULATION_NOTICE, notice)
        self.assertEqual("simulation", meta["data_source"])
        self.assertTrue(meta["run_id"].endswith("_sim"))
        self.assertIn("SIMULATED DATA", meta["notes"])
        self.assertIsNone(meta["pid_gains"]["left"])
        self.assertIsNone(meta["calibration"]["track_width_m"])
        self.assertEqual([], list((result["runs"][0] / "photos").iterdir()))

    def test_timeout_between_fragments_keeps_the_line(self):
        line = fake_line()
        result = self.record([line[:8], b"", b"", line[8:]])
        self.assertEqual(1, result["rows_written"])
        self.assertEqual(0, result["malformed_lines"])

    def test_sessions_stay_separate_when_the_computer_clock_repeats(self):
        with patch("pi.recorder.datetime") as clock:
            clock.now.return_value = datetime(2026, 1, 1, tzinfo=timezone.utc)
            first = self.record([fake_line()])
            second = self.record([fake_line()])
        self.assertNotEqual(first["runs"][0], second["runs"][0])
        self.assertEqual(2, len(list(self.root.iterdir())))

    def test_full_loopback_demo_keeps_all_300_simulated_rows(self):
        result = self.record(invented_chunks())
        self.assertEqual(300, result["rows_written"])
        self.assertEqual(0, result["malformed_lines"])
        self.assertEqual(0, result["splits"])
        meta, notice, rows = read_files(result["runs"][0])
        self.assertEqual(300, len(rows))
        self.assertEqual("simulation", meta["data_source"])
        self.assertEqual(SIMULATION_NOTICE, notice)

    def test_malformed_non_ascii_and_non_finite_frames_are_counted(self):
        result = self.record([b"Counter: 1\n", b"T,\xff\n", b"T,100,NaN,0,0,0,,,,,,\n",
                              fake_line(), b"T,200,0,0,0,0,,,,-1,,\n"])
        self.assertEqual(1, result["rows_written"])
        self.assertEqual(4, result["malformed_lines"])
        self.assertEqual(4, read_files(result["runs"][0])[0]["malformed_lines"])

    def test_oversized_frame_is_dropped_once_including_its_fake_tail(self):
        result = self.record([b"x" * 300, fake_line(), fake_line(200)])
        self.assertEqual(1, result["malformed_lines"])
        self.assertEqual(1, result["rows_written"])

    def test_256_byte_limit_includes_the_newline(self):
        tail = b",0,0,0,0,,,,,,\n"
        exact = b"T," + b"0" * (256 - 2 - len(tail)) + tail
        self.assertEqual(256, len(exact))
        result = self.record([b"T,0" + exact[2:], exact])
        self.assertEqual(1, result["malformed_lines"])
        self.assertEqual(1, result["rows_written"])

    def test_reboot_like_time_reset_starts_a_new_run(self):
        result = self.record([fake_line(1000, 20, 20), fake_line(100, 0, 0)])
        self.assertEqual(1, result["splits"])
        self.assertEqual(2, len(result["runs"]))
        before = read_files(result["runs"][0])
        after = read_files(result["runs"][1])
        self.assertEqual(1, len(before[2]))
        self.assertEqual(1, len(after[2]))
        self.assertIn("time_not_increasing", before[0]["end_reason"])
        self.assertEqual(before[0]["end_reason"], after[0]["start_reason"])
        self.assertEqual(1, len(self.reports))

    def test_each_encoder_reset_splits_even_if_time_increases(self):
        for line in (fake_line(200, 1, 20), fake_line(200, 20, 1)):
            result = self.record([fake_line(100, 20, 20), line])
            self.assertEqual(1, result["splits"])
            self.assertIn("encoder_count_decreased", read_files(result["runs"][0])[0]["end_reason"])

    def test_time_rollover_and_repeated_timestamps_split(self):
        for first, second in ((4294967295, 0), (100, 100)):
            result = self.record([fake_line(first), fake_line(second)])
            self.assertEqual(1, result["splits"])

    def test_incomplete_tail_is_counted_at_shutdown(self):
        result = self.record([fake_line(), b"T,200,0"])
        self.assertEqual(1, result["malformed_lines"])
        self.assertEqual(1, read_files(result["runs"][0])[0]["malformed_lines"])

    def test_serial_failure_closes_the_run_without_reconnecting(self):
        def broken_port():
            yield fake_line()
            raise OSError("simulated disconnect")
        with self.assertRaises(OSError):
            self.record(broken_port())
        folders = list(self.root.iterdir())
        self.assertEqual(1, len(folders))
        meta, _, rows = read_files(folders[0])
        self.assertEqual(1, len(rows))
        self.assertIn("no automatic reconnect", meta["end_reason"])

    def test_no_valid_input_makes_no_run(self):
        result = self.record([b"not telemetry\n"])
        self.assertEqual([], result["runs"])
        self.assertEqual([], list(self.root.iterdir()))

    def test_interrupt_closes_and_labels_the_run(self):
        def interrupted_port():
            yield fake_line()
            raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.record(interrupted_port())
        meta, _, rows = read_files(next(self.root.iterdir()))
        self.assertEqual("interrupted", meta["end_reason"])
        self.assertEqual(1, len(rows))


if __name__ == "__main__":
    unittest.main()
