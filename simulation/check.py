# SPDX-License-Identifier: MIT
"""One-command check of SIMULATED files, imports and rejection of damaged data."""

import json
import tempfile
from pathlib import Path

from shared.data_format import OPTIONAL_FIELDS, parse_telemetry
from simulation.simulate_run import PROJECT_DIR, write_run
from simulation.verify_run import verify


def expect_failure(action, description):
    """A damaged run must fail, rather than quietly looking successful."""
    try:
        action()
    except (OSError, ValueError, KeyError, TypeError, OverflowError):
        return
    raise RuntimeError(f"FAIL: accepted {description}")


def main():
    # TemporaryDirectory cleans up only the temporary test folder it creates.
    with tempfile.TemporaryDirectory(prefix="rover-simulation-check-") as temporary:
        run_dir = write_run(Path(temporary), "check_sim")
        verify(run_dir)

        csv_path = run_dir / "telemetry.csv"
        original_csv = csv_path.read_text(encoding="utf-8")
        lines = original_csv.splitlines(keepends=True)
        bad_number = lines.copy()
        cells = bad_number[2].rstrip("\n").split(",")
        cells[9] = "NaN"
        bad_number[2] = ",".join(cells) + "\n"
        corruptions = {
            "an unlabelled new simulation": "".join(lines[1:]),
            "a missing sample": "".join(lines[:-1]),
            "a non-finite reading": "".join(bad_number),
        }
        for description, broken_csv in corruptions.items():
            csv_path.write_text(broken_csv, encoding="utf-8")
            expect_failure(lambda: verify(run_dir), description)
        csv_path.write_text(original_csv, encoding="utf-8")

        meta_path = run_dir / "meta.json"
        original_meta = meta_path.read_text(encoding="utf-8")
        meta_path.write_text("[]\n", encoding="utf-8")
        expect_failure(lambda: verify(run_dir), "metadata that is not an object")
        metadata = json.loads(original_meta)
        metadata["data_source"] = "hardware"
        meta_path.write_text(json.dumps(metadata), encoding="utf-8")
        expect_failure(lambda: verify(run_dir), "a run falsely marked as hardware")
        meta_path.write_text(original_meta, encoding="utf-8")

        missing = parse_telemetry("T,100,0,0,0,0,,,,,,")
        if any(missing[field] is not None for field in OPTIONAL_FIELDS):
            raise RuntimeError("FAIL: missing sensor readings were turned into values")
        expect_failure(lambda: write_run(Path(temporary), "check_sim"), "overwriting a run")
        incomplete_run = Path(temporary) / "incomplete_sim"
        incomplete_run.mkdir()
        expect_failure(lambda: write_run(Path(temporary), "incomplete_sim"),
                       "overwriting an existing folder without photos/")

    print("PASS: damaged files and false hardware labels are rejected; missing readings stay missing.")
    print("Checking the committed SIMULATED example:")
    verify(PROJECT_DIR / "data" / "sample" / "example_sim")
    print("PASS: laptop simulation checks only. No hardware milestone has passed.")


if __name__ == "__main__":
    main()
