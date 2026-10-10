# SPDX-License-Identifier: MIT
"""Read the shared file format. Currently tested only with SIMULATED data."""

import csv
import json
from pathlib import Path

from shared.data_format import COLUMNS, SCHEMA_VERSION, SIMULATION_NOTICE, parse_telemetry


def read_run(run_dir):
    """Return metadata and numeric rows; preserve missing readings as None."""
    run_dir = Path(run_dir)
    metadata = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("meta.json must contain a JSON object")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("wrong schema version")
    if metadata.get("run_id") != run_dir.name:
        raise ValueError("run_id does not match the folder")
    # Real hardware support will need its own tests before it is accepted here.
    if metadata.get("data_source") != "simulation":
        raise ValueError("only simulated runs are supported at this stage")
    csv_version = metadata.get("csv_format_version", 1)
    if csv_version not in (1, 2):
        raise ValueError("unsupported CSV format version")

    rows = []
    with (run_dir / "telemetry.csv").open(newline="", encoding="utf-8") as source:
        if csv_version == 2:
            if source.readline().rstrip("\r\n") != SIMULATION_NOTICE:
                raise ValueError("the SIMULATED DATA notice is missing or changed")
        reader = csv.reader(source)
        if next(reader, None) != list(COLUMNS):
            raise ValueError("CSV header or column order is wrong")
        for sample_number, cells in enumerate(reader, start=1):
            if len(cells) != len(COLUMNS) or any("," in cell for cell in cells):
                raise ValueError(f"sample {sample_number}: expected 11 numeric CSV cells")
            try:
                rows.append(parse_telemetry("T," + ",".join(cells)))
            except ValueError as error:
                raise ValueError(f"sample {sample_number}: {error}") from error
    return metadata, rows
