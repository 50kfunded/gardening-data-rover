# Reading the data

This is the start of the Python data pipeline. It reads the simulation's saved
files and gives a small summary. It has only been tested on simulated data.
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

This runs tests using the committed SIMULATED sample and invented noise, drift
and faults. See [the soil calibration plan](../docs/soil_calibration.md) for
the home procedure, limits and blank results template.
