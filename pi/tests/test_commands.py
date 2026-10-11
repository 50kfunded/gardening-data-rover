# SPDX-License-Identifier: MIT
"""SIMULATED commands only. Nothing is sent to a motor or real board."""

import argparse
import unittest

from pi.config import Settings, open_serial, settings_from_args
from pi.send_command import command_bytes, send_command


class CommandTests(unittest.TestCase):
    def test_drive_and_stop_round_trip_through_loopback(self):
        with open_serial(Settings("loop://")) as port:
            drive = send_command(port, "D", 6.283185, -1)
            self.assertEqual(b"D,6.283185,-1.000000\n", drive)
            self.assertEqual(drive, port.read(len(drive)))
            stop = send_command(port, "STOP")
            self.assertEqual(b"STOP\n", port.read(len(stop)))

    def test_bad_or_oversized_commands_are_rejected(self):
        for bad in (float("nan"), float("inf"), 1e250):
            with self.assertRaises(ValueError):
                command_bytes("D", bad, 0)
        for args in (("GO",), ("D", 1), ("STOP", 1, 2)):
            with self.assertRaises(ValueError):
                command_bytes(*args)

    def test_partial_write_is_reported_as_a_failure(self):
        class PartialPort:
            def write(self, line):
                return len(line) - 1
        with self.assertRaises(OSError):
            send_command(PartialPort(), "STOP")

    def test_port_has_no_default_and_loopback_cannot_be_hardware(self):
        args = argparse.Namespace(config=None, port=None, source=None)
        with self.assertRaises(ValueError):
            settings_from_args(args)
        with self.assertRaises(ValueError):
            Settings("loop://", "hardware")
        with self.assertRaises(ValueError):
            Settings("socket://host:1234")
        for duration in (0, -1, float("inf"), True):
            with self.assertRaises(ValueError):
                Settings("loop://", duration_s=duration)


if __name__ == "__main__":
    unittest.main()
