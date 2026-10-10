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
