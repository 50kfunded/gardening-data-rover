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
Real UART operation is untested. Camera code, PID, Kalman filtering and AI are
not started. No hardware milestone has passed.

The Radxa ZERO 3W has been bought for £44 including shipping. It has not been
tested, and no rover has been built. The NUCLEO-G474RE was ordered on
11 October 2026 from Anglia at a listed £11.98 ex VAT. The VAT-inclusive
invoice total is unconfirmed; it has not arrived or been tested. The other
parts are still planned, apart from the already-owned C920. See [the parts list](hardware/parts.md) and
[logic board plan](docs/logic_board.md).

## Folder roles

- `shared/data_format.py`: the 11-column schema and line parser.
- `simulation/`: invented controller lines, file generation and pass/fail checks.
- `analysis/`: reads and summarises the simulated files, with no AI inference.
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

NUCLEO-G474RE is planned to handle motors, encoder interrupts and sensors with
a 100 Hz control loop. Radxa ZERO 3W is planned for UART logging, drive commands and a USB
C920 camera. UART is proposed at 115200 baud with text lines. Telemetry begins at
10 Hz, separately from the control update rate.

Wheel command units are rad/s. Encoder values are raw cumulative counts,
not signed positions. Soil values are raw ADC counts, not moisture percent.
Unavailable sensor fields stay blank and unknown calibration stays `null`.
See [the contract](docs/data_contract.md) before changing a field or unit.

Motor power is a separate AA pack; the logic/camera power bank shares ground.
The camera is planned for the Radxa's USB-C 2 through a data-capable adapter.
The Nucleo is planned on its own USB lead, with no supply from Radxa header
pins 2/4. The [wiring document](hardware/wiring.md) uses UART3-M0 on physical
pins 3 RX, 5 TX and 6 GND, crossed to USART1 D1 / PC4 TX and D0 / PC5 RX
at 3.3 V. The PC counter uses the separate ST-LINK VCP, LPUART1 PA2/PA3.
Enable the Radxa overlay in
`rsetup`; `/dev/ttyS3` is expected but unconfirmed. The wiring is planned and
untested. Do the [milestone 0 checks](docs/plan.md#milestone-0-checks-before-wiring)
before connecting the UART.

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
