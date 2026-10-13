# Project context

## What exists

The original computer simulation generates 300 invented snapshots
over 30 virtual seconds at 10 Hz, writes CSV and JSON, and verifies them.
The readings are SIMULATED DATA, not hardware or garden observations.

S0, the software preparation step, passed on 9 October 2026. The reorganised
check passes too. Board setup (0) and hardware steps 1–8 are all pending.
Milestone 1 USB counter firmware is prepared and builds, but is not uploaded
or tested on a board. Pure protocol functions pass native computer tests.
The serial logger and command sender pass simulated loopback/fake-input tests.
Real UART operation is untested. Camera processing, PID and Kalman filtering are
not started. No hardware milestone has passed.
The weekly engine now has a six-week SIMULATED fixture with daily cycles,
rain-like events, slow drift, noise/stuck/spike/dropout faults and a split
controller reboot. It keeps the telemetry/metadata versions unchanged.
Fictional observation dates live in a separate `scenario.json`; generation
dates keep their existing meaning. Analysis uses one location/calibration,
rolling baselines, EWMA and CUSUM-style checks with confidence/insufficient-data
notes and weekly templates. It never uses injected-event labels as evidence.
All thresholds remain planned and untested on hardware; photo analysis is a
documented TODO only. See [the analysis plan](docs/analysis_engine.md).
The optional watering advisor reads a separate SIMULATED water/forecast
sidecar. A mm bucket, earlier per-bed index limits and quality checks produce
provisional suggestions or a finger-check fallback. It makes no live weather
request or watering command. Bed capacity, plant thresholds, temperature
compensation and useful advice remain unvalidated. [Watering plan](docs/watering_advisor.md)
Soil calibration helpers pass SIMULATED tests for a relative wetness index,
filtering and fault warnings. The references, limits and insertion procedure
remain planned and untested on hardware. See [the soil plan](docs/soil_calibration.md).

The Radxa ZERO 3W is bought for £44 including shipping, but untested. The
planned controller is the **base Olimex RP2350-PICO2-BB48, £14.50, not yet
bought**. NUCLEO-G474RE and the ESP32 order ideas are dropped. The C920 is
already owned. No rover is assembled. See [parts](hardware/parts.md) and
[controller choice](docs/controller_choice.md).

## Folder roles

- `shared/data_format.py`: the 11-column schema and line parser.
- `simulation/`: invented controller lines, file generation and pass/fail checks.
- `analysis/`: reads simulated files, calibrates soil batches and produces daily/weekly rules and template summaries.
- `firmware/`: planned milestone 1 counter and pure protocol functions; hardware untested.
- `pi/`: serial logger and commands; tested only with simulated input.
- `hardware/`: proposed parts, wiring and mounting, all untested.
- `data/sample/`: small labelled simulation; no real private data.
- `docs/`: planned milestones, data contract, trial method and future ideas.

From the repository root, run `python -m simulation.check`. Python 3.12 was
used for verification; the original simulation needs no third-party packages.
The new `python -m pi.check` needs pyserial. See [software preparation](docs/software_prep.md)
for the virtual environment, native GCC and PlatformIO commands. `pi.demo`
uses loopback and labels its files SIMULATED DATA.

The wire protocol and 11 telemetry columns are unchanged. Metadata schema
version 2 uses `controller_*` boot-time names. Older metadata version 1 is
not migrated automatically. Extra counters, checksums
and boot identification remain [proposals](docs/protocol_proposals.md), not code.

## Planned architecture

Base BB48 handles motor signals, single-pulse encoders and sensors in a later
100 Hz control loop. Radxa handles commands, recording and the C920. Counter
firmware only prints once a second on native USB `Serial`; no control loop,
ADC, motor command or timeout is implemented by that milestone.

UART0 `Serial1` GPIO0 TX / GPIO1 RX is reserved for Radxa UART3-M0 physical
3 RX / 5 TX / 6 GND, 3.3 V, 115200 8N1. Enable Radxa's overlay through
`rsetup`; `/dev/ttyS3` is expected but unconfirmed. I2C1 `Wire1` uses GPIO2/3,
driver GPIO6–12, encoders 14/15 and ADC0/1 GPIO40/41. Leave QWST empty because
its default I2C pins share GPIO12 STBY. Later pins are only reservations.

Wheel commands stay rad/s, raw encoder counts cumulative, soil 12-bit raw
0–4095, missing readings empty and unknown calibration null. No new light
column, counter, checksum or schema version is added. Keep
`firmware/lib/rover_protocol/` unchanged. [Contract](docs/data_contract.md)

BB48 uses its own USB-C lead, computer USB first and separate bank output
later. Never combine external VSYS with USB. Keep Radxa header 2/4 disconnected
until measured/reviewed. C920 uses USB-C 2; keep the published 500 mA budget
and measure any optional hub arrangement. There is no host-handshake power
fix required for BB48's documented path, but actual startup/stay-on are untested.

Record A2/A4 silicon and ADC repeatability with motors off/on. Seven planned
4.7 kΩ pull-downs (±5% or better) at TB6612 STBY/PWM/direction inputs need a
boot/reset/BOOT test with VM disconnected. At +5%, 4.935 kΩ is about 40%
below E9's 8.2 kΩ limit, but the value is a proposal until measured. Revise
the circuit before motor power if logic low isn't assured. Add a planned
100 nF soil-input capacitor and an inline USB meter to the parts plan.
Later firmware needs local timeout/rearm and a separate physical motor e-stop.

[Wiring](hardware/wiring.md), [bring-up](docs/plan.md), [power](docs/power_plan.md)
and [software setup](docs/software_prep.md) are planned and untested. Hardware
steps 0–8 remain pending regardless of computer build/test results.

## Boundaries for the first build

Start with indoor tests. Garden movement has not been proved. Soil insertion
is manual, so unattended movement does not imply automatic soil sampling.
Train any later image model on a computer using reviewed real observations;
invented simulation values are only useful for exercising the pipeline.

Teach one milestone at a time, with exact code for the verified parts, wiring
and a pass/fail test. Explain the maths and ask for results before continuing
to the next build milestone. Future roadmaps are estimates, not instructions
to skip those tests.

## Sharing

Use the [publication checklist](docs/publication.md) before sharing a snapshot.
Keep source-only commits, a GitHub noreply identity and labelled invented examples.
Do not add credentials, identifiable records or raw photographs to Git.
Normal runs, environments and local screenshots stay ignored.
