# reading the data

this is the start of the Python data pipeline. it reads the simulation's saved
files and gives a small summary. it has only been tested on simulated data.
there is no model training, plant diagnosis or real sensor analysis yet.

from the repository root:

```powershell
python -m analysis.inspect_run data/sample/example_sim
```

`read_run.py` checks the metadata, source label, column order and numeric values.
`simulation/verify_run.py` adds the stricter 30-second simulation pass test.
neither proves that a real rover works or that a soil reading means dry or wet.
