# Computer simulation

All readings here are simulated. The generator invents messages immediately;
30 simulated seconds do not take 30 seconds on the computer. This is a file and
parser exercise, with no physics model, hardware, PID or live UART connection.

Run modules from the repository root so Python can find `shared/` and `analysis/`:

```powershell
python -m simulation.simulate_run
python -m simulation.verify_run runs/<folder_printed_by_the_first_command>
```

Or run the whole check, including a fresh temporary run and the committed example:

```powershell
python -m simulation.check
```

Replace the placeholder with the actual folder name. The first command also
prints the exact verification command, so it can be copied directly.

New CSV files start with a `# SIMULATED DATA: ...` notice, then the 11-column header.
Metadata has `data_source: simulation` and `csv_format_version: 2`. Older local
S0 runs without that notice still work when their simulation metadata is present;
the checker prints a legacy warning. Keep those files together.

## Several invented garden weeks

```powershell
python3 -m simulation.garden --output-dir runs/garden_sim --weeks 6 --seed 42
python3 -m analysis.weekly_report runs/garden_sim --dry-raw 3000 --wet-raw 1000
python3 -m analysis.check
```

This separate fixture makes hourly visits with nine 10 Hz samples each,
daily soil cycles, rain-like wetting, slow ADC drift, spikes, a stuck/noisy
signal, dropouts, missing visits and a controller reboot. It generates
immediately. All readings, references, dates and faults are SIMULATED.

It keeps the existing telemetry and metadata versions. `scenario.json` is a
separate, labelled artifact for the fictional observation dates and visit
schedule; metadata dates still describe generation. Reset run parts stay
separate. The original 30-second S0 check stays unchanged.

The new output directory must not already exist. The `3000`/`1000` calibration
endpoints are fake fixture values, not settings for the planned hardware.
See [the analysis plan](../docs/analysis_engine.md) for events, maths and open
checks. A passing simulation doesn't pass a hardware milestone.

New fixtures also include invented irrigation events and a separate
`watering_inputs.json` with SIMULATED rain/irrigation amounts, a fictional bed
profile and a next-day forecast stub (including a false forecast). Use the
weekly command's `--watering-inputs` option to exercise the planned advisor.
The weather inputs are separate from injected-fault truth and run metadata;
no live API is called. See [watering assumptions](../docs/watering_advisor.md).
