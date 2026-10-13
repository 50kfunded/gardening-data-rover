# SPDX-License-Identifier: MIT
"""SIMULATED soil, weekly, watering and generated-image dataset checks only."""

import unittest
from pathlib import Path


def main():
    print("SIMULATED DATA ONLY: invented calibration/garden faults and generated dataset pixels.", flush=True)
    root = Path(__file__).resolve().parents[1]
    tests = unittest.defaultTestLoader.discover(str(root / "analysis" / "tests"),
                                              top_level_dir=str(root))
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("PASS: simulated analysis/dataset checks only. Rules, calibration and hardware remain untested.")


if __name__ == "__main__":
    main()
