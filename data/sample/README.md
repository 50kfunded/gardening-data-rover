# simulated example data

**SIMULATED DATA ONLY.** `example_sim/` contains 300 invented rows covering
30 virtual seconds. nothing here was recorded from a rover or a real garden.
there are no names, addresses, coordinates, plants, faces or photographs.
the values are invented from scratch, rather than real data with names removed.

`date` and `started_unix_s` are the file-generation time. they are not the time
of a garden visit. `photos/.gitkeep` is only a text placeholder so Git keeps
the folder; there are no simulated or real photographs.

from the repository root:

```powershell
python -m simulation.verify_run data/sample/example_sim
python -m analysis.inspect_run data/sample/example_sim
python -m simulation.check
```

the CSV's first line labels it as simulated. the next line is the 11-column
header; the remaining 300 lines are samples. metadata repeats the simulation
label and leaves hardware calibration and PID gains as `null`.

to generate another example privately, choose a new output folder:

```powershell
python -m simulation.simulate_run --output-root runs --run-id another_example_sim
```

the generator refuses to overwrite an existing run. only this small reviewed
example belongs in Git; normal output stays in ignored `runs/`.

the invented example is [CC BY 4.0 licensed](../../LICENSE-DOCS). this grant
does not cover real private garden observations or photographs.
