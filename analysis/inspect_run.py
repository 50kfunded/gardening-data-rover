# SPDX-License-Identifier: MIT
"""SIMULATION ONLY: show what is in a saved fake run, without interpreting soil health."""

import argparse
from pathlib import Path

from analysis.read_run import read_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_folder", type=Path)
    arguments = parser.parse_args()
    try:
        metadata, rows = read_run(arguments.run_folder)
        if not rows:
            raise ValueError("the CSV has no samples")
    except (OSError, ValueError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print("SIMULATED DATA ONLY: these are invented values, not garden observations.")
    print(f"Run: {metadata['run_id']}; samples: {len(rows)}")
    print(f"Virtual sample times: {rows[0]['t_ms']}..{rows[-1]['t_ms']} ms")
    print(f"Final raw encoder counts: left={rows[-1]['enc_left']}, right={rows[-1]['enc_right']}")
    soil = [row["soil_raw"] for row in rows if row["soil_raw"] is not None]
    if soil:
        print(f"Invented soil ADC range: {min(soil)}..{max(soil)} counts, not moisture percent")


if __name__ == "__main__":
    main()
