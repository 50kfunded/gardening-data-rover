# Changes

## 2026-10-10: Radxa parts plan

- Changed the logic board plan to Radxa ZERO 3W and updated the cables and bench items.
- Recorded the board as bought for £44 including shipping, with testing still pending.
- Kept the remaining prices as estimates and added the mounting and heatsink questions.
- Only the computer simulation runs. No rover has been built, and hardware steps 0–8 are pending.

## 2026-10-10: Project links

- Updated the repository links to `gardening-data-rover`.
- Linked the Prototype 1 board directly and recorded that the source is public.
- Only the computer simulation exists; all hardware pass tests remain pending.

## 2026-10-10: Computer simulation snapshot

- Organised the fake ESP32, generator and verifier in `simulation/`.
- Kept the telemetry contract in `shared/` for simulation and future Pi imports.
- Added a file-reading pipeline in `analysis/`.
- Added a clearly labelled simulated sample and `python -m simulation.check`.
- Labelled generated CSV files and kept missing readings separate from zero.
- Refused any existing output folder, including an incomplete run.
- Added unstarted firmware/Pi folders and proposed hardware notes.
- Documented the nine pending milestones, proposed trial method and release tags.
- Expanded ignores for credentials, photos, datasets and environments.
- Chose MIT for code and CC BY 4.0 for original docs, plans and the simulated sample.

Only the computer simulation exists. No hardware was built, no real measurements
were collected and no AI model was trained. The check passes with 300 simulated
rows, 11 columns and 100 ms virtual intervals. Hardware steps 0–8 are pending.
