# laptop simulation

all readings here are simulated. the generator invents messages immediately;
30 simulated seconds do not take 30 seconds on the laptop. this is a file and
parser exercise, with no physics model, hardware, PID or live UART connection.

run modules from the repository root so Python can find `shared/` and `analysis/`:

```powershell
python -m simulation.simulate_run
python -m simulation.verify_run runs/<folder_printed_by_the_first_command>
```

or run the whole check, including a fresh temporary run and the committed example:

```powershell
python -m simulation.check
```

replace the placeholder with the actual folder name. the first command also
prints the exact verification command, so it can be copied directly.

new CSV files start with a `# SIMULATED DATA: ...` notice, then the 11-column header.
metadata has `data_source: simulation` and `csv_format_version: 2`. older local
S0 runs without that notice still work when their simulation metadata is present;
the checker prints a legacy warning. keep those files together.
