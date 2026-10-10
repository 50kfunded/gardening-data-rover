# changes

## 2026-10-10 — project links

- updated the repository links to `gardening-data-rover`.
- linked the prototype 1 board directly and recorded that the source is public.
- only the laptop simulation exists; all hardware pass tests remain pending.

## 2026-10-10 — laptop simulation snapshot

- organised the fake ESP32, generator and verifier in `simulation/`.
- kept the telemetry contract in `shared/` for simulation and future Pi imports.
- added a file-reading pipeline in `analysis/`.
- added a clearly labelled simulated sample and `python -m simulation.check`.
- labelled generated CSV files and kept missing readings separate from zero.
- refused any existing output folder, including an incomplete run.
- added unstarted firmware/Pi folders and proposed hardware notes.
- documented the nine pending milestones, proposed trial method and release tags.
- expanded ignores for credentials, photos, datasets and environments.
- chose MIT for code and CC BY 4.0 for original docs, plans and the simulated sample.

only the laptop simulation exists. no hardware was built, no real measurements
were collected and no AI model was trained. the check passes with 300 simulated
rows, 11 columns and 100 ms virtual intervals. hardware steps 0–8 are pending.
