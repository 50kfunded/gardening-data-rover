# SPDX-License-Identifier: MIT
"""Computer checks of SIMULATED serial input. These cannot pass a hardware milestone."""

import unittest
from pathlib import Path


def main():
    print("SIMULATED DATA ONLY: loopback and fake-port checks, no hardware.", flush=True)
    root = Path(__file__).resolve().parents[1]
    tests = unittest.defaultTestLoader.discover(str(root / "pi" / "tests"),
                                              top_level_dir=str(root))
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("PASS: simulated logger and command checks. No hardware milestone has passed.")


if __name__ == "__main__":
    main()
