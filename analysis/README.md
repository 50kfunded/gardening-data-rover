# Reading the data

This Python data pipeline reads the simulation's saved files, checks soil
batches and makes daily/weekly summaries. It has only been tested on SIMULATED data.
There is no model training, plant diagnosis or tested hardware calibration yet.

From the repository root:

```powershell
python -m analysis.inspect_run data/sample/example_sim
```

`read_run.py` checks the metadata, source label, column order and numeric values.
`simulation/verify_run.py` adds the stricter 30-second simulation pass test.
Neither proves that a real rover works or that a soil reading means dry or wet.

The planned soil helper maps a settled batch to a relative 0–100 wetness index,
with flags for suspicious readings and a batch-quality score. It keeps raw
telemetry unchanged and does not claim gravimetric or volumetric water content.
The endpoints and thresholds still need checking on hardware.

```powershell
python -m analysis.check
```

This runs the soil tests and weekly engine tests using the committed SIMULATED
sample and invented garden weeks, noise, drift, missing readings and resets.
See [the soil calibration plan](../docs/soil_calibration.md) for the home
procedure, limits and blank results template.

## Planned weekly analysis

```powershell
python3 -m simulation.garden --output-dir runs/garden_sim --weeks 6
python3 -m analysis.weekly_report runs/garden_sim --dry-raw 3000 --wet-raw 1000 --output-dir artifacts/weekly_sim
```

Those calibration values and garden dates are invented. Use new output
directories; earlier results aren't overwritten. No heavy analysis packages
are needed. The report uses rolling baselines, EWMA and a CUSUM-style shift
rule, with plain templates, quality scores and "not enough data" notes.
It doesn't read injected-fault labels to decide alerts.

The [analysis plan](../docs/analysis_engine.md) explains the maths, proposed
thresholds, fictional clock sidecar and limitations. Real runs, multiple soil
locations, watering decisions and photo analysis remain unimplemented or
unvalidated. No hardware milestone has passed.
