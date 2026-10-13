# Changes

## 2026-10-13: Simulated weekly analysis preparation

- Added several fictional garden weeks with hourly 10 Hz bursts, daily soil cycles, rain-like events, slow sensor drift, stuck/noisy signals, spikes, dropouts, missing visits and a split controller reboot.
- Kept all run columns, T/D/STOP and telemetry/metadata versions unchanged. Put invented observation dates and the visit schedule in a separate SIMULATED scenario artifact.
- Added daily soil/temperature/humidity summaries, drying slopes, prior-day rolling baselines, EWMA and a CUSUM-style shift rule, reusing the existing soil calibration.
- Added explainable alerts with evidence scores, limitations and "not enough data" handling. A flat signal is only possibly stuck until a controlled challenge confirms it.
- Added plain weekly templates and a documented photo-analysis TODO. No photo-analysis result or plant diagnosis is generated.
- Added computer tests for the invented weeks and faults. Rules, thresholds and hardware remain planned and untested; no hardware milestone has passed.
- Logger checks (18 tests), the unchanged S0 simulation checks and analysis checks (52 tests, including 32 new weekly tests) passed on the computer only, without `-I`.

## 2026-10-13: Pull-down proposal and cancelled order note

- Changed the seven proposed TB6612 input pull-downs to 4.7 kΩ, ±5% or better, across the parts, wiring and related docs.
- Re-read RP2350 E9: 4.935 kΩ at +5% is about 40% below its 8.2 kΩ external pull-down limit. The value stays planned and untested until measured; kept A2/A4 and boot/reset checks with VM disconnected.
- Corrected the Anglia entry to say the Nucleo order was cancelled and the planned controller changed to the base BB48, not yet bought.
- Logger checks (18 tests), simulation checks (300 invented rows) and native protocol tests (8 tests) passed on the computer only, with no hardware connected.
- Kept the data contract and T/D/STOP unchanged. No hardware milestone has passed.

## 2026-10-13: BB48 controller preparation

- Selected base Olimex RP2350-PICO2-BB48 at £14.50, not yet bought. The Anglia Nucleo order was cancelled and the ESP32 idea dropped; Radxa stays the computer.
- Switched PlatformIO/Arduino-Pico and built the USB-only, once-a-second counter for `olimex_pico2bb48`.
- Kept the native environment and pure protocol library unchanged. Updated USB/UART instructions and the sourced GPIO/diagram plan, including later reservations.
- Planned seven driver pull-downs (now revised to 4.7 kΩ, ±5% or better, untested until measured), a 100 nF soil-input capacitor and an inline USB power meter. Added A2/A4, ADC motors-off/on, STBY reset and Radxa UART checks.
- Replaced the old controller power procedure with BB48 USB/VSYS checks; kept Radxa's 500 mA host budget and optional hub measurements.
- Updated related docs and recorded the choice/alternatives. Contract board wording changed only; columns, T/D/STOP, empty readings, 256-byte limit and metadata schema did not change.
- Native, logger and simulation checks passed on the computer with simulated inputs. Hardware steps 0–8 remain pending; no upload or real measurement was made.

Older entries below describe earlier plans/results, not the currently selected controller.

## 2026-10-12: Soil calibration preparation

- Added pure Python two-point calibration, filtering, fault warnings and a quality score.
- Kept the percentage labelled as a relative wetness index, not measured soil water content.
- Added tests using SIMULATED DATA with invented noise, drift and faults.
- Added a sourced home calibration plan and a blank results template.
- Kept raw telemetry, the T/D/STOP protocol and metadata schema unchanged.
- Calibration and thresholds are planned and untested on hardware. No hardware milestone has passed.

## 2026-10-11: USB host power proposal

- Added my proposed Radxa-host power fix for the Nucleo, with a hub for the C920.
- Recorded the published host budget, USB configuration limits, source links and open questions.
- Added an optional hub to the parts plan and later bench checks for current, enumeration and bank stay-on.
- Kept the wiring diagram, pin table, protocol and metadata schema unchanged.
- Everything in this proposal is planned and untested. No hardware milestone has passed.

## 2026-10-11: Controller metadata and power research

- Renamed boot-time metadata to controller names and bumped metadata schema version to 2.
- Updated the simulation, serial logger and committed SIMULATED example.
- Kept the 11 telemetry columns, T/D/STOP messages and CSV format version unchanged.
- Added checks for the new time fields, split-run anchors and rejection of older metadata.
- Added a sourced power plan for the Nucleo and Radxa, marked planned and untested.
- The power research does not change the wiring plan or pass a hardware milestone.

## 2026-10-11: Nucleo controller plan

- Changed the planned real-time controller to NUCLEO-G474RE; Radxa ZERO 3W stays the logic board.
- The Anglia NUCLEO-G474RE order was later cancelled; the planned controller changed to the base Olimex RP2350-PICO2-BB48, not yet bought and untested.
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
