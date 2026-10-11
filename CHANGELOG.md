# Changes

## 2026-10-11: Nucleo controller plan

- Changed the planned real-time controller to NUCLEO-G474RE; Radxa ZERO 3W stays the logic board.
- Recorded the Anglia order at £11.98 ex VAT, with the invoice total unconfirmed and hardware untested.
- Built the counter for Arduino and ST-LINK, checking the core's virtual COM port mapping.
- Added a proposed pin plan, separate USB power checks and mixed jumper types.
- Kept single-pulse encoder interrupts first; timer counting and magnetic quadrature are a later milestone.
- Updated PC testing and the milestone issues for the Nucleo and Radxa.
- The simulation, logger and eight native protocol tests pass on the computer. No hardware milestone has passed.
- Kept the protocol, CSV columns and legacy metadata names unchanged.

## 2026-10-11: Software preparation

- Added planned milestone 1 counter firmware and pure protocol helpers with native tests.
- Added the serial logger, configurable port, reset splitting and D/STOP sender.
- Tested serial input with simulated loopback and fake chunks, keeping missing cells empty.
- Added setup and Windows virtual COM port notes, plus protocol proposals awaiting approval.
- Kept the T line contract unchanged. No hardware milestone has passed.

## 2026-10-11: Radxa wiring plan

- Updated the planned power and UART connections for Radxa ZERO 3W, including the diagram.
- Added UART3-M0 and the UART4-M1/UART5-M1 fallbacks, with the serial device still unconfirmed.
- Added milestone 0 checks before wiring and kept the controller on its own USB lead.
- Updated the logic board code notes and related docs; the folder still stays `pi/`.
- The computer simulation check passes. All wiring and hardware work remain planned and untested.

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

- Organised the simulated controller, generator and verifier in `simulation/`.
- Kept the telemetry contract in `shared/` for simulation and future logic board imports.
- Added a file-reading pipeline in `analysis/`.
- Added a clearly labelled simulated sample and `python -m simulation.check`.
- Labelled generated CSV files and kept missing readings separate from zero.
- Refused any existing output folder, including an incomplete run.
- Added unstarted firmware and logic board folders and proposed hardware notes.
- Documented the nine pending milestones, proposed trial method and release tags.
- Expanded ignores for credentials, photos, datasets and environments.
- Chose MIT for code and CC BY 4.0 for original docs, plans and the simulated sample.

Only the computer simulation exists. No hardware was built, no real measurements
were collected and no AI model was trained. The check passes with 300 simulated
rows, 11 columns and 100 ms virtual intervals. Hardware steps 0–8 are pending.
